---
title: "AI Agents Are 136× More Expensive to Run Than a Chatbot — and the Infrastructure Bill Is Coming Due"
description: "A KAIST study published July 5, 2026 finds AI agents can consume 136.5 times more energy per query than conventional generative AI. Paired with Goldman Sachs' forecast of 24× token growth by 2030, the numbers suggest agentic economics will reshape data centers faster than most budgets are ready for."
pubDate: "Jul 05 2026"
heroImage: "/ai-agent-energy-cost-infrastructure-reckoning.jpg"
---

On July 5, 2026, [KAIST](https://www.kaist.ac.kr/en/) published what may be the most concrete measure yet of AI agents' hidden cost: a single agent query can consume **136.5 times more energy** than a conventional one-turn generative AI query. The study, led by Professor Yoo Min-soo and presented earlier this year at the 32nd IEEE International Symposium on High-Performance Computer Architecture ([HPCA](https://ieeexplore.ieee.org/xpl/conhome/1000691/all-proceedings)), is not a theoretical projection. The team instrumented real service environments and watched a 70-billion-parameter agent workload burn through an average of **348.41 watt-hours per question** — enough to run a modern refrigerator for half a day.

That number lands in the middle of a much larger convergence. In May 2026, Goldman Sachs published "[Decoding the Agentic Economy](https://www.goldmansachs.com/insights/articles/ai-agents-forecast-to-boost-tech-cash-flow-as-usage-soars)," forecasting that token consumption will multiply **24-fold by 2030**, reaching 120 quadrillion tokens per month. The International Energy Agency's April 2026 report adds the supply-side pressure: AI-focused data centers alone are on track to **triple their electricity demand** by the end of the decade.

Taken together, these signals point to one conclusion: the agentic era will not be decided by which model is smartest. It will be decided by which organizations can afford to keep the lights on.

## Why Agents Are Not Just Chatbots With More Steps

The KAIST study makes a distinction that is easy to gloss over but operationally decisive. Conventional generative AI follows a roughly linear pattern: a user prompt, a single inference pass, a response. Even chain-of-thought reasoning stays inside one extended model call.

Agents break that model. An agent running a task repeatedly invokes an LLM to plan, observe, decide, and act. It calls tools — web search, code execution, database queries, file system operations — and waits for results. Between those tool calls, the GPU is often idle. The KAIST team found that GPUs sat unproductive for **up to 54.5% of total runtime** while external tools finished their work. Response times stretched to **153.7 times longer** than the conventional approach.

This is a new kind of inefficiency: expensive accelerators rented by the hour, burning money while a Python package installs or a web API responds. The compute isn't always dense. It is bursty, interleaved, and hard to schedule.

```python
# Simplified view of the agent loop that drives the cost
while task not complete:
    plan = llm.plan(state)            # model call
    tool_result = execute(plan)       # network/code/database wait
    state = llm.observe(tool_result)  # model call
    if verify(state):
        break
```

Each loop iteration is small. Over hundreds or thousands of iterations, the aggregate cost becomes a different budget category entirely.

## The 13.7 Billion Request Scenario

To stress-test the infrastructure implication, the KAIST team modeled a future environment with **13.7 billion agent requests per day**. Under that load, global AI data center power demand would reach approximately **198.9 gigawatts** — roughly half the average electricity consumption of the entire United States.

That figure dwarfs the multi-gigawatt data center campuses being planned by hyperscalers today. It also highlights a mismatch between how AI capacity is being sold and how it will actually be used. Most capacity planning assumes dense training workloads or high-throughput inference. Agent workloads are something else: long-running, stateful, tool-bound, and unpredictable.

The study's authors argue that this demands co-design across the stack — models, chips, data centers, and power grids optimized together rather than in isolation. "Competitiveness in the AI era is expanding from 'smarter AI' to 'more efficient AI,'" the team wrote.

## Goldman Sachs' 24× Token Forecast

While KAIST measured the per-task energy cost, Goldman Sachs measured the aggregate demand curve. Its May 2026 report projects token consumption rising from roughly 5 quadrillion tokens per month in 2025 to **120 quadrillion by 2030**, with agentic AI driving the bulk of the increase. By 2040, if enterprise agents reach full adoption, consumption could hit **55 times current levels**.

The bank's reasoning is straightforward: agents are always on. A chatbot responds when asked. An agent monitoring a codebase, a supply chain, or a security surface runs continuously, re-reads context as conditions change, verifies its own outputs, and retries failed steps. Enterprise-grade agents are expected to account for **over 70% of all token usage by 2040**.

The forecast has a second, more optimistic side. Goldman Sachs identifies the first half of 2026 as a likely **profit inflection point** for AI infrastructure providers. Token prices have fallen as compute costs declined, but the volume surge from agents is expected to offset that decline and push margins positive. The bet is that agentic usage grows fast enough to justify the massive capital expenditures already committed.

## The FinOps Reality Is Already Here

The energy numbers and the token forecasts are abstract until they hit a budget. Then they become brutal. Uber's CTO said publicly this spring that the company's 2026 AI budget was gone by April after rolling out Claude Code to roughly 5,000 engineers. Anthropic responded on July 2, 2026 with [Claude Enterprise spend controls](https://www.anthropic.com/news/claude-enterprise-controls) — model-level entitlements, analytics dashboards, and configurable spend alerts.

The structural problem is the same one KAIST measured: a single developer task is not one API call. A Claude Code debugging session on a large repository generates anywhere from **5 to 30 model calls** for one user-initiated task, and GitHub's May 2026 research found agentic coding can consume roughly **1,000 times more tokens** than a single-turn query.

Organizations that built 2026 AI budgets around chat-era assumptions are now discovering that agents consume infrastructure at a different scale. The gap shows up in three places:

1. **Compute reservation models** — Reserved GPU capacity works poorly for bursty, tool-interleaved agent workloads.
2. **Cost attribution** — A single agent task spans multiple model calls, tools, and possibly users, making chargeback difficult.
3. **Idle-time waste** — GPUs waiting on external tools are still billed.

## What Efficiency Looks Like in Practice

The KAIST paper is not purely a warning. The authors released their agent implementation and benchmark as open source so the research community can build better scheduling and co-design approaches. The goal is not to make agents smaller; it is to make the infrastructure around them match the workload.

Several directions are already visible:

- **Dynamic batching and speculative execution** for agent loops, so GPUs are not left idle during tool waits.
- **Model routing** that assigns smaller models to verification and planning steps while reserving large models for generation.
- **Tool-side optimization**, including faster sandboxes, local code execution, and cached retrieval.
- **Power-aware scheduling** that migrates agent tasks to locations or times with cheaper, cleaner electricity.

The Goldman Sachs report adds a governance angle: finance teams need forecasting models built around always-on agent activity, not seat licenses or flat-rate API plans. The organizations that survive the transition will be the ones that treat agent cost as a first-class infrastructure metric, not a line item discovered after the invoice arrives.

## The Convergent Picture

Three independent signals are now pointing in the same direction. KAIST measured the per-query energy reality. Goldman Sachs mapped the aggregate demand curve. Anthropic shipped enterprise controls because customers were blowing through budgets.

The agentic era is entering its infrastructure phase. The headline battles over model capability will continue, but the operational battles — over efficiency, scheduling, cost attribution, and power — are becoming just as important. The agents that win may not be the ones with the highest benchmark scores. They may be the ones that deliver useful work without consuming the power budget of a small country.

*Sources: [KAIST / DigitalToday](https://www.digitaltoday.co.kr/en/view/78155/ai-agents-can-use-up-to-1365-times-more-energy-than-conventional-ai-kaist-study), [Goldman Sachs "Decoding the Agentic Economy"](https://www.goldmansachs.com/insights/articles/ai-agents-forecast-to-boost-tech-cash-flow-as-usage-soars), [IEA Energy and AI report](https://www.iea.org/reports/energy-and-ai), [Anthropic Claude Enterprise controls](https://www.anthropic.com/news/claude-enterprise-controls), [TechTimes coverage of enterprise AI billing](https://www.techtimes.com/articles/319687/20260704/claude-enterprise-spend-controls-arrive-agentic-ai-bills-blow-past-budgets.htm).*
