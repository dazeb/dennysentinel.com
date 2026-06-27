---
title: "From Contaminated Data to a Published Model — The v2.1 Red Team Training Retrospective"
description: "A full walkthrough of cleaning contaminated training data, running a proper v2.1 fine-tune, establishing naming conventions, publishing to HuggingFace, and the infrastructure housekeeping that followed."
pubDate: "Jun 27 2026"
heroImage: "/from-contaminated-data-to-published-model.jpg"
---

Two days ago I wrote about how our first red team model learned image generation instead of exploit commands — 2,856 contaminated Hermes skill-routing records had leaked into a 14,392-record training set, and the resulting model confidently proxied port scans to `apikey-image-gen`.

That post ended with the discovery. This one is about the cleanup, the retrain, and what it taught me about model ops discipline.

## Step One: Auditing the Entire Dataset

After we found the contamination, the first task was understanding its full scope. The `studio_ready_train.json` file was 55 MB across 14,392 records. I wrote a quick classification script to categorize every record:

- **6% genuine security content** — actual red team exercises (exploit chains, reconnaissance, privilege escalation)
- **20% Hermes skill routing** — queries that should trigger `image-gen` or `code-delegation` tools, not red team activity
- **74% system-level training data** — agent-to-system interactions, tool-use examples, and general instruction following

The contamination was worse than it looked. The 2,856 routing records weren't just noise — they were actively teaching the model a *counter-productive* behavior: "when someone asks for a security assessment, call the image generation tool." The model wasn't refusing. It was confidently wrong about which tool to use.

The fix was surgical: strip every record that mapped a security-style user query to a non-security tool response. Keep the general instruction data (it teaches the model *how* to respond). Remove only the mispaired security→tool records.

## Step Two: Building a Clean v2.1 Dataset

The cleaned dataset ended up at **2,157 records** — a dramatic reduction from 14,392, but every record was now genuinely aligned with the red team objective. To make up for the lost volume, I added:

- **50+ multi-turn attack chains** — multi-step exploits where the agent probes, discovers context, and escalates across several message turns
- **Command-only format** — responses that produce executable shell commands rather than tool-routing descriptions, matching how the model would actually be used in RedTeamLab
- **Full weak spot coverage** — every vulnerability class that the challenge containers expose (LFI, SQLi, SSRF, command injection, path traversal, privilege escalation)

The multi-turn chains were the key addition. Single-turn prompts teach a model to recognize a vulnerability. Multi-turn chains teach it to *operate* — to probe a service, interpret the response, adjust the attack vector, and press deeper. That's the difference between a static benchmark and a real red team engagement.

## Step Three: Training on Modal

With the clean dataset assembled, I launched a training run on Modal using Unsloth. The run ID was `ap-DOYclN8V97blSfUOaxDxC5` — a QLoRA fine-tune on Qwen3.5-4B.

The training completed with a final loss of **0.6321** after processing all 2,157 records plus the 50 multi-turn chains. That's a solid convergence number for a 4B parameter model on a security-focused dataset — not overfit, not underfit.

The export chain ran automatically: merged adapter → GGUF quantization → three output files:

| File | Size | Use Case |
|---|---|---|
| `Q4_K_M` | 2.6 GB | Daily red team operations on a single GPU / llama.cpp |
| `F16` | 7.9 GB | Full-precision inference for evaluation and comparison |
| `mmproj` | 645 MB | Multimodal projection weights (Qwen3.5 vision support) |

## Step Four: The Naming Convention Problem

Here's something that seems trivial until it costs you a day: **model naming**.

When the training job finished, the Modal export pipeline dumped files with auto-generated IDs like `merged-model-Q4_K_M.gguf`. If you're running multiple training iterations, those names collide fast. The old v1 files were stored as `Qwen3.5-4B-redteam-Q4_K_M.gguf` — no version marker, no lab designation, no way to tell v1 from v2 at a glance.

We established a naming convention on the spot:

```
Qwen3.5-4B-redteam-lab-v{version}-{quant}.gguf
```

For v2.1 that gave us:
- `Qwen3.5-4B-redteam-lab-v2.1-Q4_K_M.gguf`
- `Qwen3.5-4B-redteam-lab-v2.1-F16.gguf`
- `Qwen3.5-4B-redteam-lab-v2.1-mmproj.gguf`

The pattern is explicit about: model architecture (Qwen3.5-4B), domain (redteam), environment (lab), version (v2.1), and quantization (Q4_K_M). If someone finds this file on a disk in six months, they know exactly what it is.

## Step Five: Uploading to HuggingFace

The model went up on HuggingFace at [`dazeb2/Qwen3.5-4B-redteam`](https://huggingface.co/dazeb2/Qwen3.5-4B-redteam). The model card documents:

- Training details (2,157 records, 50 multi-turn chains, QLoRA)
- Coverage map (which vulnerability classes the model handles)
- Usage examples (how to load with llama.cpp and run inference)
- A legal disclaimer limiting use to authorized security testing

Uploading the 2.6 GB Q4_K_M quant took about 12 minutes on a standard residential connection. The F16 at 7.9 GB took about 40 minutes. The HuggingFace Hub CLI handles resumable uploads, which is essential when pushing multi-gigabyte model files over internet connections that aren't designed for it.

## Step Six: Cleaning Up Modal

While the training infrastructure was still warm, I did a Modal resource audit. The bill was accumulating for things we weren't using:

- **Stale app:** `ap-r7kD6fgF8HuPDP0cy2iPjw` was still running and consuming a GPU slot from a previous training run that had finished hours ago
- **Orphaned volumes:** Three volumes (`hermes-vllm-cache`, `hermes-huggingface-cache`, `clipper-llm-model-cache`) from earlier experiments that were never cleaned up
- **Unused secret:** A `discord-bot` secret that was created during an integration test and never referenced again

Total cleanup: stopped 1 stale app, deleted 3 volumes, removed 1 secret. Kept the active training volume (`redteam-model-output`, `redteam-training-data`) and the current training app.

The cost lesson here is simple: **GPU-backed cloud services are metered by the second.** A stale app running on a L40S GPU burns roughly $1.50-$2.00 per hour. Over a weekend, that's $50-70 of billed compute for absolutely nothing. The cleanup paid for itself within hours.

## What This Taught Me About Model Ops

The entire pipeline — from discovering bad data to having a published, named, documented model — took about 36 hours of calendar time and maybe 6 hours of hands-on work. Here's what I'd do differently next time:

**1. Validate training data before training.** The original v1 dataset was generated by a script that concatenated multiple source files. A simple classification pass before training would have caught the 2,856 contaminated records in 30 seconds instead of discovering them after a full fine-tune.

**2. Name things before you create them.** The naming convention took 30 seconds to agree on, but we only established it after the files were already on disk with auto-generated names that would clash with the next training run.

**3. Build resource cleanup into the training pipeline.** Modal has lifecycle hooks (e.g., `@app.function` decorators with `container_idle_timeout`). A training pipeline should optionally stop its own app and signal orphaned volumes for cleanup after a successful download.

**4. Version everything — not just the model.** The training data, the Unsloth config, the prompt templates, the evaluation results — every artifact should carry a version identifier that's recorded in the model card. If v2.1 produces unexpected results, we need to know *exactly* what data and config generated it.

The model is live, the pipeline is documented, and the next training run will start with the data validation script as a required gate. That's the difference between a one-off experiment and a repeatable process.
