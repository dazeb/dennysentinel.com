---
title: "Hermes Agent Deep Cuts: Credential Pools"
description: "Pool multiple API keys for the same provider and auto-rotate on rate limits — no more staring at 429 errors mid-session. Here is how Hermes credential pools work and why every heavy user should set them up."
pubDate: "Jul 10 2026"
heroImage: "/hermes-agent-deep-cuts-credential-pools.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's feature: **Credential Pools**.

## What Are Credential Pools?

Credential pools let you register **multiple API keys for the same provider** and have Hermes automatically rotate through them when one gets rate-limited, exhausted, or returns an error. Instead of hitting a wall mid-conversation, the next key in the pool gets picked up transparently — your session never stalls.

The system lives entirely behind the `hermes auth` CLI and is supported across every major provider: OpenRouter, Anthropic, OpenAI, DeepSeek, Google, and any custom endpoint. You add keys interactively, list them to verify, and when a provider starts returning 429s, Hermes tries the next credential in the pool automatically.

```bash
hermes auth add             # Interactive credential wizard
hermes auth list            # Show pooled credentials
hermes auth list openrouter # Filter by provider
hermes auth remove openrouter 0  # Remove credential at index 0
hermes auth reset openrouter   # Clear exhaustion state
```

## Why It Is Obscure

Three reasons most users never find credential pools:

**1. Setup wizard skips it.** When you run `hermes setup` or `hermes model` for the first time, it asks for one API key per provider. That works, you move on, and you never think about what happens when that single key runs out of tokens or hits its rate limit.

**2. The `auth` CLI group sounds like OAuth.** When you see `hermes auth`, the association is authentication — logging in with OAuth, managing tokens. Most users never explore it because they already authenticated. The credential-pooling feature is buried inside what looks like an auth management subcommand.

**3. Rate limits are "someone else's problem" until they aren't.** When you are new to Hermes, you use one provider with one key and it works fine. It only becomes a problem after hours of heavy use — the kind of sustained session that burns through 100+ tool calls in a single day. By then, you are in a flow and do not want to stop to figure out multi-key rotation.

## How to Use It

Setting up credential pools is straightforward. Here is the flow:

### 1. Add your first key (you already did this)

When you configured Hermes the first time, you set `OPENROUTER_API_KEY` in `.env` or went through `hermes setup`. That key is registered automatically in the credential pool for its provider.

### 2. Add more keys

```bash
hermes auth add
```

This launches an interactive wizard. It asks:
- Provider (OpenRouter, Anthropic, OpenAI, etc.)
- API key (paste it — hidden input)
- Optional label (e.g., "work account", "backup key")

Repeat for each additional key. Stacking five OpenRouter keys means you have five times the rate limit before Hermes has to slow down.

### 3. Verify your pool

```bash
$ hermes auth list openrouter
Pooled credentials for openrouter:
  [0] •••••a1b2 • active — requests: 847, last error: none
  [1] •••••c3d4 • active — requests: 623, last error: none
  [2] •••••e5f6 • active — requests:  12, last error: rate_limited (2m ago)
```

Each entry shows:
- Index number (for removal)
- Masked key prefix
- Status (active, exhausted, rate_limited)
- Request count
- Last error (if any) and time

### 4. Reset exhaustion

If a key was rate-limited but the cooldown period has passed, you can clear its exhaustion state:

```bash
hermes auth reset openrouter
```

This marks all keys for the provider as available again without removing them from the pool.

## A Practical Scenario

You are running a multi-hour red teaming session against models from multiple providers. Your OpenRouter key has a limit of roughly 10 requests per minute. In a heavy session with parallel agent delegations, you will hit that limit in the first 15 minutes.

Without credential pools: your session stalls, Hermes shows a provider error, you scramble to find a second key, paste it into `.env`, restart the session, and lose all of your in-context continuity.

With credential pools: you registered three OpenRouter keys before starting. When the first key returns a 429, Hermes tries the second key on the very next request. No interruption. No error message. No session restart. The pool's exhaustion logic even knows to re-try the first key once its rate-limit window expires, so you effectively get 3× the throughput.

The same applies to heavy batch processing — bulk inference runs, large codebase migrations, or running eval suites that make hundreds of concurrent API calls. Instead of tuning batch sizes to stay under a single key's limit, you throw more keys at the problem.

## A Gotcha or Pitfall

**Pooling does not solve provider-level outages.** If Anthropic's API is down in your region, having five Anthropic keys does not help — they all go to the same upstream. Credential pools protect against *key-level* exhaustion (rate limits, quota depletion), not provider-level downtime. For that, you want multi-provider routing with fallbacks configured in `hermes model`, which is a different mechanism entirely.

Also: exhaustion state is **not persisted across Hermes profile switches** by default. If you run a session in your `work` profile, get rate-limited, switch to your `personal` profile, the rate-limit counter for that provider starts fresh because each profile maintains its own credential pool state. Good for working around limits; bad if you expect pools to be global.

## Closing

Credential pools are one of those features that is invisible when you do not need it and indispensable when you do. Five minutes of setup buys you uninterrupted sessions even during peak usage — no more mid-work scramble to find a backup API key.

For the full auth documentation and provider-specific setup, see the [Hermes credentials documentation](https://hermes-agent.nousresearch.com/docs/reference/credentials).
