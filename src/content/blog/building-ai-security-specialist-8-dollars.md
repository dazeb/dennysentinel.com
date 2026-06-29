---
title: "Building an AI Security Specialist for $8 — And What Almost Broke It"
description: "Fine-tuning Qwen3.6-27B into a blue-team defensive model cost less than a pizza. The LoRA-to-GGUF conversion almost didn't survive the trip."
pubDate: "Jun 29 2026"
heroImage: "/building-ai-security-specialist-8-dollars.jpg"
---

Last week, I published a post about how my red-team model learned image generation instead of security exploits. The training data was contaminated with 2,856 skill-routing records from Hermes — the model was learning how to route requests to image generators, not how to generate Windows privilege escalation chains.

That was the red team. It made sense to build the defensive counterpart next.

So I trained a blue-team model. Qwen3.6-27B, QLoRA r16, 2 epochs, on a Modal A100 for about 2.6 hours. Total cost: somewhere between $6 and $8. The training went fine — loss dropped from 2.42 to 0.0757, strong convergence, clean validation.

The hard part was everything after training finished.

## The Dataset: Turning Attack Knowledge Into Defense

The blue-team model needed to answer three questions for any security incident:

1. **Detection** — What log events, SIEM queries, and indicators would spot this attack?
2. **Investigation** — What evidence to collect, what systems to check, what chain of events to reconstruct?
3. **Remediation** — What to contain, what to restore, how to prevent recurrence.

The dataset came from 714 red-team skills already in the library. Each skill described a specific attack technique. I generated triples — detection, investigation, remediation — for each one. Then added 21 MITRE ATT&CK technique coverage sets (84 records), 5 multi-turn investigation scenarios (ransomware, Golden Ticket, cloud compromise, insider threat, lateral movement), and 3 defensive strategy scenarios (APT defense, Zero Trust architecture, high-ROI prioritization).

Final count: 1,933 records. 1,739 training, 194 validation.

The dataset generation itself was straightforward — a Python script that walked the skill directory, extracted technique names and descriptions, and fed them through Qwen running locally with structured output prompts. The quality checkpoint was manual: spot-checking detection queries against known correct answers (Event ID 4662 for DCSync, Event ID 4769 for Kerberoasting, Splunk `index=windows EventCode=4688` for PsExec lateral movement).

## The Training: This Is the Easy Part

Modal + Unsloth made the training trivial. One script, one `modal run --detach`, and the job runs in the background. The full spec:

- **Base model:** Qwen/Qwen3.6-27B
- **Method:** QLoRA, 4-bit, LoRA r16
- **Trainable params:** 79.7M / 27.4B (0.29%)
- **Steps:** 436 (2 epochs, effective batch 8)
- **Hardware:** Modal A100-40GB
- **Time:** ~2.6 hours
- **Cost:** ~$6–8

The loss curve was clean: 2.42 → 0.0757. No spikes, no divergence, no surprise NaN. Unsloth's `save_strategy="no"` avoided the SFTConfig pickle serialization bug that plagues high-parameter-count models. The export produced a 17GB `model.safetensors` and 7 supporting files.

Everything you hear about fine-tuning being the easy part is true. The training just worked.

## The Config That Didn't Exist

The model was trained. The weights were exported. Now I needed to run it locally on a 3080 Ti with 12GB VRAM.

This meant two things: quantize the base model to a tiny GGUF, and convert the LoRA adapter to GGUF format so `llama-server` can load it with `--lora`.

The base model quant was straightforward — Unsloth publishes GGUF versions of Qwen3.6-27B, and the UD-Q2_K_XL variant fits in 12GB with room for about 2048 tokens of KV cache.

The LoRA conversion was where it broke.

`convert_lora_to_gguf.py` expects a very specific `config.json` in the adapter directory — specifically, it needs `adapter_config.json` fields like `lora_alpha`, `lora_dropout`, `r`, `target_modules`, and `base_model_name_or_path`. The safetensors export from Unsloth puts an `adapter_config.json` in the output, but it doesn't always match what the GGUF converter expects. The `base_model_name_or_path` can be wrong (pointing to a HuggingFace cache path instead of a valid model ID), and the `lora_alpha` / `r` ratio may not be explicitly set.

The fix was manual: write a correct `adapter_config.json` by hand with the exact values used during training. The LoRA conversion then succeeded, producing a 319MB `.gguf` file.

This is the kind of failure that takes 45 minutes to diagnose and 30 seconds to fix. The error message was:

```
KeyError: 'lora_alpha'
```

But `lora_alpha` *was* in the exported config. It was just under a different key name (`lora_alpha` vs `alpha` depending on the converter version). The converter version that ships with `llama.cpp` (b3930 at the time) looks for the HuggingFace PEFT naming convention, while Unsloth exports use a slightly different schema.

The general lesson: every tool in the LLM inference stack has its own opinion about config file format, and none of them agree.

## VRAM: The 0.5GB Problem

With the UD-Q2_K_XL base GGUF at 12GB and the LoRA GGUF at 319MB, the 3080 Ti's 12GB was almost full before loading a single token. `llama-server` with `-ngl 99` offloads everything to GPU, leaving about 500MB for KV cache.

At `-c 2048`, that works. At `-c 4096`, it OOMs on long generations.

The workaround: run at `-c 2048` for interactive use, or switch to the model's merged-and-quantized GGUF (which embeds the LoRA weights directly) at Q3_K_S for better context handling. The merged version is 6.9GB — comfortably fits with room for 8192-token context.

The LoRA-only path is useful for development (swap adapters without re-downloading the base), but the merged GGUF is better for production.

## What It Produces

The final model answers blue-team questions correctly. Test results:

- **DCSync detection:** Returns Event ID 4662 with correct GUIDs for DS-Replication-Get-Changes and DS-Replication-Get-Changes-All
- **Kerberoasting:** Returns Event ID 4769 with service ticket request detection
- **Golden Ticket:** Returns KRBTGT double-reset remediation with step-by-step procedure
- **Ransomware investigation:** Returns phased approach — containment → evidence collection → root cause → recovery

The model is published on HuggingFace as `dazeb2/Qwen3.6-27B-blueteam-v1` with the complete model card, three usage methods (PEFT adapter, GGUF, API), and full training details.

## The Boring Conclusion

The training cost $6-8. The dataset took an afternoon to generate. The model works.

The LoRA-to-GGUF conversion took three attempts. The VRAM budgeting required two rebuilds. The launch flags needed tuning. The deployment to local inference needed a dedicated port, a config file, and a startup script.

This is the pattern I keep seeing across every AI agent project: the training is reliable, the infrastructure is not. Converters disagree on config formats. Inference servers have different CLI conventions. VRAM budgets don't leave room for edge cases. The model training produces the artifact, but the artifact doesn't run until you've fought through three toolchain incompatibilities.

And that is fine. It is the actual engineering work. The models are getting easier. The pipes between them are still being laid.
