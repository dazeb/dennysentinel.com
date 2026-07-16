---
title: "Inkling's Architecture Is What Matters — Not the Benchmark Scores"
description: "Thinking Machines Lab dropped Inkling yesterday: 975B parameters, Apache 2.0, controllable thinking effort, no RoPE, encoder-free multimodality. The largest American open-weights model has a lot more going on under the hood than the leaderboard numbers suggest."
pubDate: "Jul 16 2026"
heroImage: "/thinking-machines-inkling-architecture-first-look.jpg"
---

On July 15, 2026, Thinking Machines Lab — the startup founded by former OpenAI CTO Mira Murati alongside John Schulman and Barret Zoph — released **Inkling**, its first in-house model. At 975 billion total parameters (41 billion active), it is the largest American open-weights model to date, and it ships under a no-strings **Apache 2.0 license**.

Most coverage is running the standard playbook: compare SWE-bench scores, rank it against GLM 5.2 and DeepSeek V4 Pro, declare a winner, move on. But the Inkling story is not about where it lands on a leaderboard. It is about the architectural choices that got it there — several of which break from the conventions every other large model has settled on.

Let's look past the benchmark table at what Thinking Machines actually built.

## The Architecture: Where Inkling Breaks the Mold

Inkling is a decoder-only Mixture-of-Experts transformer, but the architecture diverges from the GPT/Claude/DeepSeek template in at least four meaningful ways.

### No RoPE — Relative Attention Instead

Every major model released in the last three years uses Rotary Position Embeddings (RoPE) to encode token positions. Inkling does not. Instead, it uses a learned relative attention mechanism: a fourth projection (on top of Q, K, V) produces a per-token, per-head relative feature vector, which is then modulated by the distance between query and key tokens and fed into the attention logits.

Why this matters: RoPE has desirable properties — it generalizes to unseen sequence lengths, it is simple to implement, and it has become the default. But it also imposes a rotational structure on the attention space that may not be optimal for every architecture. Thinking Machines's bet is that learning position directly in attention space gives the model more flexibility to encode positional relationships that RoPE cannot capture efficiently. The 1M token context window suggests they may be right.

### Short 1D Convolution Over Hidden States

Before each attention layer, Inkling applies a short 1D convolution (SConv) over the hidden states — reading the current token and the previous W-1 states. This is a genuinely unusual design choice in a large language model.

The intuition is straightforward: the SConv handles local pattern extraction — the kind of thing attention layers waste capacity on — while freeing the MoE and self-attention modules to focus on long-range dependencies and expert specialization. It is a deliberately engineered division of labor, and it mirrors what some vision transformers have done with convolutional stems. Seeing it in a 975B-parameter language model is notable.

### Hybrid Global-Sliding Window Attention

The decoder layers follow a 5:1 pattern — five sliding-window attention layers for every one global attention layer. Sliding window layers attend only to a fixed-size local context, while global layers attend to the full sequence.

This is less exotic than the SConv choice but still significant. Most large models use either full attention everywhere (expensive) or a consistent sparse pattern. The hybrid approach gives Inkling efficient local processing by default, with full-sequence reasoning reserved for every sixth layer. The final layer is always global, ensuring the last representation benefits from the complete context.

### Encoder-Free Multimodal Fusion

Inkling does not use CLIP, SigLIP, Whisper, or any external encoder for images or audio. Instead, it ingests both modalities through lightweight learned towers:

- **Images** are encoded as 40×40 pixel patches via a hierarchical multi-layer perceptron (hMLP) — four stacked linear layers that progressively merge pixels into embeddings, projected directly into the model's shared hidden space.
- **Audio** is converted to discrete mel spectrograms (dMel) at 100ms chunks, then classified into mel bins and embedded through an audio tower — again, directly into the shared space.

This encoder-free approach means the model learns multimodal reasoning end-to-end rather than relying on frozen encoder representations. The trade-off is that the multimodal components require training from scratch (which Thinking Machines did, on the full 45 trillion token corpus), but the result is a model whose visual and audio understanding is native to its architecture rather than bolted on.

## Controllable Thinking Effort: The Headline Feature

The feature most likely to be copied by other labs is Inkling's **controllable thinking effort** — a continuous parameter (0.2 to 0.99) that lets developers dial the model's reasoning budget up or down.

This is not the same as the "effort" parameter on reasoning models like o3 or Gemini, which typically offers a small discrete set of presets (low, medium, high). Inkling's effort is continuous, which means you can tune it to exactly the cost-performance trade-off your workload needs.

The results are measurable: at effort=0.99, Inkling scores 63.8 on Terminal Bench 2.1. Sweep the effort down and you get proportionally fewer thinking tokens and lower cost. On Terminal Bench, Inkling matches Nemotron 3 Ultra's score at roughly **one third the thinking tokens**.

### Chain of Thought Condensation

During RL training — over 30 million rollout iterations — Thinking Machines researchers observed an emergent phenomenon they call **chain of thought condensation**. Inkling naturally learned to compress its internal reasoning steps, dropping grammatical overhead and connective phrases while reaching the same conclusions. The model became more token-efficient at reasoning without being explicitly optimized for it.

This is significant because it suggests that the model is not simply memorizing reasoning chains but learning which steps are genuinely necessary. If this condenses further in future training runs, the implications for inference cost are substantial: cheaper reasoning without sacrificing capability.

## The Open-Weight Landscape Just Shifted

Inkling's Apache 2.0 license is the detail that matters most to builders. In a landscape where most "open" models come with acceptable-use policies, revenue caps, or dual-use restrictions, Inkling is legally unencumbered. You can download it, fine-tune it, deploy it commercially, modify it, and redistribute it — no phone-home, no audit clause, no revenue share.

This puts it in direct competition with the Chinese open-weights ecosystem (DeepSeek V4, GLM 5.2, Kimi K2.6) that has dominated the conversation around permissive licensing for the last year. Murati's team is making a specific argument: American labs can compete on openness, not just on capability.

The model is already available on [Hugging Face](https://huggingface.co/thinkingmachines/Inkling) in both BF16 and NVFP4 quantization, with day-0 support in SGLang, vLLM, llama.cpp, and transformers. A preview of Inkling-Small — 12B active parameters — is also available, hinting at a broader family to come.

## What This Means for AI Agents

For the dennysentinel.com audience, the agentic numbers are the ones that matter. Inkling scores:

- **77.6% on SWE-bench Verified** (beats Nemotron 3 Ultra's 71.9%)
- **74.1% on MCP Atlas** (agentic tool-use benchmark — significantly ahead of Nemotron's 44.7%)
- **46.0% on HLE with tools** (close to GPT-5.6 Sol on tool-assisted reasoning)

In agentic coding, Inkling was trained with randomized tool sets and schemas to reduce sensitivity to any particular harness — a pragmatic choice for a model designed to be fine-tuned into specialized agentic roles.

The Tinker platform lets developers fine-tune Inkling for their specific agent use case, and the company demonstrated the model writing its own fine-tuning scripts via self-prompting — a capability that, if reliable, could dramatically lower the barrier to custom agent models.

## The Bottom Line

Inkling is not the best model on any single benchmark. GLM 5.2 beats it on coding. Claude Fable 5 beats it on reasoning. GPT-5.6 Sol beats it on Terminal Bench. That is the honest assessment Thinking Machines published themselves, and it is worth taking at face value.

What Inkling is, instead, is the most **architecturally interesting** large open-weights release from an American lab in 2026. The relative attention, the short conv layers, the hybrid attention pattern, the encoder-free multimodal fusion, and the continuous thinking effort — each of these is a deliberate departure from the dominant design. Collectively, they represent a genuine alternative to the GPT architecture family that has become the de facto standard.

Whether those choices produce a durable advantage will be determined by how well the model fine-tunes, how the architecture scales to the next generation, and whether the ecosystem builds on it. But for the first time in a while, an American open-weights release is asking interesting questions about model design instead of just chasing benchmark scores.

*Disclosure: This post was researched using the Thinking Machines Lab announcement blog, the Inkling model card, the Hugging Face blog post by Hugging Face engineers, VentureBeat's coverage by Carl Franzen, and The Register's coverage. All sources published July 15-16, 2026.*
