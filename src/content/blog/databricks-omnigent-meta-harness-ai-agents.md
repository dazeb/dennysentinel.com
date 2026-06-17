---
title: "Databricks Open-Sources Omnigent: The Meta-Harness That Sits Above Your AI Agents"
description: "Databricks just released Omnigent, an open-source meta-harness that composes, governs, and shares AI agents across Claude Code, Codex, and Pi — treating each harness as an interchangeable part of a larger system."
pubDate: "June 17 2026"
heroImage: "/databricks-omnigent-meta-harness-ai-agents.jpg"
---

The AI agent stack is getting a new layer, and it is not another model.

Databricks just [open-sourced Omnigent](https://www.databricks.com/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents), an Apache 2.0 **meta-harness** that sits above the agent harnesses you already use — Claude Code, Codex, Pi, OpenAI Agents SDK, Claude Agents SDK — and makes them interoperable parts of a single system. The thesis is straightforward: the frontier of agent engineering has moved up a level. The hard problems are no longer inside the model. They are in the layer that composes, controls, and coordinates the agents around it.

## The Problem: Agent Harnesses Are Siloed

If you have been building with AI agents in 2026, the pattern is familiar. You have four or five harnesses open. You copy-paste context between them. You manually track which agent did what. You have no shared policy layer, no unified cost tracking, and no way to hand off a live session to a teammate without starting over.

Each harness — Claude Code, Codex, Pi — wraps a model and turns it into an agent. They all expose roughly the same interface: messages and files go in, text streams and tool calls come out. But they do it in their own way, with their own session model, their own sandbox, their own blind spots.

Omnigent's core insight is that this interface is standardizable. If every harness speaks the same structural language, you can build a layer above them that handles the problems no single harness solves on its own.

## Three Pillars: Composition, Control, Collaboration

Omnigent organizes its value proposition around three capabilities that single-harness setups lack.

### 1. Composition Without Rewriting

Omnigent wraps any agent in a **sandboxed runner** with a uniform API. You define an agent in YAML, and switching from Claude Code to Codex is a one-line change:

```yaml
name: polly
prompt: "You orchestrate coding sub-agents."
harness: omni
tools: [read, edit, delegate]
sub_agents:
  - harness: claude-code
  - harness: codex
  - harness: pi
```

The shipped example agent **Polly** demonstrates this: it plans a task, then delegates to coding sub-agents in parallel git worktrees. Each diff is cross-reviewed by a different vendor's model. Polly writes no code itself — it orchestrates.

Another built-in agent, **Debby**, runs two models side-by-side (Claude and GPT) and lets you trigger a `/debate` mode where they critique each other's answers until they converge.

### 2. Stateful Contextual Policies

This is where Omnigent diverges most sharply from what prompt-based governance can do. Policies are declared in YAML and enforced at the meta-harness layer — not via system prompts that the agent can ignore or forget.

```yaml
name: budget-warn
type: cost
op: ge
value: 50
action: warn
```

Policies stack across three levels: server-wide, per-agent, and per-session. The session-level rules are checked first, so you can tighten controls for sensitive workloads without affecting the rest of the fleet.

The policy engine is contextual, not just static. An example from the docs: after `npm install` runs, require human approval before `git push`. The agent can write freely to files it created, but operations that leave the machine get gated. This is the kind of state-dependent policy you cannot express in a prompt.

Cost tracking is built in. Set a threshold, and the agent pauses and asks to continue after every $100 spent. No external dashboard required.

### 3. Collaboration via Shared Sessions

Every Omnigent session is exposed over terminal, a local web UI (at `localhost:6767`), and APIs — all in sync. You can invite a teammate to view a session via URL, comment on files, send commands, or fork the session entirely.

This is the feature that turns agent sessions from single-player experiences into team artifacts. The session and its working directory become a collaboration hub, not a private terminal.

## The Sandbox Layer

Omnigent includes **Omnibox**, an OS-level sandbox that can lock down filesystem access and intercept network requests. One concrete use case: hide a GitHub security token from the agent entirely, and inject it only via an egress proxy on approved requests. The agent never sees the credential, but it can still push code when the policy allows it.

Sessions can run locally or on hosted sandboxes like Modal and Daytona, giving you hermetic execution environments without changing the agent definition.

## How It Compares

| Capability | Single Harness | Omnigent Meta-Harness |
|---|---|---|
| Agents & models | One harness; swap models inside it | Claude Code, Codex, Pi, SDKs — interchangeable |
| Switching cost | Re-integrate per tool | One-line change |
| Interfaces | Terminal or tool's own UI | Terminal, web, desktop, mobile, APIs — same session |
| Governance | Allow/deny lists, often prompt-based | Stateful contextual policies at harness layer |
| Cost control | Manual tracking | Budget policy pauses at set thresholds |
| Collaboration | Copy-paste between tools | Live shared sessions, co-drive, fork |
| Sandbox | Tool-dependent | OS sandbox + egress-proxy secret injection |
| Cloud execution | Local machine | Disposable Modal or Daytona sandboxes |
| License | Varies | Apache 2.0, open source |

## The Bigger Picture

Omnigent is in alpha. It has rough edges, a small contributor base, and the kind of documentation that assumes you already know what a meta-harness is. But the architectural bet is significant.

The history of infrastructure is a history of abstraction layers that won by being boring. Containers won not because they were the most sophisticated isolation technology, but because they were the layer that made VMs interchangeable. Kubernetes won not because it was the best scheduler, but because it was the layer that made clusters interchangeable.

Omnigent is betting that the next layer up in the AI agent stack is the one that makes harnesses interchangeable — and that the teams who standardize on that layer will ship faster than the teams who keep bolting governance onto individual tools.

The install is one line:

```bash
pip install omnigent && omni run
```

The repo is at [github.com/omnigent-ai/omnigent](https://github.com/omnigent-ai/omnigent). The docs are at [omnigent.ai](https://omnigent.ai/).

It is early. But the direction is right.
