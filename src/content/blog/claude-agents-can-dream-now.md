---
title: "Claude agents can dream now"
description: "Anthropic's new 'Dreaming' feature lets AI agents review their own past sessions and get better without human retraining. The architecture is the real story."
pubDate: "May 14 2026"
heroImage: "/blog-placeholder-about.jpg"
---

Anthropic shipped something quietly radical at their Code with Claude conference last week. Buried under the compute partnership announcements and the doubled rate limits was a research preview called "Dreaming."

The name sounds like marketing. It is not.

Dreaming is a scheduled background process that lets Claude Managed Agents review their own past sessions — up to 100 at a time — extract behavioral patterns, and update their memory stores without human intervention. Inputs are immutable. Changes only take effect when the agent explicitly adopts them. But the loop is closed: the agent gets better at its job between sessions, not just during retraining.

This is not the same thing as a model fine-tune. Fine-tuning changes the weights. Dreaming changes the agent's understanding of its own track record.

## The architecture matters

Most AI agents today are amnesiacs. A session starts, work happens, the session ends, and everything the agent learned about how you like things done is gone. The next session starts fresh. Engineers compensate by stuffing history into system prompts — an approach that works until the prompt grows past what the model can effectively use, which happens fast.

Dreaming solves a different problem. Instead of trying to cram more context into every request, it runs an offline processing phase that turns raw session history into structured memory. Patterns emerge. Repetitive failures get flagged. Approaches that worked get reinforced.

The three-layer architecture is worth understanding:

**In-context memory** — the working memory during a single session. What the model sees right now.

**External memory stores** — vector databases or key-value stores that survive between sessions. Retrievable, but require explicit logic to query.

**Dreaming** — the offline phase that extracts meaning from accumulated session data and writes it back into the memory system so the next session starts smarter.

The first two are table stakes now. The third is new.

## What it looks like in practice

An agent handling customer support can review a week of tickets during idle hours and surface patterns: "Users asking about feature X consistently need a workaround before it resolves." Next week, that insight is part of the agent's memory without anyone writing a playbook.

A coding agent that failed on a certain type of refactoring can analyze what went wrong across multiple attempts and adjust its approach. Not through a prompt tweak from a human. Through its own analysis of what didn't work.

The risk is obvious: agents that learn bad habits and embed them. Anthropic addresses this by keeping inputs immutable and requiring explicit adoption of changes. Nothing writes itself into the agent's memory without a checkpoint. But the direction is clear — the more the agent runs, the better it should get.

## The industry shift

OpenAI updated its Agents SDK in April with native sandbox execution and a model-native harness. Google launched Workspace Intelligence at Cloud Next, embedding agents directly into Docs, Sheets, and Gmail. Meta is reportedly building a "highly personalised AI assistant" for everyday tasks. The CNBC "agentic wars" narrative is real — Big Tech is placing bets on agents that act, not just chat.

Dreaming is Anthropic's answer to a specific weakness in that race. Most of the competition is fighting over who can build the most capable agent at session start. Anthropic is betting that what happens between sessions matters just as much.

## The open question

Self-improving agents are the goal. Dreaming is the first credible architecture for that at scale — but it is a research preview for a reason. The failure modes are unknown. An agent that reinforces its own biases over 100 sessions is not obviously better than one that forgets everything. The safety architecture around the dreaming process — immutable inputs, explicit adoption, scheduled rather than continuous operation — suggests Anthropic understands the downside.

The question is not whether Dreaming works. It is whether the pattern holds when agents run for months, across thousands of sessions, with edge cases that no human designed for. The answer to that question will determine whether "self-improving agents" becomes a product category or a cautionary tale.

Either way, the architecture is the story. Not the name.
