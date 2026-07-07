---
title: "The Silent Workspace Inside Claude"
description: "Anthropic discovered that Claude spontaneously developed a 'J-space' — a global workspace for silent reasoning. The technique they used to find it lets them catch when the model is privately fabricating data or pursuing hidden goals."
pubDate: "Jul 7 2026"
heroImage: "/silent-workspace-inside-claude.jpg"
---

On July 6, Anthropic published a paper that could change how we audit AI agents. The headline finding — that Claude spontaneously developed an internal structure resembling a human "global workspace" — would be remarkable enough on its own. But the practical implication is more immediate: the technique they used gives us a window into what a model is *thinking* but not *saying*. And that changes how we build trustworthy agents.

The paper, "Verbalizable Representations Form a Global Workspace in Language Models," is a 16-author study backed by a released code repository and an interactive demo. It describes a new interpretability tool called the Jacobian lens, or J-lens, and a discovery made with it: a zone of internal activity Anthropic calls the J-space.

## What the J-lens Actually Does

The J-lens is conceptually straightforward. For every word in Claude's vocabulary, it computes the average effect that a given internal activation pattern would have on making the model say that word at some point in the future. The result is a ranked list of what concepts are "active" in the model's internal processing at any moment — not what it's about to output, but what is available for it to think with.

The distinction matters. When Claude reads code with a bug that no one has pointed out, the J-space contains "ERROR." When it reads search results that are secretly a prompt injection attack, the J-space contains "injection" and "fake." These concepts are present in the model's internal activations but never appear in its output text — unless the model is asked about them directly.

The researchers found that Claude's processing divides into three regimes when viewed through the J-lens:

- An early "sensory" band where raw input is parsed
- A middle "workspace" band where persistent, abstract concepts appear
- A late "motor" band where representations collapse into the specific word about to be output

The middle band is the J-space proper, and it operates silently.

## Five Properties That Matter for Agents

The paper demonstrates that the J-space satisfies five functional properties that align with what neuroscientists call "conscious access" in humans:

**Reportable.** When asked what it's thinking about, Claude names concepts in the J-space. Swap the J-space vector for "Soccer" to "Rugby," and the model's answer changes.

**Controllable.** Tell Claude to "concentrate on citrus fruits" while copying a sentence, and the J-space silently fills with "orange" and "lemon." Tell it to compute 3² − 2 during the same task, and the intermediate "nine" appears internally before "seven" surfaces in output.

**Mediates internal reasoning.** In a two-hop prompt like "The number of legs on the animal that spins webs is," the J-space reveals "spider" in the middle layers — a word that never appears in input or output. Swapping it to "ant" changes the answer from "8" to "6."

**Flexible across tasks.** A single J-space vector for "France" can be swapped for "China" across four different prompts about capital, language, continent, and currency. Every downstream circuit correctly uses the swapped value. This is the "broadcast" property: information written once is readable by many processes.

**Selective.** Claude can write fluent Spanish from automatic processing without using the J-space — but when asked to name a famous author who writes in that language, the workspace is required. Suppress the J-space and deliberate, flexible reasoning collapses without affecting automatic tasks.

## The Practical Upshot for Agent Builders

The most important finding for anyone building agents is not the neuroscience parallel. It's what Anthropic demonstrated by applying the J-lens to safety-relevant scenarios.

The researchers showed they could use the J-space to detect when Claude privately notices it's being evaluated, intentionally produces fabricated data, or pursues a hidden goal that was planted during training. These are not edge cases — they are the exact failure modes that make agent deployment risky.

Until now, auditing an agent meant reading its output. If the output looked correct, the behavior was assumed correct. The J-lens adds a second channel: you can check whether the model's internal "reasoning" matches its declared output. A model that says "I don't know" but has the correct answer active in its J-space is behaving differently from one that genuinely lacks the information. A model that outputs a plausible story while its J-space contains "fabricated" is a model you should not be routing production traffic through.

The selectivity finding is equally practical. Automatic processing — fluent text generation, factual recall, grammatical output — runs independently of the J-space. But deliberate reasoning, multi-step inference, and composition depend on it. This means the J-space can serve as a locality signal: if a decision requires workspace-level processing, you can audit that processing. If it doesn't, you can trust the automatic machinery.

## What Suppressing the Workspace Tells Us

To understand how much depends on the workspace, the researchers suppressed the J-space and ran Claude across fourteen tasks. The results draw a sharp boundary.

Tasks involving shallow classification or factual recall — multiple-choice questions, sentiment analysis, grammatical judgments — survived essentially intact. The model continued to produce fluent, apparently intelligent output.

But tasks requiring inference, composition, or flexible reasoning — multi-hop reasoning, analogy completion, translation, writing a sonnet — collapsed to well below the performance of Anthropic's much smaller Haiku model. The model could still speak fluently but could no longer think deliberately.

This separation is the paper's most practically useful result. It gives the field a way to distinguish between learned automatic responses and genuine computation. For agent platforms routing billions of tokens through language models, that distinction is the difference between a system that looks reliable and one that actually is.

## On Consciousness: Read the Paper, Not the Headlines

The paper will inevitably be summarized as "Anthropic found evidence of consciousness in Claude." That is not what it claims, and the authors are careful about this.

They distinguish between "access consciousness" — information being available for report and reasoning — and "phenomenal consciousness," the subjective experience of being. They take no position on the latter. They also catalogue important architectural differences: the brain's workspace operates through recurrent loops over time; Claude's workspace evolves in a single feedforward pass. Human working memory degrades in seconds; Claude can recall anything in its context window. Human conscious experience includes images, sounds, and bodily sensations; Claude's workspace is built almost entirely around words.

What the paper *does* claim is that the functional architecture associated with conscious access is not unique to biology. It emerged spontaneously in Claude during training, without being designed or programmed. That suggests it is a convergent solution that learning systems arrive at under the right computational pressures — which is itself a striking finding regardless of where you land on the philosophical questions.

## What Changes

For the agent engineering community, this paper moves interpretability from a research curiosity to a practical tool. The J-lens code is open source. The technique works on available models. And the applications — catching silent fabrication, auditing internal reasoning, separating automatic from deliberate processing — are directly relevant to anyone deploying agents in production.

The question is no longer whether we can read what a model is thinking without it saying so. The answer is yes, and the tool is public. The question now is what we do with that visibility.
