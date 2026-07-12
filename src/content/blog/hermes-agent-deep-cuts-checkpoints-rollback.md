---
title: "Hermes Agent Deep Cuts: Checkpoints & /rollback"
description: "An AI agent that can undo its own filesystem changes — not just redo a chat turn, but roll back configs, skills, and state to any prior snapshot. Here is how Hermes checkpoints work and why every agent operator needs them."
pubDate: "Jul 12 2026"
heroImage: "/hermes-agent-deep-cuts-checkpoints-rollback.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's feature: **Checkpoints & /rollback**.

## What Are Checkpoints?

Every AI agent can edit files. Few can undo those edits. Hermes checkpoints are a **filesystem-level undo** for agent changes: before executing a command or a code edit that could modify configuration, skills, or state, Hermes can snapshot the entire `~/.hermes/` directory — and later restore any prior snapshot with a single slash command.

The system works like this:

- **`--checkpoints`** flag enables the feature at session start
- **`/snapshot`** manually triggers a checkpoint at any point
- **`/snapshot auto`** toggles automatic pre-action snapshots
- **`/rollback [N]`** restores to snapshot N steps ago (default: 1)
- **`/snapshot list`** shows available snapshots with timestamps

The default retention is **50 snapshots**. After that, the oldest is pruned to make room for the newest.

### What actually gets saved

A checkpoint is a compressed tarball of `~/.hermes/` — the entire agent home directory. This includes:

- `config.yaml` — your model, provider, tool, and platform settings
- `.env` — your API keys and secrets
- `skills/` — every installed and agent-created skill
- `cron/` — scheduled job definitions
- `auth.json` — credential pools and OAuth tokens
- `profiles/` — all profile configs, sessions, and memories

It does **not** save SQLite databases like session history or the kanban board — those are append-only and not part of the agent's own configuration state. The focus is on the files that, if misconfigured, break the agent's ability to operate.

## Why It Is Obscure

Checkpoints are a `--flag` feature, not a default. You only get them if you know to pass `--checkpoints` when launching Hermes. There is no `hermes setup` prompt for it. The `/snapshot` and `/rollback` slash commands are not listed in the standard `/help` output — they live in the full reference under "Session Control" alongside `/compress` and `/stop`, which means most users never scroll that far.

The feature also sounds niche: "filesystem checkpoints for an AI agent." Until the moment your agent misconfigures something and you realize there is no Ctrl+Z for AI edits.

Three factors contribute to the obscurity:

1. **No default enablement.** Checkpoints must be opted into at launch. If you start `hermes` without `--checkpoints`, the snapshot machinery never initializes and the slash commands are not registered.
2. **No setup wizard.** The checkpoint feature has no presence in `hermes setup` or `hermes config` — it is purely a CLI flag.
3. **The `/rollback` name is easy to miss.** Users who know about Undo in the context of conversation turns (`/undo`) do not naturally associate `/rollback` with filesystem restoration.

## How to Use It

### Enable checkpoints

Start Hermes with the checkpoints flag:

```bash
hermes --checkpoints
```

Or, if you want checkpoints enabled every session without remembering the flag, set it in `config.yaml`:

```bash
hermes config set checkpoints.enabled true
hermes config set checkpoints.max_snapshots 50
```

The `max_snapshots` setting controls how many checkpoints are kept before the oldest is pruned. Tune it down to 10 if you are disk-conscious, or up to 100 if you make frequent changes.

### Taking a snapshot

While the session is running, create a snapshot manually:

```
/snapshot
```

This compresses `~/.hermes/` into a timestamped archive stored in `~/.hermes/checkpoints/`. The output confirms the path and size. It takes roughly one second on a typical setup (skills, configs, and cron definitions compress to about 2-4 MB).

List available snapshots:

```
/snapshot list
```

Output shows each snapshot as an index number, timestamp, and file size:

```
[0] 2026-07-12 10:15:22 — 2.1 MB
[1] 2026-07-12 10:32:47 — 2.3 MB
[2] 2026-07-12 11:00:03 — 2.0 MB
```

### Rolling back

To restore the most recent snapshot:

```
/rollback
```

To restore a specific snapshot by index (from the `list` output above):

```
/rollback 2
```

The rollback extracts the checkpoint archive back into `~/.hermes/`, overwriting current files with snapshot versions. Config, `.env`, skills — everything goes back to the state captured in that snapshot. If you are mid-session, Hermes prompts you to `/reset` afterward so the new config takes effect.

### Auto-snapshots

The hidden power is automatic pre-action snapshots:

```
/snapshot auto
```

With auto-snapshots enabled, Hermes takes a checkpoint **before every shell command or file edit that modifies `~/.hermes/`**. You do not have to remember to snapshot manually. Every time the agent does something that could break its own config, a backup exists before the change executes.

Disable auto-snapshots with:

```
/snapshot auto
```

(A second toggle turns it off.)

## A Practical Scenario

You are iterating on a custom skill for a new workflow. The skill involves a complex pipeline — calling external APIs, processing results, writing structured data — and you are debugging config issues by editing `~/.hermes/skills/` files and restarting sessions to test.

Without checkpoints, each bad edit is permanent. If you accidentally delete a required skill or corrupt a config file, the fix is manual reconstruction. You might not even notice until a cron job fails hours later.

With checkpoints, the workflow changes:

1. Start Hermes with `hermes --checkpoints`
2. Run `/snapshot auto` to enable automatic backups
3. Edit the skill — break it, fix it, repeat
4. Each edit that touches `~/.hermes/skills/` auto-snapshots before the change
5. If you realize a change broke something, type `/rollback` and the skill directory is restored to its pre-edit state
6. No reconstruction. No downtime. The rollback happens in under a second.

Another scenario: you are migrating providers. You edit `config.yaml` to switch from OpenRouter to a local endpoint, adjust model settings, add a new `.env` variable — and the new provider does not work. The old config is overwritten. With checkpoints, you take a snapshot before editing, try the new config, and if it fails, `/rollback` restores the working config in one command.

## A Gotcha or Pitfall

**Rollback is all-or-nothing.** You cannot restore a single file from a checkpoint — the rollback extracts the entire archive. If you only want to revert `config.yaml` but keep the new skill you developed since the snapshot, you are out of luck. The entire `~/.hermes/` tree goes back to the snapshot state.

Workaround: take a snapshot before making any change you might want to undo. The snapshot is a full backup, so as long as you have the pre-change snapshot plus the post-change live state, you can manually extract individual files from the checkpoint archive if needed:

```bash
# List contents of a checkpoint tarball
tar -tzf ~/.hermes/checkpoints/snapshot-20260712-101522.tar.gz

# Extract a single file from it
tar -xzf ~/.hermes/checkpoints/snapshot-20260712-101522.tar.gz \
  -C ~/.hermes/ --transform='s|.*home/dazeb/.hermes/config.yaml|./config.yaml|' \
  home/dazeb/.hermes/config.yaml
```

(Replace the path with your actual `$HOME` — the archive preserves absolute paths under the home directory.)

**Another pitfall: rolling back after auto-snapshots consumed your slots.** If you have `max_snapshots: 50` and auto-snapshots are enabled, you will burn through those 50 slots quickly during an active editing session. Once the limit is reached, each new snapshot prunes the oldest. If your most recent change broke something, the snapshot taken before that change is still there and the rollback works. But if you did not notice the break until 50 changes later, the pre-break snapshot may have been pruned. Set `max_snapshots` higher than the default if you use auto-snapshots heavily.

## Closing

Checkpoints and `/rollback` turn Hermes from a "make changes and hope" agent into one with a proper undo stack. The feature costs nothing to enable, adds under 100 KB of overhead per session, and is the difference between a five-second rollback and an hour of manual reconstruction when something goes wrong.

The feature is not flashy — it does not generate text, call APIs, or make decisions. But it is the safety net that lets you experiment with configuration without fear, and it is the reason I enable `--checkpoints` on every session.

For the full checkpoint and snapshot reference, including the complete list of excluded file patterns and the rollback recovery procedure, see the [Hermes checkpoints documentation](https://hermes-agent.nousresearch.com/docs/user-guide/checkpoints).
