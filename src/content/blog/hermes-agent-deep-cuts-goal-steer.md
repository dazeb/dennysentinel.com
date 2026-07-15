---
title: "Hermes Agent Deep Cuts: The Four Slash Commands Most Users Never Try"
description: "/goal, /steer, /background, and /queue — four slash commands that transform single-turn chat into a persistent, asynchronous, directed work session. Most users never touch them."
pubDate: "Jul 15 2026"
heroImage: "/hermes-agent-deep-cuts-goal-steer.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's feature: **the four hidden slash commands — `/goal`, `/steer`, `/background`, and `/queue`**.

## What Are These?

Hermes has a rich set of slash commands (over 50 at last count). Most users know `/retry` and `/undo` — the safety net commands that every chat interface has. A few more discover `/model` or `/compress` through the docs.

But there are four that fundamentally change how you interact with an agent. They turn a linear chatbot conversation into a **persistent, asynchronous, directed work session**. Here is what each one does:

| Command | What it does |
|---------|-------------|
| `/goal` | Set a standing objective that Hermes keeps working toward across multiple turns until it is achieved or cleared |
| `/steer` | Inject an instruction that fires *after the next tool call*, without interrupting the current operation |
| `/background` | Run a prompt in the background while you continue the main conversation |
| `/queue` | Enqueue a prompt for the next assistant turn — runs after the current exchange finishes |

## Why They Are Obscure

These commands are not listed in the default `/help` output (which is paginated and prioritizes the most common ones). They also do not have dedicated sections in the introductory documentation — they live in the slash commands reference and the CLI subcommand docs, both of which are deep-linking targets that most users never visit.

There is a structural reason too: these commands solve problems you do not know you have until you have spent significant time working with an agent. A first-time Hermes user does not need `/goal`. A user who has run 200 sessions and keeps re-stating the same objective on every turn? That user needs exactly `/goal`.

## How to Use Them

### `/goal` — Persistent Objectives

```bash
/goal "Build a complete FastAPI authentication service with JWT tokens"
```

Once set, this goal is appended to the system prompt on every subsequent turn. Hermes checks in on progress after each response, adjusts course when something fails, and keeps working across sessions (the goal persists until you `/goal clear`).

```bash
/goal                     # View current goal
/goal status              # Show progress estimate
/goal pause               # Temporarily disable without clearing
/goal resume              # Re-enable
/goal clear               # Remove the goal
```

The key insight: a goal does not just sit there as text. It changes the agent's behavior at a structural level — it adds a "progress checkpoint" step to the implicit reasoning loop, making the agent assess what is done and what is next after every response.

**Practical trick**: Set a goal at the start of every long session. `/goal "Research, implement, and document the Stripe payment integration"` turns a series of disconnected turns into a coherent work session. The agent self-corrects — if a turn derails into an unrelated tangent, the goal pulls it back.

### `/steer` — Non-Interrupting Instructions

This is the most subtle of the four, and the most powerful for agentic workflows.

```bash
/steer "after you finish checking the test output, also run the linter"
```

`/steer` injects a future instruction that fires *immediately after the next tool call completes*. It does not interrupt the current operation — the model finishes whatever tool call is in flight, then processes the steer instruction on the next reasoning step.

This solves a common frustration: you see the agent about to do something, you want to add a step, but typing interrupts the current output. With `/steer`, you type while it works, and the instruction gets picked up organically at the right moment.

```bash
/steer "then deploy to staging after the build passes"
/steer "also log the output to /tmp/debug.log"
```

You can stack multiple steers — they execute in FIFO order, one per assistant turn.

### `/background` — Asynchronous Tasks

The heavy lifter for production workflows:

```bash
/background "Check if npm audit reports any critical vulnerabilities in the lockfile"
```

This runs the prompt as a background process with its own tool session. The main conversation keeps going. When the background task finishes, its result appears as a notice in the main thread.

```bash
/background "Deploy the staging environment and report back"
/background "Generate the API docs from the OpenAPI spec"
```

Background tasks have their own tool loop — they can read files, run terminal commands, search the web. They share the session context (config, working directory, tools) but run independently.

**Caveat**: Background tasks are not durable — if the parent session ends, they are cancelled. For durable scheduled work, use the `cronjob` tool or `hermes cron create`.

### `/queue` — Next-Turn Sequencing

The simplest of the four, and the most underrated:

```bash
/queue "after this, fix the failing test in tests/auth/test_login.py"
```

This queues a prompt for the next assistant turn. While the current turn is executing (running tool calls, processing results), `/queue` lets you pre-specify what comes next. When the current turn finishes, the queued prompt runs automatically.

This is especially useful when the current operation will take a while (multiple tool calls in sequence) and you already know what you want next. Instead of watching and waiting, you queue the next instruction and let the agent chain through both tasks.

## A Practical Scenario

Here is a real workflow that uses all four together:

You sit down to update your project's dependencies. The session unfolds like this:

1. **Set a goal**: `/goal "Upgrade all project dependencies to latest versions, fix breaking changes, and ensure all tests pass"`

2. **Start the upgrade**: "Run npm outdated and upgrade all packages"

3. **While it upgrades** (which involves running `npm outdated`, reading each changelog, deciding on major vs minor upgrades, and running `npm install`), you:
   - `/steer "after npm install, run the full test suite"`
   - `/background "Check if there are any known security advisories for packages we are upgrading"`

4. The agent finishes the install, the steer triggers the test suite to run. The background task returns: "Two packages have recent CVEs, here are the details."

5. **Queue the fix**: `/queue "Update the Dockerfile base image to match the new Node.js version from the upgrade"`

6. The queued task runs automatically after step 4's output renders.

The entire upgrade — dependency changes, test fixes, Dockerfile update, security check — happens in one continuous session without you having to re-state context or wait for each step to finish before typing the next instruction.

Without these commands, you would type "upgrade deps", wait, read output, type "run tests", wait, type "check security", wait, type "update Dockerfile". With them, you type everything once and the agent sequences the work.

## A Gotcha

**`/steer` does not interrupt mid-tool-call output.** If the model is in the middle of a long `terminal` command (e.g., downloading packages), the steer instruction queues up and fires after the *next* tool response — meaning after the command finishes. This is by design — interrupting a running shell command would corrupt its state — but it means `/steer` is not "stop what you are doing and do this instead." It is "when you finish what you are doing, add this step."

New users sometimes expect `/steer` to work like an interrupt. It does not. For that use case, use `/retry` to cancel the current response and start fresh.

**`/goal` does not survive a full exit and relaunch** unless the session is resumed. If you exit Hermes and start a new session with `hermes` (no `--continue`), the goal is lost. Always use `hermes --continue` or note the session ID to resume with `hermes --resume <id>` to preserve the goal.

**`/background` tasks share the working directory and environment.** If you change directories in the main session, background tasks that were already running can hit stale paths. Set working directories explicitly inside background prompts when paths matter.

## Closing

These four commands transform Hermes from a single-turn chat interface into a persistent work orchestrator. They are the difference between talking *to* an agent and directing *with* an agent.

- `/goal` — Persistent objectives, detailed in the [goal system docs](https://hermes-agent.nousresearch.com/docs/reference/slash-commands#-goal)
- `/steer` — Future instruction injection, in the [slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands#-steer)
- `/background` — Asynchronous tasks, see the [background execution guide](https://hermes-agent.nousresearch.com/docs/user-guide/features/background)
- `/queue` — Next-turn sequencing, documented in the [slash commands reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands#-queue)

Next time you open Hermes, try setting a goal before you type anything. You might not go back.
