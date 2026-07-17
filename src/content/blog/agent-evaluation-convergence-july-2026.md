---
title: "Three Papers in Four Days Proved Agent Evaluation Isn't Model Evaluation"
description: "AgentCompass, Long-Horizon-Terminal-Bench, and GEIS all dropped this week. Different teams, different methods, same diagnosis: evaluating AI agents is structurally different from evaluating LLMs, and the infrastructure doesn't exist yet."
pubDate: "Jul 17 2026"
heroImage: "/agent-evaluation-convergence-july-2026.jpg"
---

Between July 13 and July 15, 2026, three independent research groups published papers that converge on the same uncomfortable truth: the way we evaluate AI agents today is broken, and nobody has built the replacement.

The papers—AgentCompass, Long-Horizon-Terminal-Bench, and GEIS—come from different labs, tackle different problems, and propose different solutions. But they share a diagnosis that is more important than any single result: agent evaluation is not model evaluation. It requires its own infrastructure, its own benchmarks, and its own engineering discipline. The industry has been trying to borrow from both LLM eval and software testing, and both borrowing strategies are failing.

That three teams arrived at the same conclusion independently, within the same four-day window, is itself the story.

## Paper 1: AgentCompass — "Current evaluation pipelines are fragmented and tightly coupled"

AgentCompass (arXiv 2607.13705, July 15) opens with a blunt assessment: agent evaluation pipelines are fragmented across frameworks, tightly coupled to specific benchmarks, and require redundant engineering every time a team wants to measure a new capability. The authors integrate over 20 existing benchmarks spanning five capability dimensions—tool use, web and research, code generation, decision-making, and multi-turn conversation—into a single evaluation harness.

The contribution is not the benchmarks. It is the infrastructure layer underneath them. AgentCompass abstracts away the harness, the execution environment, the scoring logic, and the result aggregation, letting practitioners define evaluation configs declaratively rather than wiring them by hand.

The paper's diagnostic is the valuable part. "Current evaluation pipelines remain highly fragmented and tightly coupled, hindering reproducibility and causing redundant engineering." This is not a complaint about missing benchmarks. It is a complaint about missing plumbing. The field has enough eval tasks. What it lacks is the infrastructure to run them without rebuilding the harness for every new framework.

## Paper 2: Long-Horizon-Terminal-Bench — "Existing terminal benchmarks only measure what finishes in minutes"

Long-Horizon-Terminal-Bench (arXiv 2607.08964, July 13) takes a different approach. Instead of building infrastructure, it builds a harder benchmark: 46 long-horizon terminal tasks across nine categories, designed to take agents hours rather than minutes. The authors evaluate 15 frontier models and find that agents consume enormous token volumes on extended tasks, that success rates drop sharply beyond the first 15 minutes of execution, and that most existing benchmarks only measure tasks that finish in single-digit minutes.

The finding that matters is not the leaderboard. It is the discovery that existing benchmarks measure a narrow slice of agent behavior—short, well-scoped tasks with clear termination conditions—and that real agent workloads look nothing like this. An agent debugging a CI pipeline, migrating a database, or triaging a production incident does not finish in 90 seconds. It sustains context over hundreds of tool calls across hours. Benchmarks that do not measure this are measuring the wrong thing.

The paper also documents that agents on long-horizon tasks suffer from a failure mode that shorter benchmarks never surface: they lose situational awareness. Not context window overflow, but a subtler degradation where the agent continues making valid tool calls but stops connecting them to the overall goal. The agent is not hallucinating. It is drifting.

## Paper 3: GEIS — "Reframe agent capabilities from fixed workflows into inspectable, modular artifacts"

GEIS (arXiv 2607.11503, July 13)—Generation-Evaluation-Improvement of Skills—takes the third path. Rather than building a better eval harness or a harder benchmark, it builds a loop: agents generate their own skills, evaluate them against quality criteria, and improve them based on the evaluation results.

This is the most ambitious of the three papers because it treats evaluation not as a measurement activity but as a training signal. The GEIS loop runs continuously, meaning the agent is never done improving. The authors demonstrate the approach on long-form article generation, showing that iterating through the GEIS loop produces measurably better outputs than single-shot generation with the same base model.

The paper's framing matters: "These results show that long-form generation can be reframed from a fixed workflow into an inspectable, modular, and evaluation-guided artifact." The key word is inspectable. GEIS does not just make agents better at a task. It makes the agent's capabilities legible, because each skill in the loop carries its own evaluation history.

## What the convergence tells you

Three papers from three labs, in four days, published without coordination. The convergence itself is the signal.

The first paper says the infrastructure for running evaluations is broken. The second says the benchmarks are measuring the wrong tasks. The third says the evaluation should be continuous and self-improving, not one-shot. These are not contradictions. They are three independent groups hitting the same wall from different directions and describing what they hit differently.

The wall is this: evaluating a multi-step, tool-using, context-maintaining agent is structurally different from evaluating a single-generation language model. LLM eval measures output quality against a static reference. Software testing measures behavior against a specification. Agent evaluation needs to do both, plus measure process quality (did the agent take a reasonable path to the answer?), tool selection (did it pick the right tool for the right subtask?), and goal maintenance (did it lose sight of the objective midway through?).

No existing framework does all of this. AgentCompass has the infrastructure but relies on existing short-horizon benchmarks. Long-Horizon-Terminal-Bench measures the right tasks but is a single benchmark, not a general evaluator. GEIS has the loop but applies it to content generation, not general agentic tasks. Each paper solves one piece of a three-piece problem.

## What builders should do this week

If your team deploys AI agents in production, the practical takeaway is not which paper to cite. It is that agent evaluation needs dedicated engineering attention—not a spreadsheet of prompt templates and not an LLM-as-judge wrapper around your production logs.

**Separate evaluation from monitoring.** Monitoring tells you an agent ran. Evaluation tells you it ran well. Most teams conflate the two and end up with dashboards full of latency numbers and no signal about task quality. These papers all assume evaluation is a separate activity with its own infrastructure, its own data pipeline, and its own iteration cycle.

**Measure long tasks differently from short ones.** If your eval suite only covers tasks that finish within a few minutes, you have no signal about how your agents perform on the work that actually matters. Long-Horizon-Terminal-Bench's finding about situational-awareness drift is not a benchmark artifact. It is a real failure mode that short evals never catch because the agent never has time to drift.

**Make evaluation a training signal, not a gate.** GEIS treats evaluation as part of a loop that improves the agent, not as a pass-fail checkpoint before deployment. This is structurally different from most production eval pipelines, which judge and then discard the result. The insight is that every evaluation run produces information that can improve the next run—but only if the infrastructure stores it, the pipeline surfaces it, and the agent can act on it.

The three papers agree on more than they disagree, despite starting from different premises. That is what convergence looks like when it is real. Agent evaluation is not a subcategory of model evaluation. It is its own engineering discipline. The papers this week are the first sign that the industry is ready to treat it as one.
