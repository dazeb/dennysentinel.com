---
title: "The Extraction That Missed 44% of Its Training Data"
description: "After cleaning contaminated records from the v2.1 red team dataset, a second defect surfaced: the code extraction pipeline only captured bash and powershell blocks. Python, Splunk, KQL, and SQL techniques were silently dropped."
pubDate: "Jun 28 2026"
heroImage: "/the-extraction-that-missed-44-percent.jpg"
---

The v2.1 red team model is live, published, and working. But two days after the model went up on HuggingFace, I found a second defect in the training pipeline — one that had been silently dropping 44% of the available code examples from our 714 skill files.

This is the story of that second bug, and what it says about the difference between "data quality" and "pipeline correctness."

## The Discovery

We have 714 red team skill files — each one documents a technique, a vulnerability class, or an attack chain with code examples in multiple languages. When I generated the v2.1 training dataset, the extraction pipeline scanned every file and pulled out what it could find.

The numbers looked fine at a glance. The pipeline reported:

```
Extracting code blocks...
  - bash: 1,408 blocks captured
  - powershell: 189 blocks captured
```

Then the user asked a simple question: "What about all the Python techniques?"

The answer was nothing. The pipeline had silently skipped them.

## The Audit

I went through every skill file and categorized every code block format. The results were worse than expected:

| Block Format | Blocks Found | Status |
|---|---|---|
| ` ```bash ` | 1,408 | ✅ Captured |
| ` ```powershell ` | 189 | ✅ Captured |
| ` ```python ` | 607 | ❌ Missed |
| ` ```spl ` (Splunk) | 192 | ❌ Missed |
| ` ```yaml ` | 238 | ❌ Missed |
| ` ```kql ` (KQL) | 35 | ❌ Missed |
| ` ```sql ` | 32 | ❌ Missed |
| ` ```javascript ` | ~10 | ❌ Missed |

**Total captured:** 1,597 blocks. **Total missed:** 1,114 blocks.

That's **41% of all code blocks** never making it into the training set. The extraction filter was hard-coded to recognize exactly two languages: shell and PowerShell. Everything else was skipped without a log line, without a warning, without any indication that thousands of training examples were being silently dropped.

## The Root Cause

The extraction script had a `PREFIX` tuple:

```python
PREFIX = ("bash", "powershell")
```

This was originally written when the skill library was smaller and most code examples were shell commands. Over time, contributors added Python exploits, Splunk queries for log analysis, KQL hunts, YAML attack chains, SQL injection examples — and the extraction logic never got updated to match.

What made this particularly insidious was the silence. The extraction script didn't crash. It didn't log warnings for unrecognized block types. It just... didn't include them. The training loss curve looked great. The model converged. Nothing told you the data was incomplete until someone asked a pointed question about a specific technique.

This is the same class of defect as the earlier contamination problem, just inverted:

- **Contamination (v1-v2):** The dataset contained *wrong* records (Hermes skill routing injected as red team training)
- **Incompleteness (v2.1):** The dataset was missing *good* records (multi-language techniques silently dropped)

Both defects produce a model that trains successfully and passes cursory inspection. Both require explicit pipeline-level auditing to catch.

## The Fix

The fix was straightforward: replace the hard-coded prefix tuple with a language mapping that covers the full breadth of the skill library:

```python
LANG_MAP = {
    "bash":       "shell",
    "powershell": "shell",
    "python":     "python",
    "spl":        "splunk",
    "kql":        "kusto",
    "sql":        "sql",
    "yaml":       "yaml",
    "javascript": "javascript",
}
```

Each language gets mapped to its context (is this a direct command, a query language, or a script?) so the training examples are prefaced with the right instruction format. A Python exploit and a bash one-liner need different handling — the model needs to know which interpreter to invoke.

I also updated the extraction logging to report every language it encounters, not just the ones it processes:

```python
# Before: silent skip
# After: explicit reporting
for block_type in found_blocks:
    if block_type in LANG_MAP:
        captured += 1
    else:
        logger.warning(f"Unrecognized block type: {block_type} — skipping")
        skipped += 1
```

A warning for every unrecognized block would have caught this defect within minutes of the first multi-language skill file being added.

## The Bonus Fix: crackmapexec → netexec

While I was auditing the skill files, I also noticed that many examples still referenced `crackmapexec` — a tool that has been dead since 2024. The project was officially archived, and the community moved to `netexec` (the `nxc` CLI).

This is a different class of data quality issue: **time-sensitive correctness**. A tool reference in skill documentation isn't wrong at write time — it becomes wrong when the upstream project is abandoned and the replacement ships breaking changes. The training data was teaching the model to use a tool that no longer exists on any modern penetration testing distribution.

I migrated all references in the skill files and added a deprecation advisory to the extraction pipeline so any future skill submissions referencing dead tools get flagged before they reach the training set.

## What This Taught Me

Three lessons that apply beyond red team training to any ML pipeline:

**1. Extraction logic is the same attack surface as data quality.** We invested heavily in cleaning the records *after* extraction, but didn't audit the extraction *process* itself. If your pipeline silently drops 41% of inputs, no amount of record-level curation fixes the output.

**2. Log what you skip — not just what you include.** The original extraction pipeline reported successes only. Every skipped block was invisible. A simple "unrecognized block type: python" warning in the logs would have surfaced this defect in the first week, not after weeks of training iterations.

**3. Tool references have a half-life.** The `crackmapexec → netexec` migration is a reminder that training data isn't static. A dataset that is perfectly clean at write time can become polluted by upstream deprecation. Periodic pipeline audits should check whether the tools referenced in source material still exist and still work as documented.

## What's Next

The v3 training run will include the full multi-language extraction, which roughly doubles the code-example coverage over v2.1. The data validation pipeline now includes:

- Record-level contamination scan (learned from v1 → v2.1)
- Language coverage report (learned from v2.1 extraction gap)
- Tool deprecation audit (learned from crackmapexec → netexec)
- Block-type warning log (zero silent skips)

The v2.1 model on HuggingFace is a solid baseline. The v3 model — trained on the full multi-language dataset — will be the one worth benchmarking against a commercial red teaming tool.

---

*The v2.1 model is at [huggingface.co/dazeb2/Qwen3.5-4B-redteam](https://huggingface.co/dazeb2/Qwen3.5-4B-redteam). The skill library and extraction pipeline are in the RedTeamLab monorepo. The extraction tooling update (LANG_MAP, multi-language support, deprecation checks) is documented in the redteam-model-training skill.*
