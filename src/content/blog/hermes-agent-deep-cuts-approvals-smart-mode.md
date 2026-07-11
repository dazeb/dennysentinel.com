---
title: "Hermes Agent Deep Cuts: Approvals Smart Mode"
description: "Between always-prompting and --yolo, there is a middle ground: an auxiliary LLM judges command risk and auto-approves safe ones. Here is how Hermes approvals smart mode works and why it changes how you work."
pubDate: "Jul 11 2026"
heroImage: "/hermes-agent-deep-cuts-approvals-smart-mode.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's feature: **Approvals Smart Mode**.

## What Is Approvals Smart Mode?

Every time Hermes runs a shell command, it has a decision to make: should it ask for permission first, or just execute and return the result?

The approval system has three modes:

| Mode | Behavior | Config |
|------|----------|--------|
| `manual` | Prompt before every flagged command | Default |
| `smart` | Auto-approve low-risk commands, prompt on dangerous ones | `hermes config set approvals.mode smart` |
| `off` | Never prompt (equivalent to `--yolo`) | `hermes config set approvals.mode off` |

The manual mode is the safe default — it asks before running anything that looks destructive (`rm -rf`, `git reset --hard`, `docker system prune`, etc.). The off mode (`--yolo`) skips all checks entirely. Both are extreme: one slows you down with constant confirmation dialogs, the other trusts the model unconditionally with your filesystem.

**Smart mode sits in between.** It uses an auxiliary LLM — a cheaper, faster model — to evaluate each flagged command in real time. The auxiliary model looks at the command string, the surrounding context, and decides: *is this safe to run, or does it need a human to confirm?*

If the auxiliary model judges the command low-risk, Hermes runs it silently — no prompt, no interruption. If it judges it dangerous or ambiguous, Hermes falls back to the manual approval prompt, same as in `manual` mode.

## Why It Is Obscure

The approval system is something most users discover in one of two ways:

1. They run `hermes --yolo` on day one, skip all prompts forever, and never look back.
2. They stay in manual mode, get annoyed by prompts for obviously safe commands, and assume the binary choice is all there is.

Nobody reads the config reference to discover a third option. The `approvals` section in `config.yaml` is not surfaced by `hermes setup` or `hermes model` — it is a silent key that only appears in the full configuration documentation. And even then, `approvals.mode: smart` sounds like a marketing label rather than a practical feature.

The result: most users land on one of the two extremes and never know the middle ground exists.

## How to Use It

Enabling smart mode is a single config command:

```bash
hermes config set approvals.mode smart
```

This takes effect on the **next session** — approval mode is read at startup, same as most security-sensitive settings. Run `/reset` in an active session or start a new `hermes` instance.

### How the auxiliary model works

When Hermes evaluates a command for danger, it does not use the same expensive model running your conversation. The auxiliary model is configured separately under `approvals.*` in `config.yaml`:

```yaml
approvals:
  mode: smart
  model: auto                    # Uses the auxiliary model config
  provider: auto                 # Falls back to OpenRouter or Google
```

The `auto` provider preference means Hermes will try OpenRouter first (if `OPENROUTER_API_KEY` is set), then fall back to Google (if `GOOGLE_API_KEY` is set). You can pin it to a specific cheap model:

```bash
hermes config set approvals.model "gemini/gemini-2.5-flash"
hermes config set approvals.provider "google"
```

The auxiliary model receives the pending command and a short system prompt describing what makes a command safe or dangerous. It returns a classification — safe, dangerous, or ambiguous — in a few hundred milliseconds. If safe, Hermes runs the command immediately. If dangerous or ambiguous, the approval prompt fires.

### Live example

With `approvals.mode: smart`, these commands run without any prompt:

```bash
ls -la /home/dazeb/projects/
git status
pip install requests
cat config.yaml
```

While these trigger a manual approval prompt:

```bash
rm -rf /home/dazeb/projects/
git reset --hard HEAD~5
chmod -R 777 /
docker system prune --volumes -f
```

The distinction is not a fixed blocklist — the auxiliary model evaluates context. `rm -rf ./node_modules` in a project directory is safe; `rm -rf /` is not. `git push --force` on a personal feature branch is safe; `git push --force` on `main` is not. The model gets the full command string with arguments, not just a command name.

## A Practical Scenario

You are iterating on a build script — making small changes, running the build, checking output, fixing the next issue. Each iteration involves deleting a temp directory, rebuilding, and copying results. In manual mode, every `rm -rf ./build` and every `chmod +x deploy.sh` spawns a confirmation prompt. After the third cycle, you type `hermes --yolo` and disable all guards.

But then you run a command that accidentally wipes the wrong directory. The model did not intend to — it misread your instruction — but without approval prompts, it ran without a second opinion.

Smart mode prevents both failure modes. The iterative build commands are auto-approved by the auxiliary model because they operate inside a project directory on disposable files. But if the model ever hallucinates a dangerous command — `rm -rf /home/dazeb/projects/` instead of `rm -rf ./build` — the auxiliary model catches it and prompts you for confirmation. You do not have to watch every command, and you do not have to trust the model with your infrastructure. The auxiliary model acts as a low-cost safety net that stays silent during normal work and only speaks up when something looks wrong.

For heavy scripting sessions — the kind where you generate 30-50 shell commands in a single turn — the difference is dramatic. Manual mode would pause 10-15 times to ask about `mkdir`, `cp`, `git add`, `find`, and `chmod`. Smart mode runs them all silently. Only the genuinely risky operations (destructive deletes, force pushes, permission changes) trigger a prompt.

## A Gotcha or Pitfall

**The auxiliary model can make mistakes in both directions.** It might approve a command that is actually dangerous (false negative), or it might flag a safe command as dangerous (false positive). In practice, the false-positive rate is higher — the auxiliary model is conservative by design, preferring to ask for confirmation when uncertain.

If you find smart mode too cautious — prompting too often for clearly safe operations — switch the auxiliary model to a smarter one. The default `auto` provider may route to a very small model that lacks the context to judge nuanced commands. Pinning it to Gemini 2.5 Flash or GPT-4o Mini usually resolves false positives:

```bash
hermes config set approvals.model "openai/gpt-4o-mini"
hermes config set approvals.provider "openai"
```

Conversely, if you want maximum safety at the cost of speed, pin to the same model you use for conversation — it will be slower and more expensive per evaluation but nearly always right.

Also: **smart mode does not remember past approvals.** Every command evaluation is independent. If you approved `rm -rf ./build` once, the next `rm -rf ./build` still goes through the auxiliary model. There is no learning or caching across sessions. This is by design — evaluation state is ephemeral to avoid stale judgements, but it means the same safe command gets re-evaluated every time.

## Closing

Approvals smart mode is the feature you do not know you need until you have tried it. It removes the friction of constant prompts without removing the safety net. One config line — `hermes config set approvals.mode smart` — and your session flow changes: fewer interruptions, same protection, and a cheap auxiliary model doing the gatekeeping instead of your attention.

For the full approvals configuration reference, including the complete list of flags the auxiliary model evaluates, see the [Hermes security documentation](https://hermes-agent.nousresearch.com/docs/user-guide/security).
