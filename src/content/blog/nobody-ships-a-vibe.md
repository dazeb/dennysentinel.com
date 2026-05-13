---
title: "Nobody ships a vibe"
description: "Vibe coding makes great demos. Production agents need sandboxing, audit trails, and boundaries. The boring stuff is the product."
pubDate: "May 13 2026"
heroImage: "/blog-placeholder-about.jpg"
---

Vibe coding is having a moment. Describe an app to an AI. Watch it generate a working prototype in minutes. Ship it before lunch. The demos are genuinely impressive.

The subreddits are full of people doing it. The YouTube tutorials promise it is the future. One weekend, one prompt, one product. The pitch is seductive.

It also has nothing to do with running autonomous agents in production.

Last week, OpenAI published something that got far less attention than the demo videos. On May 8, they released a detailed technical post called "Running Codex safely at OpenAI." It is not a launch announcement. It is not a hype piece. It is a security playbook.

The post walks through how OpenAI's own engineering teams deploy coding agents internally. It covers sandboxing policies, approval workflows, network boundaries, credential management, and agent-native telemetry. Every section ends with a TOML config block.

The message is clear: if you run an agent that can write code, read repositories, and execute commands, you need hard boundaries around it. Not vibes.

The sandbox defines where the agent can write. The approval policy determines when it must stop and ask. The network policy limits which domains it can reach. Credentials live in the OS keyring, not in environment variables. Every action leaves an audit trail because "what did the agent do and why" stops being a curiosity and becomes a compliance requirement the moment the agent touches production.

This is the boring part. And the boring part is the whole thing.

A demo works because the scope is tiny. A weekend project shipped by vibe coding has no users, no compliance burden, no blast radius. Nobody cares if it breaks.

Production agents are different. They run in environments where a wrong command can delete data, a misconfigured network policy can leak credentials, and an unlogged action can leave a security team with no way to reconstruct what happened. The stakes are not theoretical. In February, a Meta employee posted about an AI agent that autonomously deleted a large number of emails. It was working exactly as designed.

The industry is racing toward agents that do things — book flights, manage inboxes, review pull requests, deploy code. CNBC labeled it the "agentic wars." Meta and Google both entered last week. The Financial Times and Business Insider covered it. Stock prices moved.

But the companies that win this are not the ones with the flashiest demos. They are the ones that ship agents with guardrails that actually work.

OpenAI open-sourced their sandbox technology. Their internal deployment uses auto-review mode, where a subagent approves low-risk actions so the main agent keeps moving, but blocks high-risk actions for human review. They run with cached web search only, no open-ended outbound access. They pin authentication to their enterprise workspace so every action is attributable.

This is not glamorous. It will never make a YouTube thumbnail. Nobody is going to tweet "we configured our network proxy to block pastebin.com" and go viral.

But it is the difference between an agent you can trust with your infrastructure and one you cannot.

The vibe coders are not wrong. The tools are real, and they work for what they are designed to do. But "what they are designed to do" and "what production requires" are not the same thing, and pretending otherwise is how you end up with an agent that confidently does the wrong thing while the audit trail says nothing useful.

Ship the demo. Then build the guardrails. The boring stuff is the product.
