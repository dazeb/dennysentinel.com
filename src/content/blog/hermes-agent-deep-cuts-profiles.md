---
title: "Hermes Agent Deep Cuts: Profiles"
description: "Most users run one Hermes instance and never realize they can have independent work, security research, and personal profiles — each with its own config, skills, cron jobs, and memory. Here is how profiles work and why they change everything."
pubDate: "Jul 09 2026"
heroImage: "/hermes-agent-deep-cuts-profiles.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is the first in an ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's feature: **Profiles**.

## What Are Profiles?

Hermes profiles are fully independent agent instances sharing the same binary. Each profile gets its own:

- **Config** — model provider, toolsets, terminal backend, compression settings
- **Skills** — an isolated skill directory loaded only in that profile
- **Sessions** — separate conversation history, never cross-contaminated
- **Cron jobs** — scheduled tasks belong to the profile that created them
- **Memory** — durable facts stay in their profile's namespace
- **Plugins** — enabled per-profile, not globally

You create a profile, switch to it with `--profile`, and Hermes treats it like a different installation. The config files live under `~/.hermes/profiles/<name>/` with the same layout as the default profile.

```bash
hermes profile create security-lab
hermes --profile security-lab
```

That is it. You now have a second Hermes that cannot see your work profile's sessions, does not have access to the same skills, and talks to a different model if you configure it that way.

## Why It Is Obscure

Profiles are not hidden, but they are easy to miss. The default `hermes` command runs the "default" profile with zero indication that more exist. The `hermes profile list` subcommand is buried in a long CLI reference, and the profile system really shines when you combine it with other features — worktree mode (`-w`), per-profile cron jobs, and isolated skill directories — that most users discover one at a time.

The documentation covers profiles, but there is no runtime hint that shouts "you could be running three of these." Most people use one profile indefinitely, treating Hermes as a single agent rather than a multi-instance framework.

## How to Use Profiles

### Create and Switch

```bash
# List existing profiles
hermes profile list

# Create from scratch
hermes profile create redteam

# Clone your current profile as a starting point
hermes profile create personal --clone

# Switch for a single command
hermes --profile redteam chat -q "Scan our infrastructure for exposed ports"

# Set a profile as your default
hermes profile use personal
```

### Per-Profile Configuration

Each profile has its own `config.yaml` and `.env`. This means you can wire different providers, models, and tools to different profiles:

```bash
# Work profile uses Claude for coding
hermes --profile work config set model.default anthropic/claude-sonnet-4

# Redteam profile uses a cheaper model for reconnaissance
hermes --profile redteam config set model.default openrouter/deepseek/deepseek-v3

# Personal profile uses a local model (no API cost)
hermes --profile personal config set model.provider openai-compatible
hermes --profile personal config set model.base_url http://localhost:1234/v1
```

### Per-Profile Skills

Skills installed in one profile do not pollute another. This is useful when you want security-research skills available in your redteam profile but not in your work profile, or when you are testing a new skill before promoting it:

```bash
# Skills live under ~/.hermes/profiles/<name>/skills/
hermes --profile redteam skills install cybersecurity-skill-bundle
hermes --profile work skills list  # No security tools visible here
```

### Per-Profile Cron Jobs

Cron jobs are profile-scoped. Your work profile's daily standup briefing does not interfere with your personal profile's morning news scan. Each scheduler runs independently:

```bash
hermes --profile work cron list
hermes --profile personal cron create "every morning 7am" "Summarize Hacker News top stories"
```

### Wrapper Scripts

For everyday use, `hermes profile alias` creates shell wrappers so you do not type `--profile` every time:

```bash
hermes profile alias work hw
hermes profile alias redteam hr

# Now these work:
hw chat -q "What is on my calendar today?"
hr chat -q "Check if our CVEs have any new exploits"
```

## A Practical Scenario

Here is a setup I run daily:

**Profile: `work`** — Claude Sonnet 4 via Anthropic, full toolset (web, file, terminal, browser, delegation), skills for code review and API design, cron jobs for daily standup prep and dependency audit. This is the profile I use for development and writing.

**Profile: `redteam`** — DeepSeek V3 via OpenRouter (cheaper for bulk scanning), terminal-heavy toolset with browser disabled, skills for CVE research and vulnerability assessment, cron jobs for overnight attack-surface scans against isolated lab targets. This profile has no access to my work repos or sessions.

**Profile: `personal`** — A local Llama model via Ollama (free, offline), limited to web search and note-taking skills, Telegram gateway only (no CLI). Used for personal research, reading summaries, and casual conversation.

Three independent agents. One binary. Zero cross-contamination.

## A Gotcha

**Profile isolation is filesystem-deep, not process-level.** Profiles share the same Hermes binary, Python runtime, and process namespace. A runaway cron job in one profile can consume system resources that affect another profile's running session. If you run profile-based workloads on resource-constrained hardware (like my WSL partition with 8 GB RAM), plan your cron schedules to avoid overlapping heavy jobs across profiles.

Also: `hermes profile delete` is destructive. It removes the entire profile directory including its sessions, skills, and cron definitions. There is no trash or undo — the curator safety net only covers skills in the default profile. Use `hermes profile show <name>` to review what a profile contains before deleting it.

## Closing

Profiles transform Hermes from a single-agent tool into a multi-instance agent orchestrator. They let you compartmentalize by role, provider, and risk level without running multiple installations or Docker containers. If you run Hermes for more than one kind of work, you are leaving capability on the table by using a single profile.

Relevant docs: [Hermes Agent Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)
