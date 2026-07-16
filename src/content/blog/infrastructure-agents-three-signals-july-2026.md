---
title: "Three Signals This Week That Infrastructure Must Be Rebuilt for Agents"
description: "Meta's infrastructure VP, the Kubernetes SIG Apps maintainers, and an industry analyst all said the same thing in the same week: execution infrastructure designed for stateless HTTP requests breaks under agent workloads. Here is what each signal says and why they converge."
pubDate: "Jul 16 2026"
heroImage: "/infrastructure-agents-three-signals-july-2026.jpg"
---

Three independent sources published essentially the same argument in the same week. A Meta VP telling a conference audience the company has maybe 20 months to rebuild its infrastructure. The Kubernetes SIG Apps maintainers shipping a new abstraction because Pods do not fit agent workloads. An InfoWorld analyst laying out the four capabilities agent execution requires that Kubernetes does not provide.

Each source approaches the problem from a different vantage point — a hyperscaler infrastructure operator, an open-source platform community, and an industry analyst tracking patterns across hundreds of deployments. The fact that all three land on the same diagnosis in the span of 72 hours is the signal worth reading.

Here is what each one says, and why their convergence matters more than any single argument.

## Signal 1: Meta's three assumptions are breaking at once

At VB Transform 2026 on July 15, Meta VP of Engineering Barak Yagour told the audience that agentic queries hitting Meta's data systems grew **30x in a single half**. That growth is breaking three assumptions the company spent two decades building around.

**Capacity.** The old mental model was linear: one engineer generates one unit of system load. That model is gone. Yagour put the new math bluntly: "One engineer used to mean one unit of load. Now one engineer spawns 10 agents, each spawning subagents. Your 1,000-person org can generate the load of 100,000 users practically overnight."

The load multiplication is not a Meta-specific phenomenon. Automated traffic overtook human traffic on the internet last year at 51% of the total (Imperva 2025 Bad Bot Report), and agent traffic is growing roughly **eight times faster** than human traffic (HUMAN Security 2026 State of AI Traffic report). Yagour cited both figures to ground the argument: this is not a Meta data center problem; it is an industry-wide pattern that arrived faster than anyone prepared for.

His recommended response is not to block agent traffic but to make infrastructure agent-aware — dynamic controls that understand agent hierarchies, cost attribution that traces consumption back to the use case that spawned it, and throttling that adapts based on priority rather than a flat rate limit.

**Identity.** An agent does not fit the categories infrastructure teams built access controls around. It is not a human user (no badge, no login ceremony, no manager who approved its access). It is not a deployed service (no fixed API contract, no predictable call pattern, no pre-scoped permissions). Yet it makes autonomous decisions that touch data systems, write to databases, and trigger production workflows. Current identity systems have no slot for this category, which means agents either get over-privileged (attached to a human's credentials) or under-scoped (blocked from doing useful work).

**Velocity.** Yagour cited GitHub Copilot's 46% code authorship rate, then noted the follow-on problem: "That code still needs to be built, tested, deployed, monitored. The agent writes the code in seconds, but your CI/CD pipeline doesn't get faster just because the machine is the author."

Faster code generation shifts the bottleneck from writing code to every step after it. If your build takes 12 minutes and your deploy runs once an hour, an agent that writes code in three seconds does not change your latency to production — it just makes the wait more frustrating.

Yagour closed with the timeline that makes the argument urgent: "We spent 20 years building infrastructure for humans. We have maybe 20 months to rebuild the whole thing for a world where humans and agents co-create at scale. The window is open, but it won't stay open for long."

## Signal 2: Kubernetes needs a new abstraction for agents

On July 14, the team behind kagent published a post on the CNCF blog asking a question that would have seemed heretical two years ago: **Is a Pod the right deployment unit for an AI agent?**

The kagent team started the way most agent platform projects do — running multiple agents inside a single runtime. As the number of agents grew, fundamental questions emerged: how do you isolate one agent from another? How does each agent get its own identity? How do you enforce network policies per agent? "These aren't Kubernetes questions," the post notes. "They're agent platform questions."

Their first answer was straightforward: run every agent in its own Pod, Service, and ServiceAccount. Pods provide process isolation. ServiceAccounts give each agent identity. Existing network policies, admission controllers, and security controls work without modification. Observability systems can attribute metrics to individual agents.

That worked, for a while. Then the mismatch became impossible to ignore.

Agents are fundamentally different from microservices. Most services are expected to be continuously available. Agents are not — they wake up when a task arrives, execute for seconds or minutes, then go idle. Running a dedicated Pod for every dormant agent is wasteful. Agents spawn subagents dynamically, pause for human approval, impersonate users, and have lifetimes measured in minutes rather than days.

The team's answer is **agent-substrate** — an additional control plane above Kubernetes. Instead of treating every agent as a first-class Kubernetes workload, Kubernetes manages a fixed number of execution Pods (Workers), while agent-substrate manages a much larger number of logical agents (Actors) that share those workers.

The critical design insight: **Pods become execution workers, not the deployment model for agents.** An Actor is a logical entity scheduled onto a Worker when work arrives and removed when execution completes. Identity, security policy, and observability follow the logical Actor, not whichever Pod happened to host it at a given moment.

This matters because the distinction is structural, not just operational. If you tie an agent's identity to a Pod, you cannot recover it after the Pod is evicted. If you tie security policy to a Pod's ServiceAccount, you have to re-express that policy every time the agent moves. The questions multiply: Who owns an Actor? How do quotas work across teams when execution is no longer one-to-one with Pods? What does observability look like when traces span Workers?

These are open questions. The fact that the Kubernetes community is building dedicated infrastructure to answer them — rather than recommending teams compose solutions from existing resources — is itself the clearest acknowledgment that agent execution does not fit the old model.

## Signal 3: The four things agent execution requires that Kubernetes cannot provide

On July 16, InfoWorld published an analysis that synthesizes the operational experience of teams running agents at scale. The piece identifies four capabilities that execution infrastructure must provide for agent workloads, none of which map cleanly onto Kubernetes primitives.

**Millisecond environment provisioning.** An agent's reasoning loop stalls if it has to wait 45 seconds to two minutes for a sandbox. The difference between a two-second cold start and a two-minute cold start is not a performance optimization; it determines whether the architecture is viable for interactive use. Perplexity's SPACE platform (detailed in a separate technical report this week) achieves median sandbox creation of 60ms — roughly **50x faster** than a well-tuned Kubernetes cluster.

**Durable state management.** Agents accumulate context across long sessions. They pause, hand off subtasks, and resume. Every re-initialization burns tokens reconstructing context the agent already built. The execution layer needs to provide state continuity that survives Pod evictions, network interruptions, and tool failures.

**Coordination primitives.** Production agent systems are not single agents; they are pipelines of specialized agents with handoffs that need to be reliable and inspectable. Spawning subagents, passing structured outputs between them, and tracking task dependencies across concurrent processes requires coordination infrastructure that the request-response model never needed.

**Session-scoped credentials.** An agent holds different credentials than the user who spawned it, and those credentials change as the agent accesses different systems during a task. Standard container-level secret management (mount a volume at startup, done) does not work when the agent creates new sandboxes dynamically or hands off context to a subagent.

The article cites CAST AI's 2026 State of Kubernetes Optimization Report for the cost side of the mismatch: across 23,000 production clusters, average CPU utilization sits at **8%**, down from 10% the prior year. CPU overprovisioning jumped from **40% to 69%** year over year. Agent workloads compound this: an agent holding an open inference connection or waiting on a tool call registers as idle to a scheduler reading CPU and memory. The infrastructure overprovisions for demand it cannot measure, while the actual bottleneck — environment provisioning latency and state continuity — goes unaddressed.

## Why the convergence matters

Three different sources, published within 72 hours of each other, from three different institutional perspectives, all diagnosing the same structural gap.

- **Meta's Yagour** describes the problem from the hyperscaler operator perspective: the load model is inverted, identity categories no longer fit, and the velocity bottleneck has shifted.
- **The kagent team** describes the problem from the platform engineering perspective: Pod-level abstractions break for agents, and a decoupled control plane is necessary.
- **The InfoWorld analysis** describes the problem from the industry patterns perspective: four concrete capabilities that agent execution needs, none of which the stateless-service model provides.

The convergence itself is the story. When a hyperscaler infrastructure VP, an open-source Kubernetes project, and a cross-industry analyst all publish the same diagnosis in the same week, the pattern is not speculative. It is an industry-wide recognition that the compute model underpinning most of the last decade's infrastructure decisions no longer fits the workloads being built today.

The timeline Yagour gave — 20 months — may be optimistic for some organizations and pessimistic for others. But the direction is settled. Execution infrastructure designed for stateless HTTP requests does not work for agent workloads. Teams that recognize this and start rebuilding their execution layer now will have a meaningful structural advantage. Teams that wait for the abstractions to stabilize will spend 2027 and 2028 wondering why their agent systems are unreliable at a scale that should be tractable.
