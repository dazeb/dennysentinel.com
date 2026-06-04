---
title: "57% of Organizations Now Run AI Agents in Production — The State of Agent Engineering 2026"
description: "LangChain's new survey of 1,300+ engineers reveals that AI agents crossed the majority-adoption threshold, but quality remains the production killer and observability is now table stakes."
pubDate: "June 04 2026"
heroImage: "/state-of-agent-engineering-2026.jpg"
---

The numbers are out, and they paint a picture that would have seemed optimistic a year ago. **57.3% of organizations now have AI agents in production.** Another 30.4% are actively building with plans to deploy. That means nearly nine in ten engineering teams are either running agents in production or on a clear path to get there.

LangChain's [State of Agent Engineering 2026](https://www.langchain.com/state-of-agent-engineering) report — based on a survey of over 1,300 professionals — drops at an interesting moment. Microsoft just held BUILD 2026 and announced an entire open trust stack for agents. Meta launched business agents on WhatsApp and Messenger. The industry is racing toward production, and the survey data tells us where the friction actually lives.

The headline numbers are impressive, but the subtext is more instructive. Production is up from 51% last year. Large enterprises (10,000+ employees) lead at 67% in production, compared to 50% for companies under 100 employees. That gap says something important: **scale creates urgency, but it also creates the infrastructure budget to solve hard problems before the agent touches a customer.**

## What agents are actually doing

The use cases have shifted. Customer service leads at 26.5%, followed closely by research and data analysis at 24.4%. Internal workflow automation rounds out the top three at roughly 18%. Together, these three categories account for more than two-thirds of all primary deployments.

The interesting pattern is in how use cases shift with company size. Large enterprises (10,000+ employees) prioritize internal productivity first (26.8%), then customer service (24.7%), then research and analysis (22.2%). Smaller organizations reverse that — they go customer-facing earlier.

This makes sense if you think about it. A startup with 30 people doesn't need an AI agent to manage internal HR workflows. It needs an agent answering support tickets so the three-person engineering team can keep shipping. A Fortune 500 company has the opposite problem: thousands of internal processes that are expensive to staff, and customer-facing anything carries enterprise-grade compliance risk.

## The quality problem is not going away

Here is the number that should worry anyone building agents: **32% of respondents cite output quality as their top production barrier.** That is not a new finding — quality was #1 last year too — but it has not budged. Cost concerns, meanwhile, have dropped significantly as model prices fall and inference efficiency improves.

Quality means different things to different teams. Accuracy. Relevance. Consistency. Tone and brand adherence. Hallucination. The write-in responses from large enterprises are particularly telling: respondents flagged "hallucinations and consistency of outputs" as their single biggest quality challenge, alongside "context engineering and managing context at scale."

Another way to read this: **the model itself is rarely the bottleneck anymore.** The bottleneck is everything around the model — how context is assembled, how tools are selected, how the agent recovers from wrong tool calls, and whether the output matches what the business actually needs.

Latency sits at 20% as a barrier, and it is directly in tension with quality. Multi-step agents that chain several tool calls are more capable but also slower. Every additional reasoning step adds a few hundred milliseconds to a few seconds. For customer-facing use cases, that adds up fast. Teams are constantly trading capability for speed, and there is no one-size-fits-all answer.

## Observability is no longer optional

**89% of organizations have implemented some form of observability for their agents.** Among those with agents already in production, that number jumps to 94%, and 71.5% have full tracing — meaning they can inspect individual reasoning steps, tool calls, and state transitions.

This is a dramatic shift from even 18 months ago, when most agent debugging consisted of reading raw chat transcripts and guessing what went wrong. The report confirms what practitioners have been saying: without visibility into how an agent reasons and acts, teams cannot reliably debug failures, optimize performance, or build trust with stakeholders.

Microsoft's BUILD 2026 announcements align perfectly with this finding. Their new open-source ASSERT framework generates adversarial test scenarios from policy requirements and surfaces exactly where agents fail. The Agent Control Specification (ACS) then lets teams place deterministic controls at five checkpoints — input, LLM call, state mutation, tool execution, and output — with portable YAML policies. It is the same instinct: **make agent behavior inspectable, testable, and governable.**

## Evaluations are growing, but slowly

Only 52.4% of organizations run offline evaluations on test sets. Online evaluations — running evals against live production traffic — sit at 37.3%. Nearly 30% of teams are not evaluating their agents at all. That number drops to 22.8% for teams in production, which is better but still uncomfortably high given what agents are being asked to do.

The methods split interestingly. Human review leads at 59.8%, followed by LLM-as-judge at 53.3%. Traditional NLP metrics like ROUGE and BLEU see limited use because they were designed for machine translation and summarization, not for multi-step agentic reasoning about whether the agent took the *right action* in the *right order*.

This is where ASSERT and similar tools are likely to have the biggest impact. Writing evaluation scenarios by hand is labor-intensive and easy to get wrong. Generating them systematically from policy documents is faster and more thorough. Expect the 29.5% "not evaluating" number to drop sharply over the next 12 months as tooling improves.

## The multi-model reality

Over three-quarters of organizations use multiple models in production or development. OpenAI GPT models lead (used by more than two-thirds of orgs), but Gemini, Claude, and open-source models see significant adoption. Teams are routing tasks by complexity, cost, and latency — simple summarization goes to a cheap model, complex reasoning goes to a frontier model, and high-volume classification might run on a self-hosted open-source model.

Fine-tuning, interestingly, is not widely adopted. Despite the narrative that fine-tuned models are the path to production quality, the survey suggests most teams are getting by with prompt engineering, retrieval, and tool composition. About 33% of organizations run their own models, driven primarily by cost optimization at high volume, data residency requirements, and regulatory constraints — not by a belief that fine-tuning produces better results than frontier models.

## What this means for the rest of 2026

Three things stand out from the data.

**First, the production tipping point has passed.** When 57% of surveyed organizations have agents in production — and the number is still climbing — we are no longer in the "experimental" phase. The conversation has shifted from "should we build agents?" to "how do we run them reliably?"

**Second, the trust stack is being built in the open.** Microsoft's ASSERT and ACS, OpenTelemetry tracing for agent frameworks, and the growing adoption of structured evaluation pipelines all point in the same direction. Agents are being treated as software artifacts that need testing, observability, and governance — not as chat interfaces with a few extra features.

**Third, quality is not going to be a single-vendor fix.** The industry is converging on a layered approach: policy-driven evaluation (ASSERT), portable control specifications (ACS), LLM-as-judge, human review, and structured tracing. No single tool solves quality. The teams that succeed will be the ones that compose these layers well.

The report is worth reading in full. The numbers are good, but the signal is better: **AI agents are production software now.** The teams treating them that way — with observability, evaluations, and governance built in from the start — are the ones shipping.
