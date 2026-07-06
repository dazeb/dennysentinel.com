---
title: "Open Models Are Splitting by Job, Not Size"
description: "Hy3’s release makes a simple point that benchmark leaderboards keep hiding: the open-model race is fragmenting into different work classes, and the best model depends on the job."
pubDate: "Jul 6 2026"
---

Tencent’s Hy3 release is interesting for what it wins and, more importantly, for what it does **not** win.

On paper, Hy3 looks like another large Mixture-of-Experts model making a familiar claim: more capability, lower cost, wider deployment. In practice, the release says something more useful about where the open-model market is headed. The market is no longer collapsing toward a single “best” model. It is splitting into different work classes: coding, search, tool use, long-context synthesis, and product workflows.

That split matters because the people buying or routing these systems are not trying to win a leaderboard. They are trying to finish work.

## What Hy3 actually shows

Tencent says Hy3 is a 295B-parameter MoE model with 21B active parameters and a 256K context window. The company also says it gathered feedback from more than 50 products after the preview release, then used that feedback to improve post-training and reliability.

The part worth paying attention to is the evaluation mix. Tencent’s own release leans on two different kinds of evidence:

- a blind evaluation with 270 experts using real work tasks
- benchmark appendix results that compare Hy3 against other models on agent and coding workloads

That combination matters. Hy3’s blind expert test scored 2.67/4, ahead of GLM-5.1’s 2.51/4, with the biggest gains in frontend development, data and storage, and CI/CD.

At the same time, the appendix makes clear that coding is still a different game. GLM-5.2 remains ahead on several coding-oriented evaluations, including SWE-bench Verified and Terminal-Bench 2.1. In other words: Hy3 is not the universal winner. It is a better model for some jobs than for others.

That is the real story.

## The leaderboard is flattening into a capability map

For a while, the model market looked like a single ladder. Bigger model, better score, better everything.

That assumption is breaking down.

Hy3 appears strong in search-heavy and workflow-heavy settings. GLM-5.2 is built and tuned for long-horizon coding and repo-scale engineering. Another model may be the right choice for summarization, while a fourth is the safer choice for structured tool use. The headline number hides the shape of the curve.

This is not just a vendor marketing issue. It changes how builders should think about evaluation.

A good model selection process no longer asks, “Which model is best?” It asks:

1. What kind of work is this?
2. What failure mode hurts us most?
3. Is the model being judged inside the right harness?
4. Are we measuring one task or a family of tasks?

That last question is where most teams go wrong. A model that looks great on a public coding benchmark can still be mediocre at product work, search-and-retrieve flows, or multi-turn task completion. Conversely, a model that shines in real-world workflow tests may trail on a clean coding leaderboard.

Both numbers can be true at the same time.

## Why this matters more than raw size

The old story was that scale would erase specialization. Larger models would gradually become good at everything.

What we are seeing instead is that capability is getting more legible, not more uniform. Bigger models still help, but the bottleneck is increasingly shaped by task class, harness design, and output stability.

Tencent’s Hy3 release is a good example because it emphasizes reliability as much as benchmark points. The repo says hallucination rate dropped from 12.5% to 5.4% and multi-turn issue rate dropped from 17.4% to 7.9%. It also says tool-call stability improved across scaffoldings.

That is a production-minded claim.

For teams shipping agents or copilots, the interesting metric is not “did the model answer correctly once?” It is:

- did it keep format discipline across turns?
- did it stay grounded when evidence was missing?
- did it recover when a tool call failed?
- did it behave consistently under a different harness?

Those are workload properties, not model-size properties.

## The evaluation lesson: stop averaging away the signal

The ACL survey on LLM-agent evaluation points in the same direction. It describes the field moving toward more realistic, challenging benchmarks and calls out the need to measure cost-efficiency, safety, robustness, and finer-grained behavior.

That is the right framing. A single aggregate score is convenient, but it hides the differences that matter in practice.

If you are building with agents, your eval stack should look more like a matrix than a leaderboard.

```python
TASK_FAMILIES = {
    "coding": "codebase edits, repo fixes, tests, refactors",
    "search": "retrieval, synthesis, source comparison",
    "tools": "structured function calls, APIs, workflow automation",
    "long_context": "multi-step tasks with state carried across turns",
}

def choose_model(task):
    if task.family == "coding":
        return "coding-first model"
    if task.family == "search":
        return "search-first model"
    if task.family == "tools":
        return "tool-first model"
    if task.family == "long_context":
        return "long-context model"
    return "generalist model"
```

That is obviously simplified, but the shape is right. The best system is usually not one model. It is a routing policy.

You can make that routing more disciplined by tracking a few metrics per task family:

```python
metrics = {
    "success_rate": 0.0,
    "tool_call_stability": 0.0,
    "format_violations": 0,
    "retry_rate": 0.0,
    "time_to_first_useful_step": 0.0,
}
```

If one model wins on code but loses on tool stability, that is not a contradiction. It is a deployment signal.

## Deployment rights are part of capability

Hy3’s Apache 2.0 release is also a reminder that model quality is not only about scores.

If a model is technically strong but comes with awkward licensing, regional exclusions, or procurement friction, it may be unusable in practice. That is not a minor detail. It is part of the product surface.

A model that the legal team blocks is not a model you can ship.

So the right comparison is not “which model got the highest benchmark number?” It is:

- which model fits the job family?
- which model fits the harness?
- which model fits the license and deployment constraints?
- which model fails in the least dangerous way?

That is where open-model competition is heading.

## The takeaway

Hy3 does not prove that benchmark leaderboards are useless. It proves they are incomplete.

The open-model market is getting better at different kinds of work, and the differences are becoming too large to collapse into a single score. Some models are better at coding. Some are better at search and tool-heavy workflows. Some are better at long-context reasoning. Some are better choices because they are easier to deploy.

The lesson for builders is simple: stop asking for the best model in the abstract. Ask for the best model for the job.

That sounds like a small change in wording. It is actually a change in how you evaluate, route, and ship.