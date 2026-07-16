---
title: "Hermes Agent Deep Cuts: Gateway Per-Platform Toolsets"
description: "The same Hermes agent, different capabilities depending on where you talk to it — Telegram gets search and read-only, CLI gets everything, Discord sits in between. Here is how per-platform toolsets work and why every gateway user should configure them."
pubDate: "Jul 16 2026"
heroImage: "/hermes-agent-deep-cuts-gateway-per-platform-tools.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's topic is **gateway per-platform toolsets**: the ability to give your Hermes agent different tool capabilities depending on which platform you are talking to it from.

## What Is Gateway Per-Platform Toolsets?

Hermes Agent has a multi-platform gateway — the same agent instance can simultaneously serve Telegram, Discord, Slack, WhatsApp, Signal, the CLI, and a dozen other platforms. Most users who set up the gateway connect one or two platforms and call it done. What they miss: **each platform can have its own toolset configuration.**

This means:

- **Telegram** — search the web, read files, delegate research tasks. No terminal access, no code execution, no file writes.
- **Discord** — web search, read-only file access, skill management. No dangerous shell commands.
- **CLI** — full toolset: terminal, code execution, browser, file writes, everything.
- **API Server** — a curated subset for programmatic consumption.

Same agent. Same memory, same skills, same cron jobs. Different capabilities per surface.

## Why It Is Obscure

Three reasons most users never configure this:

1. **The gateway setup wizard is easy-mode** — `hermes gateway setup` walks you through connecting platforms, but it does not prompt you to configure per-platform toolsets. It assumes the defaults are fine.
2. **The tools UI hides per-platform toggles** — `hermes tools` opens a curses interface that shows toolsets and their status, but the per-platform column is easy to miss unless you know to look for it.
3. **There is no error when you skip it** — the agent works fine everywhere with the default toolset. You never feel the gap until a production terminal command fires from a Telegram message and you think "wait, I did not want that running from my phone."

## How to Use It

The per-platform tool configuration lives in the `hermes tools` curses interface. Open it:

```bash
hermes tools
```

You will see a table like this (simplified):

```
Toolset         │ CLI │ Telegram │ Discord │ Slack
────────────────┼─────┼──────────┼─────────┼──────
web             │  ✔  │    ✔     │    ✔    │  ✔
terminal        │  ✔  │    ✘     │    ✘    │  ✘
file            │  ✔  │    ✔     │    ✔    │  ✔
code_execution  │  ✔  │    ✘     │    ✘    │  ✘
browser         │  ✔  │    ✘     │    ✘    │  ✘
vision          │  ✔  │    ✔     │    ✔    │  ✔
image_gen       │  ✔  │    ✔     │    ✔    │  ✔
skills          │  ✔  │    ✔     │    ✔    │  ✔
delegation      │  ✔  │    ✔     │    ✔    │  ✔
cronjob         │  ✔  │    ✘     │    ✘    │  ✘
```

Toggle with space or enter. The changes take effect on the next `/reset` or gateway restart.

You can also control this from `~/.hermes/config.yaml` if you prefer text over curses:

```yaml
toolsets:
  terminal:
    platforms:
      cli: true
      telegram: false
      discord: false
      slack: false
  code_execution:
    platforms:
      cli: true
      telegram: false
  browser:
    platforms:
      cli: true
      telegram: false
```

The per-platform overrides merge with the global toolset enable/disable — if a toolset is globally disabled, no platform can use it.

Additionally, skills can be gated per platform:

```bash
hermes skills config
```

This opens a similar interface showing which skills are loaded on which platform. A skill about system administration might be CLI-only, while a note-taking skill is available everywhere.

## A Practical Scenario

You run Hermes on a VPS with the gateway serving Telegram (your mobile interface) and the CLI (your workstation interface). Every morning, you:

**On Telegram (mobile, walking to coffee):**
- `/skills find fetch-api` — search for a skill
- `What is the status of the production deploy?` — web search for status
- `Summarize the latest PR reviews` — delegation to research
- No terminal commands execute from here. The model cannot accidentally `docker rm -f $(docker ps -aq)` from your phone.

**On the CLI (workstation, at desk):**
- Full terminal access for debugging
- `code_execution` for analyzing data
- Browser automation for testing UI
- Cron management

The same session, the same agent, the same memory. But the risk profile is wildly different per surface. The Telegram side is effectively read-only for infrastructure operations. The CLI side has the keys to everything.

This is not a theoretical scenario — it is the exact configuration that prevents an accidental `rm -rf /var/lib/docker` from an mistyped Telegram command. The gateway integration test suite at Hermes includes a regression test for exactly this case: verifying that `terminal` tool calls are rejected on Telegram while `web_search` passes through.

## A Gotcha

**Platform toggles take effect on session reset, not instantly.** If you disable `terminal` for Telegram at 10:00, any currently running Telegram session continues with the old toolset until it resets (`/new` or `/reset`). This is because Hermes snapshots the toolset at session creation to preserve prompt caching — changing tools mid-session would invalidate the cached system prompt.

The same applies to `hermes skills config` changes. Always run `/reset` on the target platform after changing toolsets or skill visibility.

Another subtlety: **the default toolset for new platforms is "inherit from CLI".** If you add a new platform (say, Matrix) and have not explicitly configured its tools, it inherits the CLI toolset — which may include terminal and code execution. Always explicitly configure a new platform's tools before connecting it to untrusted surfaces. The safest pattern is to create a "gateway" profile with restricted tools and point all messaging platforms at it.

## Closing

Per-platform toolsets turn a single Hermes instance into a multi-surface agent that respects the security posture of each interface. Your phone should not be able to run `docker kill` commands. Your CLI should be able to do everything. The gateway makes this distinction possible — but only if you configure it.

For the full gateway platform documentation, including the complete list of supported platforms and per-platform configuration options:

[https://hermes-agent.nousresearch.com/docs/user-guide/messaging/](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/)
