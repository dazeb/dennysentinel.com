---
title: "Hermes Agent Deep Cuts: Worktree Mode (`hermes -w`)"
description: "Run parallel agents on the same repo without clobbering each other — Hermes spins up isolated git worktrees automatically."
pubDate: "Jul 19 2026"
heroImage: "/hermes-agent-deep-cuts-worktree-mode.jpg"
---

I'm running Hermes Agent v0.18.2, and this post is part of the Deep Cuts series exploring lesser-known features that ship with Hermes but don't get the spotlight they deserve.

---

## What Is Worktree Mode?

`hermes -w` (or `hermes --worktree`) starts a Hermes session in an **isolated git worktree** — a separate checkout of the same repository at a different filesystem location, sharing the underlying `.git` directory but with its own working tree and branch.

Every invocation of `hermes -w` automatically:
1. Creates a new worktree under `.hermes/worktrees/<session-id>/`
2. Checks out a new branch named `hermes/<session-id>`
3. Runs the agent inside that worktree's directory
4. Cleans up the worktree on session exit (optional — see the gotcha below)

This is the same isolation pattern used by Claude Code (`claude -w`), OpenAI Codex (`codex --worktree`), and Cline — because without it, two agents editing the same files in the same directory is a recipe for corrupted state, lost edits, and merge conflicts you didn't ask for.

---

## Why It's Obscure

- **Hidden behind a single flag**: `-w` / `--worktree` is easy to miss in `hermes --help` output.
- **No interactive prompt**: Unlike profiles or model selection, there's no `hermes setup` wizard that asks "do you want worktree isolation?"
- **Documentation lives in a niche section**: The [git worktrees guide](https://hermes-agent.nousresearch.com/docs/user-guide/git-worktrees) is thorough but tucked under "User Guide → Git Worktrees" rather than front-and-center in the getting-started flow.
- **Most users run one agent at a time**: If you only ever have a single Hermes session, you never feel the pain this solves.

---

## How to Use It

### Basic invocation

```bash
# In your repo root
cd ~/myproject
hermes -w
# or
hermes --worktree
```

That's it. Hermes handles the `git worktree add` and branch creation internally. You'll see a banner like:

```
🌿 Worktree mode: .hermes/worktrees/20260719_143052_a1b2c3d
🌿 Branch: hermes/20260719_143052_a1b2c3d
```

### With a profile

```bash
hermes -w -p redteam
# or
hermes --worktree --profile redteam
```

Profiles and worktrees compose cleanly — the redteam profile gets its own isolated checkout.

### With a specific task (one-shot)

```bash
hermes -w -q "Refactor the auth middleware to use the new token format"
```

### Resume a worktree session

```bash
# List recent sessions (shows worktree paths)
hermes sessions list

# Resume by session ID — Hermes restores the worktree context
hermes --resume 20260719_143052_a1b2c3d
```

### Manual worktree management (advanced)

If you want control over the worktree location or branch name:

```bash
# Create your own worktree first
git worktree add ../myproject-feature-x feature/x

# Then run Hermes inside it (no -w flag needed)
cd ../myproject-feature-x
hermes
```

---

## A Practical Scenario: Parallel Feature Development

You're building a SaaS dashboard. Two features need to land this week:
1. **New billing page** — touches `src/billing/`, `src/api/billing.ts`, database migrations
2. **Real-time notifications** — touches `src/notifications/`, `src/api/ws.ts`, shared `src/hooks/`

Without worktrees, you'd have to:
- Run Hermes, wait for it to finish feature 1, commit, then run again for feature 2
- Or run two Hermes instances in the same directory and pray they don't edit the same file

With worktrees:

```bash
# Terminal 1: Billing feature
cd ~/saas-dashboard
hermes -w -q "Build the new billing page with Stripe integration, usage tables, and invoice PDF generation"

# Terminal 2: Notifications feature (runs simultaneously)
cd ~/saas-dashboard
hermes -w -q "Implement real-time notifications via WebSocket: server push, client hook, toast UI"
```

Each agent gets:
- Its own `src/` tree to edit freely
- Its own branch (`hermes/20260719_...` and `hermes/20260719_...`)
- No risk of clobbering the other's changes
- Shared git history — `git log --all --oneline --graph` shows both branches diverging from main

When both finish, you review each worktree's changes, merge or rebase onto `main`, and delete the worktrees:

```bash
# From main repo
git worktree list
# Shows both worktrees

# After reviewing & merging
git worktree remove .hermes/worktrees/20260719_143052_a1b2c3d
git worktree remove .hermes/worktrees/20260719_143053_d4e5f6
git branch -d hermes/20260719_143052_a1b2c3d
git branch -d hermes/20260719_143053_d4e5f6
```

---

## Combining with Delegation (Subagents)

`hermes -w` isolates the **parent** agent's filesystem. But what about `delegate_task` subagents?

By default, subagents inherit the parent's working directory — they share the same worktree. For true parallel isolation, combine worktrees with the `-w` flag **on each spawned agent**:

```bash
# Terminal 1: Spawn orchestrator in a worktree
hermes -w -q "Coordinate: spawn backend and frontend agents for the new user dashboard"

# Inside that session, the orchestrator uses delegate_task with worktree isolation:
# (The subagent would need its own -w invocation — currently requires manual setup)
```

> **Note**: Full subagent worktree isolation is an area Hermes is improving. For now, the cleanest pattern is multiple top-level `hermes -w` invocations in separate terminals, coordinated via Kanban (`hermes kanban`) or a shared spec document.

---

## A Gotcha: Worktree Cleanup on Crash

By default, Hermes **removes the worktree on clean exit** (`/exit`, `/quit`, Ctrl+D). But if the process is killed — `SIGKILL`, OOM, power loss, `tmux kill-session` — the worktree **stays on disk**.

You'll accumulate orphaned worktrees under `.hermes/worktrees/` and orphaned branches `hermes/*`.

### Cleanup routine

```bash
# List all worktrees
git worktree list

# Prune stale ones (removes worktree dirs for branches that no longer exist)
git worktree prune

# Or nuke everything Hermes created
rm -rf .hermes/worktrees/
git branch -D $(git branch | grep '^  hermes/')
```

### Pro tip: Disable auto-cleanup for debugging

If you want to inspect a worktree after the session ends (e.g., to see what the agent actually changed), set:

```bash
export HERMES_WORKTREE_KEEP=1
hermes -w
```

The worktree persists at `.hermes/worktrees/<session-id>/` with the agent's branch checked out.

---

## Related: Kanban + Worktrees = Multi-Agent Assembly Line

The [Kanban board](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban) (`hermes kanban`) is the missing piece for coordinating parallel worktree agents:

```bash
# Create a board
hermes kanban init

# Add tasks
hermes kanban create "Backend: User API endpoints" --assignee backend-agent
hermes kanban create "Frontend: User dashboard UI" --assignee frontend-agent

# Start workers in worktrees
hermes -w --profile backend-agent   # picks up "Backend: User API endpoints"
hermes -w --profile frontend-agent  # picks up "Frontend: User dashboard UI"
```

The Kanban dispatcher (running in the gateway) atomically claims tasks and spawns the right profile in its own worktree. This is how you get **true parallel agentic development** — not just "two agents in the same folder hoping for the best."

---

## Closing

Worktree mode is the difference between "I'll run Hermes on this repo" and "I'll run a fleet of Hermes agents on this repo." It's a single flag (`-w`) that unlocks the same isolation model the major AI coding tools converged on — because filesystem isolation is the only thing that actually works at scale.

**Docs**: [Git Worktrees Guide](https://hermes-agent.nousresearch.com/docs/user-guide/git-worktrees)  
**CLI reference**: `hermes --help` → `--worktree, -w`

---

*Next Deep Cut: STT/TTS voice stack — full speech pipeline with local and cloud providers. Stay tuned.*