---
title: "Alibaba Cloud Just Rebranded Cloud Infrastructure for the Agent Era"
description: "At WAIC 2026, Alibaba Cloud launched Agent Native Cloud — a full-stack platform with Agent Teams multi-agent orchestration, Agentic Computer sandboxing, and a Skills portal, reimagining cloud infrastructure around AI agents as first-class citizens."
pubDate: "Jul 19 2026"
heroImage: "/alibaba-agent-native-cloud-waic-2026.jpg"
---

# Alibaba Cloud Just Rebranded Cloud Infrastructure for the Agent Era

On July 18 at the [World Artificial Intelligence Conference (WAIC)](https://www.worldaic.com.cn/) in Shanghai, Alibaba Cloud did something that, on its face, sounds like marketing copy: it launched **Agent Native Cloud**, a full-stack cloud platform built from the ground up for AI agents. But the details reveal something more structurally significant than a rebranding exercise.

## The Three Pillars: Run, Teams, Loop

Qi Zhou, head of Alibaba Cloud's Cloud-Native Application Platform, introduced the platform with three core components that together define what "agent-native" means in practice:

**Agent Run** is the runtime layer — secure isolation sandboxes for agent execution, an Agentic File System (Agentic FS) purpose-built for agent workloads, and lifecycle management infrastructure that treats agent processes as first-class cloud citizens rather than glorified serverless functions. This is the layer that answers "where does the agent actually execute, and what guarantees does it get?"

**Agent Teams** handles multi-agent orchestration — identity integration so agents can authenticate across cloud services without leaking credentials, coordination primitives for agent-to-agent communication, and workload distribution that understands agent dependencies (an agent that needs to call an API, write to object storage, and cache results in Redis should not have to manage three separate access policies manually).

**Agent Loop** is the feedback layer — monitoring, evaluation, and continuous improvement infrastructure. Agents publish outcomes; the platform measures them; the loop feeds back into agent behavior. This turns agent deployments from "deploy and pray" into observable, improvable systems.

## Agentic Computer: Sandboxing as Infrastructure

A standout announcement was **Agentic Computer** — a secure, disposable execution environment for agents. The problem this solves is well-known to anyone running agents in production: agents need to execute arbitrary code, browse the web, and call APIs, but giving them unfettered access to production infrastructure is a liability.

Agentic Computer provides ephemeral sandboxes with network policies, filesystem isolation, and credential scoping built in. The platform handles sandbox lifecycle — spin up, execute, tear down — without the agent's author needing to write a single line of security configuration. This is the kind of infrastructure that the [MCP specification's security model](https://aaif.io/blog/mcp-is-growing-up/) has been calling for, and Alibaba Cloud is the first major cloud provider to ship it as a native platform capability rather than an add-on.

## The Skills Portal: Cloud APIs Become Agent Tools

Alibaba Cloud also launched a [Skills portal](https://www.alibabacloud.com/en/press-room/alibaba-cloud-unveil-advanced-agentic-ai-ecosystem) that converts common cloud capabilities into reusable, MCP-compatible agent tools. Instead of writing custom API wrappers for every cloud service an agent needs to call, developers publish a skill once — defining the tool's schema, authentication requirements, and execution policy — and any authorized agent can discover and invoke it.

This is a direct parallel to the [MCP Apps capability](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) in the forthcoming MCP 2026-07-28 spec, where servers can expose renderable UI components to agents. The convergence is telling: both the protocol layer (MCP) and the infrastructure layer (Alibaba Cloud) are converging on the idea that agent-tool interactions should be discoverable, authenticated, and governed at the platform level, not hacked together per-agent.

## Why "Agent Native" Matters

The term "agent-native" versus "AI-native" is not semantic hair-splitting. AI-native cloud (what AWS, GCP, and Azure have been building) optimizes for model training and inference — GPU clusters, vector databases, model registries, and ML pipelines. Those workloads are fundamentally request-response: submit a batch, wait for training, serve the model.

Agent workloads are fundamentally different. Agents loop: perceive, reason, act, perceive again. They maintain state across turns. They call multiple tools in sequence, conditionally branch based on results, and can run for hours or days. An agent's execution profile looks more like a distributed transaction than an API request.

The [Omdia Market Radar report](https://www.alibabacloud.com/blog/602967) that named Alibaba Cloud a Leader in "Agentic AI Cloud Titans in Asia & Oceania, 2026" identified native agent support as a key evaluation criterion. Alibaba Cloud's announcement gives them a concrete offering to point to.

## Context: This Is Not a First Mover, but a Fast Follower

Alibaba Cloud is not the first to the "agent-native cloud" label. [Daytona Cloud](https://www.daytona.io/) launched in May 2026 with sub-100ms sandbox creation and agent-native Docker environments. Sealos introduced [Seakills](https://www.linkedin.com/posts/sealos_github-labringseakills-ai-agent-skills-activity-7455503795301691392-WKEL) for agent-native deployment in April 2026. And [Huawei Cloud](https://cryptobriefing.com/alibaba-cloud-launches-agent-native-cloud-to-scale-enterprise-ai-agents/) announced new agent programs at the same WAIC 2026 event.

What makes Alibaba's entry significant is scale. As the largest cloud provider in Asia-Pacific, Alibaba Cloud can make "agent-native" infrastructure accessible to the enterprises that are currently running agents on general-purpose VMs and hoping nothing breaks. The Skills portal, in particular, lowers the barrier: an enterprise team that already uses Alibaba Cloud can make its agents discover and invoke cloud services without writing custom integration code for every service.

## What to Watch

Three things to track in the coming months:

1. **Adoption velocity.** How many enterprise teams actually migrate agent workloads from generic compute (ECS, Serverless) to Agent Run sandboxes? Platform-native features only matter if teams use them.

2. **MCP compatibility depth.** The Skills portal claims MCP compatibility, but the MCP 2026-07-28 spec releases in [nine days on July 28](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/). Alibaba Cloud's timeline for full stateless-protocol compliance will determine whether the Skills portal is genuinely interoperable or a walled garden in MCP clothing.

3. **Competitor response.** AWS, GCP, and Azure have all invested heavily in AI-native infrastructure. None has yet announced an equivalent agent-native runtime layer. If agent workloads continue their current growth trajectory, the silence will not last.

## The Bottom Line

Alibaba Cloud's Agent Native Cloud is the most concrete signal yet that the cloud industry recognizes agents as a fundamentally new workload class. The three-pillar architecture — runtime, orchestration, feedback — and the emphasis on sandboxed execution and reusable skills provide a reference model that other providers will have to answer to.

The category is real. The question is whether the infrastructure will arrive fast enough for the agents that are already being built on top of it.
