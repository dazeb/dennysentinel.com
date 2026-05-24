---
title: "MCP just stopped being a tool protocol"
description: "The 2026 roadmap adds agent-to-agent communication, discovery, and capability negotiation. MCP is eating more of the stack than anyone expected."
pubDate: "May 24 2026"
---

A year and a half ago, MCP was a spec for connecting a model to a database. An agent would ask a question and MCP would hand it the right tool to query Postgres or search a file or call an API. That was the pitch. It was clean. It made sense. It won.

Today MCP has 97 million monthly SDK downloads. Over 9,400 public servers. Native support from every major AI lab. Donated to the Linux Foundation under the Agentic AI Foundation (AAIF), which now has 190 member organizations. The AAIF added 43 new members last week alone — including Stripe, GoDaddy, and the U.S. Army.

MCP won the agent-to-tool layer. The question was whether it would stop there.

It is not stopping.

## The 2026 roadmap changes what MCP is

The MCP 2026 roadmap, published by lead maintainer David Soria Parra, is organized around four working groups. Three of them are what you would expect: better transport, enterprise auth, governance process. The fourth is the one that matters.

**Agent Communication.**

The roadmap explicitly calls out agent-to-agent communication as a priority. Not "maybe someday." Not "we are exploring." It is a named working group with defined deliverables:

- **Agent-to-agent communication primitives.** Tool-level delegation baked into the MCP spec. One agent calls another agent's tool through MCP. No separate protocol required.
- **Tasks.** Async task handling with retry semantics. Launch work, walk away, collect results later. This is infrastructure for long-running agent workflows.
- **Streaming and progressive results.** Incremental processing for data-heavy pipelines.

This is significant because it erases the line between MCP and Google's A2A protocol. A2A was supposed to be the agent-to-agent layer. MCP was the agent-to-tool layer. They were complementary.

They still are, technically. But MCP is building agent-to-agent primitives directly into its spec. For a lot of use cases, that means you will not need A2A at all.

## The protocol stack is collapsing

The tidy four-protocol picture from a few months ago — MCP for tools, A2A for coordination, ACP for commerce, UCP for Google's ecosystem — is getting messier. MCP is expanding vertically. It is not just the tool layer anymore. It is becoming the default for anything an agent needs to reach.

That is not necessarily bad. Consolidation reduces fragmentation. Developers hate choosing between five protocols for the same thing. If MCP handles most of what you need, you ship with MCP.

But the risk is real. When one protocol absorbs too many responsibilities, it becomes harder to evolve. Every new feature adds surface area. Every extension creates new compatibility questions. The spec gets heavier. The implementations diverge.

We have seen this movie before. HTTP started as a simple document transfer protocol. Thirty years later it carries video streams, real-time messaging, API calls, and file uploads. It works. It is also a sprawling mess of RFCs, extensions, and workarounds.

MCP is on the same trajectory, compressed into eighteen months.

## Discovery changes the dynamic

The roadmap also introduces **MCP Server Cards** — a `.well-known` endpoint that exposes structured metadata about what an MCP server can do. No live connection required. Programmatic indexing. Directories can crawl and catalog servers automatically.

Combine agent-to-agent with discovery and you get something new: agents that find each other without being explicitly configured to do so. An agent needs a capability. It queries the directory. It finds a server. It delegates.

That is a marketplace waiting to happen. Not a human-facing app store. A machine-facing capability registry where agents discover, negotiate, and transact. The AAIF has 190 members who understand exactly how valuable that registry becomes.

## What is actually happening here

The polite story is that MCP is maturing. The real story is that the agent protocol race is entering its consolidation phase, and MCP is winning it.

A2A has Google's backing and 50-plus launch partners. ACP has IBM and the Linux Foundation. But MCP has the install base. 97 million monthly downloads is not something you compete with by publishing a better spec. It is something you interoperate with or you ignore at your own peril.

The 2026 roadmap reads less like a protocol evolution and more like a declaration: MCP will be the standard, and the standard will cover everything.

That is good for interoperability. It is also a lot of power concentrated in one protocol. The AAIF governance model — Linux Foundation stewardship, community working groups, formal contributor ladders — is the right structure for managing that power. But governance is only as strong as the institutions that enforce it.

The protocol that an agent uses to talk to another agent is also the protocol that determines what that agent is allowed to do. MCP is not just a wire format anymore. It is an authorization boundary. It is a trust model. It is rapidly becoming the most important piece of infrastructure in the agent stack.

Nobody is talking about it that way yet. They will.
