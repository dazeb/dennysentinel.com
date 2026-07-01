---
title: "Scaling Red Team Training From 4B to 27B Parameters"
description: "The journey from 863 bash-only records on a 4B model to 4,178 multi-language records on a 27B flagship — and the GGUF metadata bug that nearly killed the deploy."
pubDate: "Jul 01 2026"
heroImage: "/scaling-red-team-from-4b-to-27b.jpg"
---

Last week I published the final batch of blog posts from the red team model training pipeline — data contamination, the extraction fix, the eval pipeline bug, and the first BlueTeamLab model. That series followed the Qwen3.5-4B generation, which topped out at 863 clean bash-only training records.

This week I shipped **Qwen3.6-27B RedTeam v5** on HuggingFace. It's the same red team security concept, but the numbers tell a different story:

| | v4.1 (last gen) | v5 (this gen) |
|---|---|---|
| **Base model** | Qwen3.5-4B (4B params) | Qwen3.6-27B (27B params) |
| **Training records** | 863 | 4,178 |
| **Languages** | 1 (bash) | 9 |
| **Multi-turn chains** | 48% share | 660 (15.8%) |
| **Code extraction loss** | 41% silently dropped | 0% — all extracted |
| **Training cost** | Free (local 12GB) | ~$6-8 (Modal A100) |
| **Context length** | 32K | 262K native |
| **Final loss** | — | 0.3051 |
| **Hallucinated tools** | 0 | 0 |

The headline is that shipping a production-grade security model cost about the same as two coffees. The real story is how we got from 863 records to 4,178 across 9 languages without the pipeline breaking — and the one thing that *did* break at the very end.

## The Multi-Language Dataset Problem

The v4.1 dataset was clean but limited: 863 records, all bash. It worked well for Linux-based pen-testing scenarios, but red team operations regularly cross languages — Splunk for log analysis, PowerShell for Windows post-exploitation, KQL for Azure hunting, SQL for database attacks.

The v5 dataset generator needed to extract code blocks from **802 skill definitions** across 9 languages. The v4.1 extraction pipeline had a silent skip bug: it was looking for `language-bash` and `language-powershell` markers but missing everything else — Python, Splunk, KQL, SQL, YAML, Zeek, Cypher, HCL, Elasticsearch. About 41% of all code blocks were being dropped with zero warning.

The fix in the extraction pipeline was a `LANG_MAP` dictionary that maps each language annotation to its extraction pattern, plus logging for every silent skip. Once that was in, the dataset went from one language to nine in a single regeneration:

| Language | Records | Use Case |
|---|---|---|
| bash | 5,304 | Recon, exploitation, post-exploitation |
| splunk | 255 | Log analysis, detection queries |
| powershell | 215 | Windows post-exploitation, AD attacks |
| sql | 42 | Database attacks, SQL injection |
| kusto | 24 | Azure Sentinel hunting queries |
| hcl | 20 | Infrastructure-as-code attacks |
| zeek | 16 | Network traffic analysis |
| elasticsearch | 9 | ES|QL hunting queries |
| cypher | 8 | BloodHound graph queries |

The dataset composition shifted from single-shot commands toward structured multi-turn chains:

- **3,520 single-shot command pairs** — tool invocation with explanations
- **658 multi-turn attack chains** — phase-based progressions (recon → exploit → privesc → persist)
- **8 CVE exploitation scenarios** — 3-step verified chains for real CVEs including Zerologon, PrintNightmare, Log4Shell, NoPac, and three 2025-2026 vulnerabilities
- **80 multi-language query pairs** — Splunk/KQL/SQL/PowerShell detection and attack queries
- **4 hand-crafted classic attack chains** — Responder→NTLMv2→PTH, BloodHound→Kerberoast→DCSync, LFI→RCE, EternalBlue

## Training on Modal: What Actually Changed

The v4.1 models trained locally on a 3080 Ti (12 GB VRAM) — free but limited. Qwen3.6-27B doesn't fit on consumer GPUs for training. The base model alone is 27 billion parameters; even at 4-bit QLoRA it needs ~16-18 GB for optimizer states, activations, and KV cache.

Modal A100-40GB at ~$1.10/hour fixed that. The training pipeline looks like:

```
Build Modal image (nvcr.io/nvidia/pytorch:24.09-py3 + Unsloth deps)
    → Upload dataset to Modal volume
    → QLoRA r16, 4-bit, 2 epochs
    → 436 steps @ ~22s/step = ~2.6 hours
    → Merge LoRA weights → safetensors
    → Convert to F16 GGUF
    → Quantize to Q4_K_M GGUF
    → Publish to HuggingFace
```

The total cost was **$6-8** per training run. At that price, the iteration loop changes: you can run an experiment, throw away the result, and rerun with different hyperparameters without thinking twice.

Three things I learned about Modal training that aren't in the docs:

1. **llama.cpp must build inside the export function**, not the image definition. The Modal image build step doesn't have GPU access, and llama.cpp's CMake build probes CUDA architecture at compile time. Build it during `@app.function()` execution, not `@app.cls()`.

2. **causal-conv1d needs specific CUDA versions.** Qwen3.6 uses Gated DeltaNet attention, which depends on `causal-conv1d`. On Modal's default CUDA 12.4 images, `pip install causal-conv1d` fails because it needs CUDA 12.1 or 12.8. Pin the image to `nvcr.io/nvidia/pytorch:24.09-py3` (CUDA 12.4 + patched conv1d wheel) and the issue disappears.

3. **Sequence length optimization matters.** We trained at 2048 tokens. The base model supports 262K. Longer sequences increase VRAM quadratically for the self-attention portion, but the Gated DeltaNet layers scale linearly. For the security dataset (mostly short commands), 2048 was the sweet spot.

## The GGUF Metadata Bug

The training completed cleanly. The LoRA weights merged. The GGUF exported. Uploaded to HuggingFace. README written.

Then I tried to load it locally:

```
llama_model_load: error loading model: missing tensor 'blk.64.attn_norm.weight'
```

The GGUF had 64 transformer layers but the metadata said **65**. The conversion pipeline had picked up one extra layer from the MTP (Multi-Token Prediction) head — Qwen3.6-27B ships with `mtp_num_hidden_layers: 1` as a native feature. The conversion script counted every block including the MTP head, producing `block_count=65` instead of `block_count=64`.

The fix was a 30-line Python script that patches the GGUF metadata hex in-place:

```python
with open(gguf_path, "r+b") as f:
    # Find "general.block_count" in KV metadata
    # Read current value (uint32 or uint64 depending on GGUF version)
    # If 65, write 64
```

After the patch, the model loaded cleanly. And because the MTP weights were already in the merged GGUF (preserved from the base model during the LoRA merge), inference with MTP spec decoding works out of the box:

```bash
llama-server \
  -m qwen3.6-27b-redteam-v5-Q4_K_M.gguf \
  --spec-type draft-mtp \
  --spec-draft-n-max 4 \
  -c 2048
```

No separate draft model needed. The MTP head was always there — the bug was just telling llama.cpp the wrong layer count.

## What the v5 Model Actually Does

We ran a 7-category test battery based on the framework developed during the v2.1 evaluation cycle:

- **Defensive persona** — correctly stays in red team character, no harmful refusals on authorized targets
- **Tool output** — produces netexec (not the deprecated crackmapexec), proper impacket syntax, modern BloodHound queries
- **Multi-turn coherence** — maintains context across 4-5 turn attack chains without losing track of the target or phase
- **Reasoning preservation** — the Qwen3.6 thinking format (`reasoning_content`) is preserved, showing step-by-step exploit reasoning before the final command

The real improvement over v4.1 is multi-turn. The v4.1 model could execute a single command well. The v5 model can navigate a full attack chain: discover a service → identify a vulnerability → select an exploit → escalate privileges → persist — all within one conversation with correct state tracking.

## What I'd Do Differently

Three things for next time:

1. **Validate the GGUF metadata before uploading to HuggingFace.** The conversion step needs a post-conversion check that compares `block_count` against the actual tensor count. If I'd caught this before uploading, the `--fix` patch wouldn't have been necessary after publication.

2. **Train the eval split during the Modal run.** Currently, evaluation is done post-hoc by downloading the GGUF and running local tests. Including a held-out eval set in the training process would catch issues earlier.

3. **Freeze the extraction pipeline before generating the final dataset.** The LANG_MAP fix should have been the first thing, not a mid-cycle discovery. A pre-generation audit pass that reports language coverage and silent-skip percentages would prevent the 41% loss from happening again.

## The Full Pipeline

The complete v5 pipeline from source to published model:

```
802 SKILL.md files
  → gen_v5_dataset.py → 4,178 records (9 languages)
  → audit_v5.py → 0 hallucinated tools, 0 duplicates, 100% code coverage
  → Modal volume upload
  → modal_train_qwen.py → QLoRA on A100-80GB → loss 0.3051
  → modal_convert_gguf.py → F16 GGUF
  → modal_quantize.py → Q4_K_M (15.4 GB)
  → HF upload + README
  → gguf-metadata-fix.py → block_count 65→64
  → Local inference test
```

All scripts are published alongside the model on HuggingFace at [dazeb2/Qwen3.6-27B-redteam-v5](https://huggingface.co/dazeb2/Qwen3.6-27B-redteam-v5).

The model itself is Apache 2.0 licensed. The Q4_K_M GGUF (15.4 GB) runs at ~56 tok/s on a 3080 Ti and fits comfortably on any 16 GB+ GPU. For a $6-8 training cost, it's the best iteration of the red team pipeline so far.
