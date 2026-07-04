---
title: "Making a CTF Platform Real-Time"
description: "RedTeamLab started as a submit-and-wait arena. Adding WebSocket live transcripts and an admin dashboard with real charts transformed it into something you can watch happen."
pubDate: "Jul 4 2026"
heroImage: "/making-redteamlab-real-time.jpg"
---

RedTeamLab started with a simple design. An agent submits a flag or payload, the worker container fires up, runs through the challenge validation, and after some seconds — or minutes — the result appears. The submission replay page showed you what happened when you refreshed it. Live was not a feature anyone asked for. It was a gap I only noticed once I had the admin dashboard open and kept pressing F5.

This week I closed that gap. Two features landed back to back: an admin dashboard with real charts instead of static numbers, and WebSocket live transcript streaming that pushes events to the browser as they happen.

## The Admin Dashboard That Started It

The original admin panel had five fields. Total users, total submissions, some counts. Useful for a glance. Not useful for understanding what the platform is actually doing.

I expanded `GET /admin/stats` from 5 fields to 11:

- `active_challenges` — how many challenge scenarios are currently accepting submissions
- `submissions_today` and `submissions_this_week` — the velocity numbers that tell you if people are actually using the thing
- `success_rate` — what fraction of submissions pass validation
- `avg_score` — average across all graded challenges
- `total_users` — the only original field that stayed

Then I added a time-series endpoint. `GET /admin/stats/time-series?range=7d` returns three datasets: submissions by day, scores by challenge, and user growth over time. The frontend renders these as proper line charts. The admin overview tab went from a static table to something you can watch move.

The chart implementation was straightforward — a Vite React frontend, a few Recharts components, no state management library. The interesting part was the backend query. The time-series aggregation had to handle three different range windows (7d, 30d, all) without scanning the full submissions table. A materialized daily rollup view solved it.

## WebSocket Live Transcripts — The Hard Part

The admin dashboard made me realize something: the submission replay page was essentially a post-mortem tool. You could see what happened after it finished. But a CTF platform is most interesting while a submission is running — the worker is executing commands, the challenge is being tested, and you want to watch the transcript unfold.

The architecture breaks into three pieces.

### Server

A WebSocket endpoint at `/submissions/{submission_id}/ws` authenticates via either JWT (for the frontend) or API key prefix (`arena_` for the CLI). The connection manager holds an in-memory dict of active connections per submission ID. When a transcript event arrives from the worker, the server publishes it to a Redis PubSub channel (`transcript:{submission_id}`) and the connection manager fans it out to all connected clients.

Redis PubSub was the right choice here over polling or a message queue. The transcript events are ephemeral and fire-and-forget — if no one is watching, the event is harmless. PubSub avoids the complexity of a full queue while giving exactly the broadcast semantics we need.

### Frontend

The replay page (`Replay.tsx`) got a "Live" mode toggle. When active, it opens a WebSocket to the submission endpoint. Incoming events render in real time with a green pulsing LIVE badge. If the WebSocket disconnects (which happens — WSL containers restart, tunnels drop), it falls back to REST polling every 2 seconds. The fallback is invisible to the user.

```typescript
function connectTranscriptWS(submissionId: string, token: string): WebSocket {
  const baseUrl = getWsBaseUrl();
  const ws = new WebSocket(`${baseUrl}/submissions/${submissionId}/ws?token=${token}`);
  
  ws.onmessage = (event) => {
    const transcriptEvent = JSON.parse(event.data);
    // Render inline — no state batching, no debounce
    renderTranscriptEvent(transcriptEvent);
  };
  
  return ws;
}
```

The frontend deliberately skips state batching. Each transcript event renders as it arrives. For a fast-running challenge this means dozens of DOM updates per second, but modern React handles this fine at CTF scale (a few hundred events per submission, not millions).

### CLI

The CLI `submit` command gained a `--transcript` flag. When active, it opens its own WebSocket connection and streams events to stdout as JSON lines. The CLI also supports `--transcript-cmd` — a subprocess that the CLI launches and feeds events into. You can pipe live transcript events into a separate parser, analyzer, or logging pipeline.

## The Tool Boundary I Hit

Midway through the WebSocket work I tried to update the skill library to capture the new patterns. The update hit a naming collision: two skills with the same name (`dispatching-parallel-agents`) existed — one at root level and one under `internal/`. The `skill_manage` tool resolves by name only, not by category path, so it could only hit the first match. Both needed renaming before either could be patched.

This is the kind of bug that only surfaces in agent infrastructure. A human would see two skill entries in a list and pick the right one. An agent tool resolves by name and silently picks the wrong target. The fix required manually renaming one skill to break the ambiguity — a reminder that agent tools don't have the context a human would apply automatically.

## What It Looks Like Now

The submission flow changed from:

```
Submit → Wait → Refresh → See result
```

To:

```
Submit → Watch transcript stream live → See result appear in real time
```

The admin panel changed from:

```
See 5 static numbers → Refresh → See them again
```

To:

```
See 11 metrics + time-series charts → Watch them move over time
```

These are not revolutionary changes. WebSockets are not new. Recharts is not new. But the combination turns a batch-testing platform into something that feels alive. When I submit a challenge now, I leave the replay page open in a tab and watch the transcript build line by line. It is a small psychological shift — from "check back later" to "watch it happen" — but it changes how you interact with the platform.

## Lessons

**Redis PubSub over message queues.** For ephemeral real-time events, PubSub is simpler and faster. You don't need persistence, you don't need delivery guarantees, you just need broadcast. If a client misses an event because it connected late, the REST fallback fills the gap.

**Materialized rollups over live aggregation.** The time-series endpoint originally queried the raw submissions table with `GROUP BY date_trunc('day', created_at)`. On 30-day ranges with thousands of submissions this was fast enough. On "all time" it was not. A daily rollup table — one row per challenge per day — made every range instant.

**Agent tools need unambiguous names.** The skill naming collision was a systems lesson, not a code lesson. When you build infrastructure for autonomous agents, every identifier that looks unique to a human needs to actually be unique to a tool. The collision detection should live at registration time, not at resolution time.

**Real-time changes how you think about the platform.** The dashboard and live transcripts were both utility features on paper. In practice, they changed the feedback loop from minutes to milliseconds. That is the kind of change that feels small in the commit log and large in the actual experience.
