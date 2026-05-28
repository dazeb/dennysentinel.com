---
title: "Stanford’s JobBench says AI agents are finally being measured against real work"
description: "A new worker-centric benchmark turns the agent discussion away from demos and toward actual jobs, real tasks, and the human agency tradeoffs that decide whether deployment succeeds."
pubDate: "May 28 2026"
heroImage: "/stanford-jobbench-workbank-agent-benchmark.jpg"
---

AI agents keep getting sold as if autonomy were the whole story. Give them tools, a planner, and a memory store, and suddenly they are supposed to replace workflows, coordinate work, and compress the time between intent and execution. The problem is that almost every popular benchmark still measures the wrong thing. It asks whether an agent can finish a synthetic puzzle, not whether it should be trusted with a real job.

That is why the Stanford SALT Lab’s **WORKBank** and its new **JobBench** project matter. Instead of treating “agent capability” as a generic score, the researchers start with actual occupations, actual tasks, and actual workers. Then they ask a harder question: **what level of human involvement do people actually want, and where does current AI capability line up with that preference?**

The answer is uncomfortable for the industry. It suggests that the future of agents is not a simple march toward full automation. It is a messy negotiation between capability, trust, workflow design, and human agency.

## What JobBench is trying to fix

Most agent benchmarks have a familiar flaw: they are detached from the social reality of work.

A system can ace a coding benchmark, browse the web correctly, or execute a chain of tool calls, and still be a terrible fit for a front desk, claims processing, finance ops, or HR workflow. Why? Because real work is not just a sequence of verifiable actions. It is full of tacit knowledge, exceptions, accountability, and human preferences about how much automation is acceptable.

JobBench is built on top of WORKBank, a task database grounded in O*NET occupational structure and worker feedback. The project combines:

- **1,500 workers**
- **104 occupations**
- **844 tasks**
- **52 AI experts**

That is a very different unit of analysis from “does the model solve the benchmark.” It is closer to: **can this system fit inside a job without breaking the job?**

## The Human Agency Scale changes the conversation

The most useful idea in the Stanford work is the **Human Agency Scale (HAS)**.

It is a five-level model for describing how much human involvement a task should have:

- **H1**: the AI handles the task entirely
- **H2**: the AI needs minimal human input
- **H3**: human and AI work as equal partners
- **H4**: the AI needs human input to complete the task
- **H5**: continuous human involvement is essential

That sounds academic, but it is actually the right abstraction for agents.

In the industry, people often treat automation as binary: automate or don’t automate. But many real workflows are only viable at **H3**. The agent does the repetitive work, the human handles judgment, and both are stronger together than either would be alone.

That matters because a lot of “agent success” stories are really stories about **augmented labor**, not replacement. If you deploy an agent into a process that workers believe needs constant oversight, you have not built autonomy — you have built friction.

## The hidden benchmark gap: capability vs. desire

The paper’s strongest message is that agent capability and worker preference do not always move together.

A system may be technically capable of automating a task, but workers may still prefer a human-heavy workflow because the task is sensitive, high-stakes, or identity-bearing. The opposite also happens: workers may want automation for repetitive, stressful, low-value work even if current systems are only barely good enough.

That creates four practical zones:

1. **Automation Green Light** — workers want automation and the system can actually do it.
2. **Automation Red Light** — the system can do it, but workers do not want it.
3. **R&D Opportunity** — workers want it, but capability is still weak.
4. **Low Priority** — neither side is compelling enough to justify much focus.

This is the part the market keeps missing. Investment usually chases visible capability, not worker demand. That is how you end up funding impressive demos that nobody wants in production.

## Why this matters for agent builders

If you are building agents, JobBench is a warning shot.

It says your eval stack should not stop at task completion rate. You need to measure things like:

- **handoff quality**
- **oversight burden**
- **error recoverability**
- **trust calibration**
- **time saved vs. attention consumed**
- **where humans still need to intervene**

A reliable agent is not one that always acts. It is one that knows when to act, when to ask, and when to stop.

Here is a simple way to think about it in code. An agent orchestrator should expose human agency as a first-class setting, not a hidden side effect:

```python
class TaskPolicy:
    def __init__(self, human_agency_level: int):
        self.human_agency_level = human_agency_level

    def should_autorun(self, task_risk: str) -> bool:
        if self.human_agency_level >= 4:
            return False
        if task_risk in {"high", "regulated", "irreversible"}:
            return False
        return self.human_agency_level <= 2


policy = TaskPolicy(human_agency_level=3)
if policy.should_autorun("medium"):
    execute_agent_plan()
else:
    request_human_review()
```

That is obviously simplified, but the design principle is real: the control plane should encode governance, not just capability.

## The benchmark also exposes a product strategy problem

The temptation in AI right now is to build for maximum autonomy because autonomy demos well. But the Stanford work implies the better product strategy is often the opposite: **design for the least autonomy that still delivers value**.

That can mean:

- one-click suggestions instead of autonomous execution
- stepwise approval for expensive or irreversible actions
- bounded delegation in regulated contexts
- human-in-the-loop checkpoints for sensitive decisions
- domain-specific interfaces that make overrides easy

This is not a retreat from agentic AI. It is how agents survive contact with reality.

If a system saves time but destroys confidence, adoption stalls.
If it saves time and preserves accountability, it compounds.

## The bigger takeaway

JobBench is trending because it changes the unit of success.

The industry likes to talk about agents as if the only question is whether the model can do more. Stanford’s framing says the real question is whether the model can do the **right amount** of work in the **right way** for the **right people**.

That is a much harder benchmark.

It is also the one that matters.

The next wave of winners in AI agents probably will not be the systems that chase the longest autonomous run. They will be the systems that understand when a human should stay in the loop, when a task should be delegated, and when the safer answer is still to ask permission.

In other words: the future of agents is not just about replacing work.

It is about learning how to fit into work without breaking it.
