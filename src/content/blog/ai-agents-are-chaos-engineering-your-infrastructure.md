---
title: "AI agents are chaos engineering your infrastructure right now"
description: "79% of orgs run agents in production. Zero of them track the outages agents cause."
pubDate: "May 25 2026"
heroImage: "/ai-agents-chaos-infra.jpg"
---

There is a category of production incident that engineering teams are not tracking yet. It does not fit any existing postmortem template. The root cause field says "connection pool saturation" or "cascading restart." The initiator is invisible.

It was an AI agent.

Seventy-nine percent of organizations now run autonomous agents in production. Ninety-six percent plan to expand. Gartner says a third of enterprise software will include agentic AI by 2028 — and that 40% of those projects will be canceled due to poor risk controls.

Between those numbers is a blind spot nobody is talking about.

## The incident you cannot classify

Current incident frameworks treat agent failure and infrastructure failure as separate disciplines. One team handles model reliability. Another handles SRE. When an agent makes a bad decision, it is an AI problem. When a service goes down, it is an ops problem.

This separation does not survive contact with production.

Here is what actually happens. A remediation agent detects elevated latency on a microservice. Its training says: restart the cluster. The action is technically correct given the narrow context it was given. But the agent does not know three things.

Three other services are handling peak traffic. The shared connection pool is at 87% utilization. A dependent database is running a background index rebuild.

The restart fires. The recovering service gets hit by a thundering herd from everything downstream. The cascade takes out the full stack.

The postmortem gets filed under "service restart" or "connection pool exhaustion." The agent is never named. It was just doing its job.

## Every autonomous action is a chaos event

Mature chaos engineering programs rely on a human making a judgment call before any experiment. Someone checks the dashboards, the error budget burn rate, the dependency stability. Only then do they pull the trigger.

When you introduce an autonomous remediation agent, that question disappears. The agent sees an anomaly. The agent takes an action. The action is a chaos event.

Nobody planned for it. Nobody calculated the blast radius. Nobody checked whether the system could absorb the stress.

Reported AI-related incidents rose 21% from 2024 to 2025. That number is almost certainly understated, because agents are not classified as the initiating cause in most incident databases. The failures are real. The attribution is wrong.

## The missing concept: absorb capacity

The core gap is that enterprise systems have no shared concept of absorb capacity — the real-time estimate of how much additional stress a system can take before it breaches its SLOs.

Human-led chaos programs manage this implicitly. An experienced SRE looks at a dashboard and knows, without calculating it, that now is a bad time to mess with the payment service. Agents do not have that intuition. They have a threshold and a playbook.

What is needed is a resilience budget — a continuously recomputed, consumable resource that every agent action draws from. The budget is built on four live signals:

- SLO burn rate
- P99 latency trend direction over the last 40 minutes
- Dependency saturation state
- Application behavioral signals

Without a shared ledger, multiple teams and agents can collectively produce a blast radius no one planned.

## LLMs are not the fix

LLMs can help generate chaos hypotheses from dependency graphs. They can surface plausible failure modes faster than manual processes. That is useful.

They cannot make execution decisions when signals are ambiguous. That judgment requires information outside any monitoring system: pending deployments that change topology, known fragile dependencies, the fact that the DBA is running a migration and asked everyone to stay off the database for twenty minutes.

The model will be confidently incorrect about a system boundary that no longer exists. In chaos engineering, that means an unplanned outage. The dependency graph is stale. The model does not know it. The agent acts anyway.

## What changes

The first step is classification. If an agent initiated an action that changed infrastructure state and an incident followed, the agent goes in the root cause field. Not the symptom. The agent.

The second step is shared state. Every agent that can touch infrastructure needs to know the current absorb capacity before it acts. That means a single source of truth for system stress that agents query before making changes — the same way a human SRE checks dashboards before a planned experiment.

The third step is blast radius simulation. Before an agent restarts a service cluster, it should estimate what else breaks. That simulation will be wrong sometimes. It will still be better than not simulating at all.

None of this is a reason to stop deploying agents. Autonomous remediation is going to happen regardless. The question is whether we track the damage it causes or pretend the postmortem template still works.

Right now, we are pretending.
