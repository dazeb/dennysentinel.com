---
title: "Vercel's eve Is a Filesystem-First Bet on Durable Agents"
description: "Vercel's new eve framework treats an agent like a Next.js app: a directory of markdown skills, TypeScript tools, and durable workflows. The interesting part is not the syntax — it is the assumption that production agents need persistence, sandboxing, and approvals by default."
pubDate: "Jul 07 2026"
heroImage: "/vercel-eve-filesystem-first-agent-framework.jpg"
---

Vercel shipped [eve](https://vercel.com/blog/introducing-eve), an open-source agent framework, on June 17, and the announcement landed with the expected "Next.js for agents" framing. After two weeks of docs, examples, and an 0.20.0 release on July 5, the shape of the bet is clearer: Vercel thinks the hard part of agent engineering is no longer prompting the model. It is everything that happens around the model — state, sandboxes, approvals, channels, and traces — and that those concerns should be file-based conventions the same way routes and pages are in Next.js.

The result is a framework where an agent is a directory tree. `instructions.md` is the system prompt. `tools/*.ts` registers functions automatically. `skills/*.md` loads playbooks on demand. `channels/*.ts` exposes the same agent on Slack, HTTP, cron, and more. Underneath it all, eve uses Vercel's Workflow SDK to make every conversation durable.

## The filesystem as the agent definition

eve's core abstraction is that an agent's structure should be visible without reading code. The canonical layout looks like this:

```text
agent/
  agent.ts                 # model, fallbacks, compaction
  instructions.md          # system prompt
  tools/
    run_sql.ts             # one TypeScript file per tool
  skills/
    revenue-definitions.md # one markdown file per skill
  subagents/
    investigator/          # delegated child agent
  channels/
    slack.ts               # surface adapters
  schedules/
    monday-summary.ts      # cron-like triggers
```

This is not a radical departure from what other agent frameworks offer. LangChain, the OpenAI Agents SDK, and others all have tools, prompts, and runtimes. What is different is the convention-over-configuration posture. In eve, the filename is the tool name. The directory name is the skill name. There is no explicit registration step because the framework owns the loop.

That design choice matters because it collapses the distance between "an agent I can run locally" and "an agent I can operate in production." The same tree that works with `eve dev` can be deployed to Vercel Functions, where Workflows handle durability and the Agent Runs tab shows every turn, tool call, and token count.

## Durable execution is not an afterthought

Most agent demos assume a warm process that stays alive for the length of the task. Production agents do not get that luxury. They wait on humans, call slow APIs, and run for hours. If a deploy lands mid-run, the agent loses its place unless something explicitly saved it.

eve addresses this by building every conversation on the open-source [Workflow SDK](https://vercel.com/docs/workflows). Each step is checkpointed. If the process restarts, the workflow replays from the last completed step. The agent can pause for human approval indefinitely without consuming compute, then resume exactly where it stopped.

This is the same durability model Vercel itself uses. The company says agents now trigger around 29% of Vercel deployments, up from less than 3% a year ago. When half your deploys come from agents, a framework that survives deploys stops being a nice-to-have.

## Sandboxing and approvals by default

The other production concern eve bakes in is isolation. Agent-generated code runs in a sandbox, not in the application runtime. The default adapter uses Vercel Sandbox in production and Docker, microsandbox, or bash locally. Because the sandbox is an adapter, you can plug in another backend, but the default makes the safe choice the easy choice.

Approvals work the same way. Any tool can declare a `needsApproval` predicate:

```typescript
import { defineTool } from "eve/tools";
import { z } from "zod";

export default defineTool({
  description: "Run a read-only SQL query against the warehouse.",
  inputSchema: z.object({ sql: z.string() }),
  needsApproval: ({ toolInput }) => estimateScanGb(toolInput.sql) > 50,
  async execute({ sql }) {
    // ...
  },
});
```

When the predicate returns true, the agent parks. No polling, no background worker, no custom approval UI in a separate repo. The framework handles the pause and resume.

## Skills, MCP, and the avoid-bloat mechanic

Skills in eve are markdown files with a `description` in frontmatter. The framework advertises each skill to the model alongside a built-in `load_skill` tool. When a request matches the description, the model loads the skill into the current turn. This keeps the context window slim until the guidance is actually needed.

For external tools, eve uses the [Model Context Protocol](https://modelcontextprotocol.io/). A connection file points at an MCP server, and eve brokers authentication so the model never sees the URL or credentials. The framework ships with adapters for Slack, GitHub, Linear, Notion, Salesforce, and Snowflake, and custom channels are a `defineChannel` call away.

The MCP integration is where eve's convention model starts to pay off. Because the framework owns tool discovery, an MCP server's capabilities slot into the same namespace as local tools. The agent does not care whether `run_sql` is a local function or a remote connector; it sees a description, calls it, and moves on.

## Self-hosting and the open-source hedge

Despite the Vercel-native defaults, eve is built on open-source SDKs and released under the Apache 2.0 license. The model routing goes through the open [AI SDK](https://sdk.vercel.ai/docs). Durable execution uses the open Workflow SDK. You can swap PostgreSQL in for the managed state backend, Docker in for Vercel Sandbox, and run the whole thing elsewhere.

That is a meaningful hedge. Vercel is obviously betting that the managed path is smoother — AI Gateway for model calls, Workflows for durability, Sandbox for isolation, and Connect for OAuth. But the framework does not require that path, which makes it viable for teams who want Vercel's conventions without Vercel's platform.

## The real bet: agents have a shape

Vercel's argument is that every generation of software eventually earns its framework once enough people build the same thing by hand. Agents, the company claims, are at that point. The problems repeat across projects: state, sandboxing, approvals, channels, traces, evals. eve says those should be conventions, not code.

The counterargument is that agents are still too heterogeneous to standardize. A customer-support agent, a coding agent, and a data-analyst agent have very different tool sets, latency requirements, and failure modes. A directory layout cannot capture all of that.

eve's response is to keep the conventions shallow. It does not prescribe what your agent does. It prescribes where you put the pieces. That is a smaller claim than "one framework for every agent," and it is probably the right one. If the location of the instructions, tools, and skills becomes standard, the rest of the ecosystem can build around it.

## What to watch

Two things will determine whether eve becomes a standard or stays a Vercel-internal convenience.

First, the harness ecosystem. Vercel's own [AI SDK 7](https://vercel.com/blog/ai-sdk-7) adds `HarnessAgent`, which wraps Claude Code, Codex, Deep Agents, OpenCode, and Pi behind a common interface. If those harnesses start producing eve-compatible directory layouts, the framework becomes an interoperability layer rather than a silo.

Second, the self-hosted story. eve works without Vercel today, but the managed path is clearly the happy path. If Docker-based local development and PostgreSQL-backed durability remain first-class, teams with compliance or latency constraints will adopt it. If they drift behind the managed features, eve will be a Vercel-only framework with an escape hatch that rusts shut.

The bottom line is that eve is not a model release. It is an infrastructure release dressed as a developer framework, and that is exactly where the interesting work in agents is happening right now. The model layer keeps improving, but the difference between a demo and a production agent is everything else. Vercel is betting that "everything else" can be a directory tree.
