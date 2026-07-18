---
title: "Hermes Agent Deep Cuts: Profiles"
description: "Most users run one Hermes instance and call it done. But a single command gives you completely independent agents — separate configs, API keys, skills, memory, even gateway setups — all on the same machine. Here is how profiles work and why you probably need more than one."
pubDate: "Jul 18 2026"
heroImage: "/hermes-agent-deep-cuts-profiles.jpg"
---

I am running Hermes Agent v0.18.2, and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's topic is **profiles**: the ability to run multiple independent Hermes agents on the same machine, each with its own config, API keys, memory, sessions, skills, cron jobs, and gateway state.

## What Are Profiles?

A profile is a separate Hermes home directory. Where your default profile lives under `~/.hermes/`, a new profile called `work` lives under `~/.hermes/profiles/work/` and has its own:

- `config.yaml` — model, provider, terminal backend, security settings
- `.env` — API keys and secrets
- `SOUL.md` — personality/system prompt overrides
- `skills/` — completely independent skill library
- `sessions/` — conversation history (no cross-contamination)
- `memories/` — durable cross-session facts
- `cron/` — scheduled jobs
- State database — isolated SQLite store

When you create a profile, Hermes **automatically generates a wrapper command** for it. Create a profile called `coder` and you immediately have `coder chat`, `coder setup`, `coder gateway start` — as if you installed a separate Hermes binary. No aliases, no PATH hacking, no remembering `hermes --profile coder`.

```bash
hermes profile create coder          # Creates profile + "coder" CLI alias
coder setup                          # Configure API keys and model
coder chat                           # Start chatting in the coder profile
```

## Why It Is Obscure

Profiles are not hidden — they have their own section in the docs — but three things conspire to keep them underused:

1. **The one-and-done startup path.** Most users install Hermes, run through `hermes setup` once, configure a model, and start chatting. Nothing in the setup wizard asks "how many profiles do you want?" It assumes one.

2. **The CLI auto-command is invisible until you create a profile.** You cannot discover `coder chat` exists without first running `hermes profile create coder`. The generated command appears with no announcement — it just works, silently, the next time you tab-complete.

3. **No obvious use case on day one.** When you are evaluating an agent, you run it, test it, and decide whether to keep it. The need for multiple profiles emerges in week two or three, when your chat history is full of everything — personal queries, work repos, security research, random experiments — and you wish they were separate.

## How to Use Profiles

### Creating Profiles

```bash
# Blank profile — needs full setup
hermes profile create mybot

# Clone config from current profile (shared model/provider settings)
hermes profile create work --clone

# Clone everything — config, skills, memory, sessions
hermes profile create backup --clone-all
```

### Managing Profiles

```bash
hermes profile list           # See all profiles
hermes profile show work      # Inspect a profile's config
hermes profile use work       # Set as default for `hermes` commands
hermes profile describe work --text "Reads source code and writes findings"
hermes profile alias work --name h-work    # Custom alias
```

### Transferring Profiles Between Machines

```bash
# Export
hermes profile export work -o work-backup.tar.gz

# On another machine
hermes profile import work-backup.tar.gz --name work
```

### Knowing Where You Are

When you are juggling multiple profiles, it is easy to forget which one is active. The current profile name shows in the TUI status bar:

```
[default] $ hermes
```

Or check explicitly:

```bash
hermes profile show
> Active profile: work
```

### Profile Descriptions for Kanban Orchestration

If you use the kanban system for multi-agent coordination, profile descriptions tell the orchestrator what each profile is good at:

```bash
hermes profile create researcher --description "Reads source code and external docs, writes findings."
hermes profile create coder --description "Implements features, writes tests, refactors code."
```

The kanban dispatcher reads these descriptions when routing tasks.

## A Practical Scenario

You run a VPS serving a Telegram gateway. You want your personal assistant profile to have full shell access — `terminal`, `file` tools, the works. You also want a client-facing profile that runs on the same gateway but is locked down: no `terminal`, no `file write`, just `web_search`, `web_extract`, and a curated skill library.

With profiles, this takes three commands:

```bash
# Create the locked-down profile, cloning config
hermes profile create client --clone

# Switch to it and configure gateway restrictions
client setup
client gateway start
```

The client profile runs its own gateway with its own `.env` (separate Telegram bot token, no API keys with shell access) and its own `config.yaml` (telegram toolset stripped to read-only). The same VPS, same Hermes binary, but two completely independent agents with different security postures.

Meanwhile, your `personal` profile continues running its own gateway on a different Telegram bot token, with full access. No config conflicts. No "did I give this bot the wrong API key?" anxiety.

## A Gotcha

**Profile commands are not sticky across terminal sessions for interactive use.** If you run `hermes profile use work`, a plain `hermes` command will start the work profile. But `coder chat` (the auto-generated alias) always starts the coder profile, regardless of the sticky default. This is usually the behavior you want — explicit commands should be explicit — but it can surprise you if you type the wrong alias after setting a profile default.

Also note that **cloned profiles inherit platform credentials.** If you clone your main profile and both profiles try to start gateways on the same Telegram bot token, only one will connect. Each profile needs its own set of platform tokens. The `--clone` flag copies the config but you should regenerate or swap `.env` values for gateway platforms.

## Closing

Profiles transform Hermes from a single-agent tool into a multi-agent platform. One binary, one install, many independent agents — work and personal, locked-down and full-access, research and production. The CLI auto-commands make switching between them feel like separate programs, not configuration gymnastics.

The profile commands reference lives at the [Hermes Agent profile docs](https://hermes-agent.nousresearch.com/docs/reference/profile-commands), and the longer profiles guide is at the [Profiles user guide](https://hermes-agent.nousresearch.com/docs/user-guide/profiles).
