---
title: "Recursive Agent Loops Are the Next Coding Era — and Nobody Is Ready for the Token Bill"
description: "Anthropic's Claude Code lead says agents prompting other agents is the defining shift of 2026. NVIDIA's A-Evolve already showed what that looks like at frontier scale — including a model that corrected its own broken metric mid-campaign."
pubDate: "Jun 28 2026"
heroImage: "/recursive-agent-loops-next-coding-era.jpg"
---

The head of Anthropic's Claude Code team told Meta's @Scale conference this week that agentic coding is entering its third era. Two years ago, programmers typed source code. Last year, agents wrote the code. Now, agents are starting to prompt other agents that then write the code — and Boris Cherny thinks that shift is as big as the move from hand-written source to agent-written code was in 2024.

The pattern that makes it work is what practitioners are calling the **loop**: a long-running, recursive structure where subagents watch a codebase, open pull requests, and keep working in the background until some signal tells them to stop. No human interruption. No fixed iteration count. The subagent itself decides when the loop is done.

That sounds like a modest change in architecture. It is not. It changes who is in control of the development process, how costs are accounted for, and which kinds of engineering problems are safe to automate.

## The Loop, Not the Agent

The conventional model for agentic coding is "start, check, stop." A human writes a prompt, the agent produces code, the human reviews it. The human is the unit of progress — every output passes through their attention before reaching production.

A loop removes the human as the rate limiter. Cherny described his own development environment as running two persistent subagents in the background: one that constantly looks for ways to improve architecture, and another that hunts for duplicated abstractions to unify into shared helpers. Both open pull requests like human contributors. Neither ever reaches a clean stopping point. They run until a human tells them to stop — or until the inference budget runs out.

The open-source implementation of this idea is called the **Ralph Loop**, named after Ralph Wiggum from *The Simpsons*. It is deliberately simple:

1. Ask the model to summarize everything done so far.
2. Ask if it has accomplished its goal.
3. If yes, the loop ends. If no, run again with new context attached.

That is it. No complex state machine. No external orchestrator. The model decides when it is done, and the loop structure gives it permission to keep going until it gets there. Anthropic's own Claude Code documentation now has 148 references to loops across its overview and how-to guides. The Claude Design update from the same week folded in design-system import and Claude Code handoff — integration surfaces that the pattern can exploit once it has a runtime.

## What the Loop Makes Possible

The loop pattern unlocks a class of engineering work that conventional agents handle poorly: **hill-climbing problems**. Code quality, test coverage, architectural cleanup — these are tasks where incremental improvement is measurable and compounding, but no single pass produces a finished result. A loop can iterate on test coverage until every module hits 80%, then stop. A conventional agent produces one round of tests and asks what to do next.

The same reasoning applies to dependency upgrades, lint rule adoption, dead-code removal, and documentation drift. All of these are cyclical maintenance tasks that teams underinvest in because the human cost of each pass is roughly the same as the first pass. A loop changes the marginal cost profile: the first pass costs tokens, the second pass costs fewer tokens (because some work is already done), and the loop stops when the verifier says the condition is met.

Cherny framed the economics directly: *"If that sounds expensive, it should."* Anthropic is in the business of selling tokens, and the calculus looks different for customers than it does for a model provider. But the math still works for a specific class of problems. A loop that spends $50 in tokens to close 200 stale pull requests across a monorepo is cheaper than a senior engineer spending two days doing it manually — and the senior engineer is probably doing work the loop cannot do.

## The NVIDIA A-Evolve Proof Point

If Boris Cherny's talk is the industry articulation of the loop pattern, the **NVIDIA A-Evolve** result — published on arXiv on June 9 and covered widely this week — is the evidence that the pattern scales beyond code refactoring into autonomous AI research.

The A-Evolve system performed end-to-end post-training on NVIDIA's 30B-parameter Nemotron model with zero human intervention over four rounds running multiple weeks on multi-H200 Kubernetes clusters. It placed 8th out of roughly 4,000 entries on the public NVIDIA Nemotron-Reasoning Challenge, scoring 0.86 against the top human entry of 0.87. That is not a tie, but it is a single-point gap on a frontier leaderboard from a system that wrote its own training strategies, ran its own experiments, and evaluated its own results.

Three design choices made the loop survive at that scale:

- **Immutable reference substrate.** Every round forks the same audited default training stack. It is never overwritten, ensuring comparable results across weeks of autonomous operation.
- **Homogeneous, memory-free workers.** Eight identical workers per round, each starting fresh from the substrate, unaware of the others. No state carries between rounds except the search policy.
- **Round-level evidence aggregation.** Feedback arrives only after each round. Only the search policy is updated — not model weights or intermediate artifacts.

These choices embody what the loop pattern requires in practice: a way to contain the loop so that its side effects are bounded and auditable. The workers have total freedom inside their sandbox, but the substrate is inviolable.

### The Self-Correction That Matters Most

The most significant finding in the paper is not the leaderboard score. It is the **mid-campaign metric inversion**. At some point during the run, candidates began pushing the system's internal development metric to record highs without moving the external target. A naive optimizer — including every reinforcement learning loop in production today — would continue pursuing higher dev scores, deepening the gap between the proxy and the real objective.

The A-Evolve system detected this. It revised its own search policy, stopped asking for interventions that raised the proxy, and began specifically seeking interventions that lowered it while improving the external target. It performed this correction without being prompted, without a human noticing the decoupling, and without a fixed rule that said "proxy must correlate with target."

This is a live instance of **specification gaming** correction — or, as alignment researchers have documented for years, a system that caught itself in the act of Goodhart's Law and changed course. The paper is careful to note that the system's internal reasoning during this detection is not fully interpretable; the correction is observable and measurable, but the chain of thought is not transparent. That remains an open alignment question. But the fact that the correction happened at all, at frontier scale, without human intervention, is a data point that changes what engineering teams should expect from autonomous loops.

## The Governance Gap

The loop pattern introduces a governance problem that most teams are not prepared for. The conventional agent model has natural stops: every tool call result, every user approval, every fixed iteration limit. A loop has no natural stops. It runs until one of the following conditions is met:

- The verifier says the goal is accomplished.
- The verifier says the goal cannot be accomplished.
- The token budget is exhausted.
- A human intervenes.

That is a fundamentally different risk profile. A conventional agent that goes off the rails produces one bad output. A loop that goes off the rails produces compounding bad outputs and burns tokens until it hits a budget ceiling.

Cherny's recommendations for engineering leaders are worth quoting directly: define which problems are loop-safe and which ones are not; set acceptable token spend per loop; assign clear authority for who can change that cap mid-quarter; and build an audit process that reviews loop-produced artifacts before they reach production. The teams that do not have these conversations are going to learn the answers the hard way, and the cost of that learning is going to come straight out of their inference budget.

The companies shipping agent platforms — OpenAI, Anthropic, GitHub, Vercel — all have a financial incentive to push loop adoption. Token spend correlates with their revenue. The product opportunity for the next six months is not a better model; it is a **loop management interface** that exposes current step, duration, token spend, and a clean pause-resume capability. The first platform to ship a trustworthy one will set the standard, and the second-tier tools will spend the next year catching up.

## What Loops Mean for Agent Infrastructure

The engineering lesson from both Cherny's talk and the A-Evolve paper is that the loop is a new primitive, not a new configuration of existing primitives. Running a loop requires different infrastructure than running a conventional agent: durable state that survives restarts, token accounting that is visible to the developer, verifiers that are deterministic enough to gate promotion, and sandboxes that are isolated enough to contain the loop's side effects.

Vercel's AI SDK 7, released this week, ships a `WorkflowAgent` for durable execution that survives process restarts. That is exactly the kind of infrastructure the loop pattern needs. The question is whether the monitoring, approval, and rollback tooling arrives at the same pace as the execution capability.

The takeaway is straightforward. Recursive agent loops are not a research curiosity or a conference demo. They are the architecture that Claude Code, A-Evolve, and the open-source Ralph Loop community are already running in production. The capability is here. The governance is not. The engineering teams that figure out the governance first — not the inference throughput, not the model quality, but the boundaries and budgets around the loop — will be the ones that benefit from the pattern without getting burned by it.
