---
title: "Hermes Agent Deep Cuts: Auxiliary Model Routing"
description: "Your expensive Claude or GPT model should not be describing images or compressing conversation context. Here is how to route auxiliary tasks to cheaper models — and why it cuts costs without cutting capability."
pubDate: "Jul 13 2026"
heroImage: "/hermes-agent-deep-cuts-auxiliary-model-routing.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's feature: **Auxiliary Model Routing**.

## What Is Auxiliary Model Routing?

Every Hermes session uses a main model — the one you set with `hermes model` or configured in `config.yaml`. That model handles your conversation, makes tool calls, and generates responses. But Hermes also runs several background tasks that do not need your expensive main model's full reasoning capability:

- **Vision analysis** — When you share an image, Hermes sends it to a vision-capable model for description
- **Context compression** — When the conversation approaches the token limit, Hermes summarizes earlier turns to stay under the window
- **Session search** — When you use `session_search`, an auxiliary model formulates search queries and synthesizes results

With auxiliary model routing, you can configure **separate models and providers** for each of these tasks. Your main model stays focused on what it does best — reasoning, coding, tool orchestration — while cheaper, faster, or task-specialized models handle the supporting work.

The configuration lives under the `auxiliary.*` keys in `config.yaml`:

```yaml
auxiliary:
  vision:
    provider: openrouter
    model: openai/gpt-4o-mini
  compression:
    provider: openrouter
    model: openai/gpt-4o-mini
  session_search:
    provider: openrouter
    model: openai/gpt-4o-mini
```

Each task gets its own provider and model. If you do not configure any auxiliary models, Hermes falls back to `auto` — which tries OpenRouter, then Google Gemini, in that order.

## Why It Is Obscure

Auxiliary model routing is invisible by design. When auxiliary tasks fire, there is no "now using GPT-4o-mini for vision" banner — Hermes just does the work. The fallback `auto` provider works well enough that most users never need to touch these settings.

Three reasons it stays hidden:

**1. No default configuration is generated.** When you run `hermes setup` or `hermes config`, the auxiliary section does not appear in the default config at all. You need to know it exists and add it manually. There is no wizard step that asks "which model should describe images?"

**2. The config key structure is nested.** `auxiliary.vision.provider` is not something you stumble on browsing flat keys. It lives in a `config.yaml` section that is not shown in `hermes config` output unless it has been populated.

**3. Vision and compression happen silently.** You might not even realize your main model is handling vision calls — they are embedded in the conversation loop, and Hermes does not log or announce which model processed the image. The cost just shows up in your API bill.

## How to Use It

### 1. Start with the default

Before configuring anything, check what Hermes is currently using:

```bash
hermes doctor
```

This shows your main model and provider. If you have not configured auxiliary models, the output does not mention them. That is normal — `auto` fallback is active by default.

### 2. Pick your auxiliary model

The ideal auxiliary model is:

- **Cheap** — you want to burn tokens on it freely (GPT-4o-mini at ~$0.15/M input tokens vs GPT-4o at ~$2.50/M is a 16× price difference)
- **Fast** — compression and vision run mid-conversation; latency matters
- **Vision-capable** — only relevant for the vision task, but if you route all three to the same model, it needs image support for vision

My default for all three auxiliary slots is `openai/gpt-4o-mini` via OpenRouter. It is fast, vision-capable, costs $0.15/M input tokens, and handles image descriptions and text summarization well enough that the main model never needs to take over.

### 3. Configure each task

Set each auxiliary task independently. Mix and match providers and models:

```bash
# Route vision to a cheap multimodal model
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model openai/gpt-4o-mini

# Route compression to a fast small model on a different provider
hermes config set auxiliary.compression.provider anthropic
hermes config set auxiliary.compression.model anthropic/claude-3-haiku

# Route session search to Google Gemini (free tier)
hermes config set auxiliary.session_search.provider google
hermes config set auxiliary.session_search.model gemini/gemini-2.0-flash
```

Each setting takes effect on the next session start (`/reset` in an active session, or exit and relaunch).

### 4. Verify the routing

After configuring, start a new session and trigger each auxiliary task:

1. **Vision** — send an image. Watch the API call logs or your provider dashboard. You should see calls to your configured vision model, not your main model.
2. **Compression** — the `/compress` slash command triggers a manual compression cycle. The auxiliary compression model processes the summary.
3. **Session search** — use `session_search` in a query. The auxiliary search model processes the retrieval and synthesis.

You can also check which model processed each call by inspecting your provider's usage dashboard. With OpenRouter, for example, each request shows the model slug in the request log.

## A Practical Scenario

You are running Hermes all day — coding, reviewing research papers, and discussing architecture. Your main model is Claude Sonnet 4 ($3.00/M input tokens). Over an 8-hour session, you share roughly 30 screenshots, trigger context compression four times, and run session search six times.

**Without auxiliary routing:** Claude Sonnet 4 handles every vision call, every compression pass, and every search query. Those 40 auxiliary calls add roughly 120,000 input tokens at $3.00/M — **$0.36 in auxiliary costs** that could have been $0.018 with GPT-4o-mini.

**With auxiliary routing:** GPT-4o-mini ($0.15/M) handles the same 120,000 tokens for **$0.018**. The cost difference is 20×. And the main model never wastes context on "this image contains a bar chart with four columns" — it starts its turn already knowing what the image contains, thanks to the auxiliary model's description.

The savings compound with heavy usage:

| Usage pattern | Main model cost | Auxiliary cost (no routing) | Auxiliary cost (routed) |
|---|---|---|---|
| Light (10 images/day) | — | $0.09 | $0.0045 |
| Medium (30 images + 5 compressions) | — | $0.45 | $0.023 |
| Heavy (100 images + 20 compressions) | — | $1.50 | $0.075 |

These numbers assume GPT-4o-mini at ~100 tokens per image description. Real costs vary, but the ratio is consistent: routing auxiliary tasks to a cheaper model cuts their cost by 15–20×.

Beyond cost, there is a latency benefit. GPT-4o-mini responds in ~300ms versus Claude Sonnet 4's ~800ms for the same prompt. Vision calls and compression runs complete faster, making the session feel snappier — especially during `/compress` cycles where the user is waiting.

## A Gotcha or Pitfall

**The `auto` fallback may not fail gracefully for all tasks.** If your `auto` provider targets OpenRouter and OpenRouter has no available endpoint for the requested auxiliary task (for example, a vision request when no vision-capable model is available through the configured fallback chain), the task can silently fail or produce empty output. Hermes does not raise an error — the auxiliary result is just not there, and the main model proceeds without it.

This is most visible with **context compression**. If the compression model fails, the conversation continues growing until it hits the token limit, at which point Hermes may truncate or drop older messages. You get no warning — just a session that mysteriously stops remembering early context.

**Mitigation:** Explicitly set at least the compression auxiliary model to a reliable fallback. I use `openai/gpt-4o-mini` because it is available through multiple providers and has near-perfect uptime. If cost is a concern, Google's Gemini 2.0 Flash is free-tier eligible and equally reliable.

Also note: **auxiliary models do not apply to `delegate_task` children.** Each delegated subagent uses its own model — configured separately under `delegation.model` and `delegation.provider` in `config.yaml`. The auxiliary routing only applies to the parent session's embedded tasks.

## Closing

Auxiliary model routing is one of those configuration optimizations that quietly saves you money every single session. It does not add new capabilities — but it makes your existing capabilities cheaper and faster by ensuring the right model handles the right job. A single `config.yaml` section, five minutes of setup, and your expensive main model stops doing busywork.

The feature is documented on the [Hermes configuration page](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) under the Auxiliary section. That reference lists all available auxiliary task keys, supported providers, and per-task model recommendations.
