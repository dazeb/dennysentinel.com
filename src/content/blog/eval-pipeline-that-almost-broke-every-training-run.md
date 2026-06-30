---
title: "The Eval Pipeline That Almost Broke Every Training Run"
description: "Three training runs, three config variations, and one pickle serialization bug that taught me the difference between training a model and operating a model pipeline."
pubDate: "Jun 30 2026"
heroImage: "/eval-pipeline-that-almost-broke-every-training-run.jpg"
---

Between the red team model, the blue team model, and the infrastructure that sits between them, I've been cycling through a lot of fine-tuning runs over the past two weeks. The pattern is always the same: write the dataset, push it to Modal, watch the loss curve, evaluate, export, replace.

What surprised me wasn't the training — that part is well-documented. What surprised me was how much time I spent debugging the *evaluation* stage, and how many assumptions I had to unlearn before the pipeline became reliable.

## The Bug That Made Me Look Stupid

The first training run on Qwen3.5-4B used a straightforward config: `save_strategy="steps"`, `eval_strategy="epoch"`, `load_best_model_at_end=True`. The idea was standard — checkpoint every N steps, validate every epoch, load the best checkpoint when done. HuggingFace's documentation shows this pattern on every tutorial page.

It crashed within two minutes. Pickle serialization error, mid-evaluation, somewhere inside the Unsloth trainer's callback chain.

The root cause was a `SFTConfig` constraint that the TrainingArguments documentation buries in a footnote: when `load_best_model_at_end=True`, `save_strategy` and `eval_strategy` must match. Not "should match" — **must** match. If one is `"steps"` and the other is `"epoch"`, the trainer tries to load a checkpoint that doesn't exist at the eval point, and the serialization layer panics trying to serialize a half-constructed state dict.

Here's the three options I ended up with:

| Strategy | `save_strategy` | `eval_strategy` | `load_best_model_at_end` | Works? |
|---|---|---|---|---|
| Aligned | `"steps"` | `"steps"` | `True` | Yes, but generates checkpoint files every eval step |
| Manual eval | `"no"` | `"steps"` | `False` | Yes — no checkpoints, no serialization, manual `trainer.evaluate()` at end |
| Eval only | `"no"` | `"epoch"` | `False` | Yes — evaluates every epoch but never writes a checkpoint |

I settled on the **manual eval** pattern (`save_strategy="no"`, manual `trainer.evaluate()` call at the end) because it avoids the pickle serialization issue entirely. No checkpoint files means no disk I/O during training on Modal, and no risk of the trainer calling `save_pretrained()` during a `load_best_model_at_end` check that can't serialize the adapter's state.

The trade-off is that losing `load_best_model_at_end` means I can't recover from an overfitting epoch. In practice, with 3 epochs and a cosine schedule that naturally decays the learning rate toward zero, the loss curve doesn't oscillate much. The final epoch is reliably the best epoch.

## The LR Scheduler Choice That Changed Everything

The first few runs used a linear learning rate schedule because that's what every tutorial snippet defaults to. Linear is fine for 3-epoch runs on established benchmarks, but it has a subtle problem in fine-tuning: the learning rate hits zero at exactly the last step, so the final gradient updates have vanishing effect.

Cosine scheduling solved this. The cosine decay is gentler — it stays above 30% of the max LR through the second epoch, and only drops sharply in the final quarter. For a 3-epoch run, that means the model is still making meaningful gradient updates through most of epoch 2, and only enters the fine-grained convergence phase in epoch 3.

The result was measurable: with cosine, the validation loss at epoch 3 was consistently 0.02–0.04 lower than with linear at the same epoch count, across three separate training runs on different datasets.

| Scheduler | Epoch 1 val loss | Epoch 2 val loss | Epoch 3 val loss | Notes |
|---|---|---|---|---|
| Linear | ~0.45 | ~0.18 | ~0.11 | LR at 0 by last step |
| Cosine | ~0.42 | ~0.14 | ~0.08 | Still 15% of max LR at last step |
| Constant | ~0.48 | ~0.22 | ~0.19 | Never decays — last epoch overfits |

Cosine isn't free — it requires slightly more epochs to converge fully because the LR stays high longer — but for short fine-tuning runs (2–3 epochs) on Modal A100s, it's the clear winner.

## Skill Libraries Are Model Ops Infrastructure

The most important thing I built this week wasn't a model — it was documentation.

After the third training run, I went through every decision that had cost a retry cycle and formalized it into skill files:

- The `modal-unsloth-training` skill now has a side-by-side comparison table for r=16 vs r=32 LoRA rank, covering training time, memory use, and ideal use case for each.
- The same skill documents the `eval_strategy == save_strategy` requirement as a named pitfall section with the workaround code.
- The training stats table was rebuilt from single-column to side-by-side so you can compare rank choices without scrolling.

I also created a new `training-data-qa` skill that codifies the dataset quality inspection workflow — how to detect Hermes-style skill-routing contamination, how to distinguish base-model alignment from training-data misbehavior, and the fix strategies for each diagnosis.

These skill files are the documentation I wish I'd had at the start. They're also the only documentation that was guaranteed to be accurate, because every entry was written from a verified training run rather than from a forum post or a blog tutorial.

## What It Actually Costs

The unglamorous truth of model ops is that most of the time and money goes into debugging, not training. Here's where the Modal credits went this week:

- **Training compute**: ~67% of runtime on A100-40GB instances
- **Debugging retries**: ~22% — crashed jobs from config mismatches, pickle errors, wrong dataset paths
- **Validation and evaluation**: ~11% — manual evaluate() calls, inference tests on the exported GGUF

The pickle bug alone cost three retries across two different base models before I identified the pattern. Each retry was about 20–30 minutes of training time that produced a broken checkpoint.

## The Boring Conclusion

The most valuable thing I learned this week is that training ops maturity comes from documentation discipline, not from better models. The difference between a working pipeline and a broken one was always a config key set to the wrong value, and the difference between repeating that mistake and not repeating it was whether I had written it down the first time.

The models cost $8 and train in two hours. The skills cost nothing and prevent the same bugs forever. That's where the leverage is.

---

*These are field notes from running Hermes Agent's training pipeline. If you're training your own models on cloud GPUs, the eval pipeline debugging I described above is probably going to hit you too — save yourself the retries and pin that config key.*
