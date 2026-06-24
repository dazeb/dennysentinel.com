---
title: "Nine Bugs Before the First Agent — Shipping RedTeamLab"
description: "Building an AI agent red-team testing arena from scratch meant fixing 9 production bugs before a single agent submitted a flag. The debugging log reads like a checklist of what breaks when you let AI agents run Docker containers."
pubDate: "Jun 24 2026"
heroImage: "/nine-bugs-before-the-first-agent.jpg"
---

Last week I renamed the project from `agent-arena` to `redteamlab`, redeployed everything, wired a submission pipeline end-to-end, and discovered nine distinct bugs between the first smoke test and a fully verified pipeline.

The project is simple in concept: an AI agent connects to a challenge container (think HackTheBox for agents), captures a flag, and submits it for scoring. The hard part is everything else — authenticating the agent without leaking keys, spawning clean Docker stacks per submission, surviving the scoring round without state corruption, and making the whole thing work on a single VPS at `178.104.6.193`.

Here's what broke, in order of appearance.

## Bug #1: Rate Limiter on the Wrong Scope

The first smoke test returned `429 Too Many Requests` — on the *second* request.

```json
/api/v1/challenges/easy-lfi:1  Failed to load resource: 429 ()
```

The frontend makes about 5 requests at startup (auth check, challenge list, leaderboard). Each one counts. The rate limiter was wired as Starlette middleware with a scope of `auth:login` — 5 requests per 15 minutes — but it wrapped the *entire application*, not just the login endpoint. After the frontend's initialization barrage, every route was locked out for 15 minutes.

**Fix:** Narrow the rate limiter to only apply to `POST /api/v1/auth/login`. Everything else routes through per-endpoint or unscoped limits.

## Bug #2: Missing `/auth/me` Endpoint

The frontend calls `GET /api/v1/auth/me` after login to verify the session. The endpoint simply didn't exist — a gap between the frontend's expected API surface and what the router defined.

```python
# Frontend expected endpoint — didn't exist
@app.get("/api/v1/auth/me")
async def get_me(user: User = Depends(get_current_user)):
    return UserRead.from_orm(user)
```

**Fix:** Add the endpoint, wire it into the auth router, return the user schema.

## Bug #3: API Key Prefix Extraction Off-by-One

The API keys use a `prefix.secret` format — the first 14 characters are the visible prefix stored in the database for identification, the rest is the full secret.

```python
# Before — missed the last prefix char
prefix = raw_key[:13]  # truncates the 14th character

# After — correct
prefix = raw_key[:14]
```

An off-by-one on key prefixes means every key deforms on ingress. The user sees "key_abc123def456" in their config file, but the database stores "key_abc123def45". Any subsequent lookup by prefix fails silently. This one took longer to catch than it should have because the error was a silent empty set, not a crash.

## Bug #4: Docker-in-Docker File Permissions (The `chmod` Trap)

This one is subtle and cost the most time.

The worker container spawns challenge stacks using Docker-in-Docker. Inside the worker container, a non-root user runs the actual application. The Dockerfile copied `app.py` into the image with root ownership and `644` permissions. Then the `USER` directive switched to `appuser`.

```dockerfile
COPY app.py /app/
USER appuser
```

The problem: the non-root user is the one executing inside the challenge container, and `app.py` is owned by root. `Permission denied`.

The fix is to **run `chmod` before `USER`**:

```dockerfile
COPY app.py /app/
RUN chmod -R a+r /app/
USER appuser
```

This seems obvious in retrospect, but the error message looks like a Python import failure (`can't open file '/app/app.py'`) — which sent me digging through PYTHONPATH and shebang lines for 20 minutes before checking file permissions.

## Bug #5: Fixed Host Ports in Challenge Compose Files

The first challenge compose file used `8080:8080` — mapping container port 8080 to host port 8080. This works for the first submission, but the second one gets `port already allocated`.

The fix is container-port-only:

```yaml
ports:
  - "8080"  # No host binding — Docker auto-assigns
```

The worker reads the actual host port from the Docker API after the container starts. The connection info returned to the agent includes the real port.

## Bug #6: Hardcoded Worker Redis URL

The ARQ worker had `redis://localhost:6379/0` hardcoded. In production, Redis is at a different hostname inside the Docker network. The worker silently connected to nothing and never processed jobs — submissions were stuck in "pending" forever.

```python
# Before
redis = await create_pool("redis://localhost:6379/0")

# After
redis = await create_pool(str(settings.redis_url))
```

The `settings.redis_url` loaded from environment variables via pydantic-settings, properly resolving the Docker service hostname.

## Bug #7: Worker Shutdown Crash (`wait_closed`)

When the worker service restarted during deployment, it crashed with:

```
AttributeError: 'Redis' object has no attribute 'wait_closed'
```

The old Redis client API used `wait_closed()` for graceful shutdown. The installed version uses `aclose()`. The crash didn't prevent the new container from starting, but it left orphaned Redis connections and spammed the logs.

```python
# Before
await redis.wait_closed()

# After
await redis.aclose()
```

## Bug #8: Missing Worker Service in Deploy Compose

The production `docker-compose.deploy.yaml` had the API, Postgres, and Redis services — but not the worker. The worker only existed in the development `compose.yaml`. Deploy builds included database migrations and API containers, but submissions went unprocessed because no worker was running.

**Fix:** Add the worker service block to `docker-compose.deploy.yaml`, mirroring the dev config but using the production image tag.

## Bug #9: Air-Gapped Worker Container Had No Docker CLI

The worker needs to spawn Docker stacks for each submission — Docker-in-Docker. The base image didn't include the Docker CLI. You can't `apt-get install docker.io` in a slim Python image without bloating the build or fighting version incompatibilities.

**Fix:** Install Docker CLI + Compose plugin from GitHub static builds in the Dockerfile:

```dockerfile
RUN curl -fsSL https://github.com/docker/cli/releases/download/v27.0.0/docker-27.0.0.tgz \
    | tar xz -C /usr/local/bin --strip-components=1 docker/docker \
    && curl -fsSL https://github.com/docker/compose/releases/download/v2.29.0/docker-compose-linux-x86_64 \
    -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose
```

Then mount `/var/run/docker.sock` into the worker container. The worker has CLI access to the host Docker daemon without running as root.

## The Verified Pipeline

After all nine fixes, the end-to-end flow:

```
POST /submissions          → 201 — submission created, ARQ job enqueued
Worker spawns Docker stack → Container built + started + healthy
Connection info returned   → 172.17.0.1:8080 (Docker bridge + mapped port)
POST /submissions/{id}/done → Status: "scoring", score job enqueued
Worker runs check.sh       → checker executes
Score breakdown            → {total, modifiers, final_score}
```

The scoring engine correctly computes `final_score=0` when nobody solves the challenge — which is the expected baseline. The CLI is wired up as `arena submit/login/done/status/leaderboard`, connecting to the API at `api.redteamlab.pro`.

## The Lesson

Nine bugs before a working pipeline. None of them were architectural — they were all edge cases in the gap between local dev and production Docker: port conflicts, missing services in compose files, silent Redis dead-ends, off-by-ones in key prefixes, permission hierarchy in multi-stage builds.

The one that stands out is the `chmod` trap (bug #4). Every Dockerfile author has hit this, but it doesn't surface until your otherwise-correct image runs as a non-root user in production. The pattern — `RUN chmod -R a+r /app` before `USER` — is now baked into every Dockerfile in the repo.

RedTeamLab is live at [redteamlab.pro](https://redteamlab.pro/). The first agent hasn't submitted a flag yet, but the pipeline is ready.
