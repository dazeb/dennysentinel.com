---
title: "What It Takes to Validate Security Challenges: RedTeamLab's Test Infrastructure"
description: "Building a challenge validation pipeline for a red team training platform — where tests mean spinning up Docker containers with actual vulnerabilities, and every layer adds a new way to break."
pubDate: "Jul 03 2026"
heroImage: "/challenge-validator-test-infrastructure.jpg"
---

When your product is "people exploit vulnerable Docker containers to learn offensive security," testing that your challenges actually work is not optional. It is also not simple.

RedTeamLab runs five challenge categories — Local File Inclusion, WebDAV, Password Spraying, Misconfigured Nginx, and SSH Private Key exposure. Each is a Docker Compose stack with a known vulnerability embedded. If the stack fails to build, or the vulnerability is patched by a dependency update, or the scoring script returns a false positive, the training breaks silently.

I spent the last session turning a manual validation script into a proper CLI tool with CI automation. The specifics are worth writing down because they illustrate a broader truth: infrastructure for testing security training is itself a security problem.

## The Starting Point: A Script That Worked Locally

The original validator lived in `API/scripts/validate_challenges.py`. It worked — you could run it from the repo root and it would spin up each challenge's Docker stack, run the exploit, and return a pass/fail verdict. The problem was discoverability. You had to know the exact invocation path, the right Python environment, and which Docker compose commands were valid. New contributors (and future me) would not find it by browsing the repo.

```bash
# The old way — works only if you know where to look
python3 API/scripts/validate_challenges.py --challenge easy-lfi
```

The fix was to wire it into the existing CLI surface. The project already had an `arena` CLI from an earlier phase. Adding two commands — `arena challenges test` and `arena challenges verify` — meant the validator became self-discovering:

```bash
# The new way — discoverable via --help
arena challenges test          # quick smoke test (up, run, down)
arena challenges verify        # full validation with scoring check
```

The implementation was straightforward: the CLI commands call the validator script via subprocess with a `_find_project_root()` helper that walks up from the CLI file's location. Duplicate logic would be a maintenance trap, so the CLI is purely a wrapper — all validation logic stays in the script.

## The `--build` Flag: Threading Through Three Layers

The most instructive fix was the `--build` flag. When you iterate on a challenge definition — editing the Dockerfile, adding a new exploit path, fixing environment variables — you need the validator to rebuild the image before running. Without `--build`, you get the cached image, which still has the old vulnerability posture.

Adding the flag required touching three layers:

1. **Validator CLI** (`validate_challenges.py`): Added `--build` to `argparse`, threaded through `parse_args` to `validate_one`
2. **Docker runner** (`docker_runner.py`): Added `build: bool = False` to `spawn_stack()` — appends `--build` to `docker compose up -d` when set
3. **CLI wrapper** (`arena/cli.py`): Wired the flag through `_run_validator()` so `arena challenges verify --build` works end-to-end

```python
# docker_runner.py — the --build flag threading
def spawn_stack(self, challenge_dir: Path, build: bool = False) -> bool:
    cmd = ["docker", "compose", "up", "-d"]
    if build:
        cmd.append("--build")
    result = subprocess.run(cmd, cwd=challenge_dir, capture_output=True, text=True)
    return result.returncode == 0
```

Three files, one feature, fifteen lines of diff. But each file lives in a different directory with its own test fixtures and dependency chain. The threading discipline — pass the flag as a named parameter at every level, never rely on environment variables or global state — is what makes the feature maintainable when challenge five breaks and you need `--build` to work.

## CI Concurrency: When Two Validations Fight Over Docker

The CI workflow was the next thing to break. The project runs challenge validation on every pull request. The first time two PRs arrived simultaneously, both pipeline runs tried to spin up Docker stacks at the same time. Docker compose on a single runner does not parallelize gracefully — containers collide on port mappings, network namespaces get confused, and the validation produces false negatives.

The fix was a concurrency guard:

```yaml
concurrency:
  group: challenge-validation-${{ github.ref }}
  cancel-in-progress: true
```

This serializes challenge validation jobs per PR branch. If you push a new commit while validation is running, the old run is cancelled and replaced. It is a one-line change with outsized reliability impact. Two simultaneous validator runs, both racing on `docker compose up`, produce chaos. Serializing them makes the results reproducible.

## SSH-Based Challenges Need sshpass

Challenge #4 (SSH Private Key) requires SSH into a container. The validation script does this:

```bash
ssh -i /tmp/test_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    root@localhost -p 2222 "cat /root/flag.txt"
```

That works on a workstation where SSH is available. In CI, the Ubuntu runner image does not ship `sshpass` — a utility that some exploit paths depend on. The fix was adding it to the CI workflow's install step:

```yaml
- name: Install dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y sshpass
```

That was a ten-minute detour to diagnose. The symptom — the validation script failing only on SSH-based challenges in CI — was specific enough to identify quickly, but it is exactly the kind of environment gap that produces silent failures when the validation suite is not run on the same OS as production.

## The Documentation That Makes It Usable

The final task was documenting the validation workflow in every challenge's README. Each of the five challenge directories now has a `## Verification workflow (canonical)` section:

```markdown
## Verification workflow (canonical)

```bash
# From repo root
arena challenges verify <challenge-slug>
```

This is not padding. When a new challenge author adds a sixth challenge, they should be able to run the validator against it without asking anyone how. Documentation that makes an operation self-discovering is infrastructure, not overhead.

The project README and AGENTS.md were also updated with a "Challenge Validation" section and CLI usage examples. The validator's CLI behavior — exit codes, logging format, the difference between `test` and `verify` — is documented alongside the commands so a subagent or future maintainer can use it without reading the script's source.

## The Verification Discipline

After the changes, the validation chain runs clean:

```
$ arena challenges test
✓ easy-lfi  (1.2s)
✓ webdav-rce  (2.1s)
✓ password-spray  (1.8s)
✓ misconfig-nginx  (1.5s)
✓ ssh-private-key  (3.4s)
5/5 challenges passed
```

Every command — `test`, `verify`, `--help`, `--build` — was checked. Ruff passed on all modified files. The CI workflow was tested by pushing to a branch and confirming the action triggered with the new concurrency guard.

## What Generalizes

Building test infrastructure for a security training platform is not fundamentally different from building test infrastructure for any complex system. The same patterns apply:

- **Discoverability matters.** A script that works but cannot be found is a script that will be rewritten by the next person.
- **Flags need to thread through every layer.** A feature that works at `spawn_stack()` but is unreachable from the CLI is a feature that does not exist.
- **CI concurrency is a reliability risk, not a performance concern.** Serializing validator runs prevents false negatives from resource contention.
- **Environment gaps will surface in CI.** The OS your CI runs on is not your workstation. Install everything you need explicitly, or accept intermittent failures on SSH-based tests.
- **Documentation is infrastructure.** If a subagent cannot verify a new challenge from the README alone, the validation pipeline is incomplete.

The boring conclusion is that most of this work is plumbing. But plumbing is what makes the pipeline trustworthy. A red team training platform where the challenges cannot be validated automatically is not a training platform — it is a guessing game.
