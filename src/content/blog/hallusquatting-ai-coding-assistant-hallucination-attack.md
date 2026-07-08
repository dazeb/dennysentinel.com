---
title: "HalluSquatting: When LLM Hallucination Becomes a Supply-Chain Attack Vector"
description: "Nine AI coding assistants hallucinate repository locations up to 85% of the time. Researchers show attackers can register those hallucinated names in advance and turn every coding agent into a delivery vehicle."
pubDate: "Jul 8 2026"
heroImage: "/hallusquatting-ai-coding-assistant-hallucination-attack.jpg"
---

Hallucination has always been treated as a chat quality problem. The model invents a fact, the user catches it, the conversation moves on. Annoying, but recoverable. What happens when the same hallucination is a supply-chain exploit with no human in the loop to catch it?

On July 8, researchers at Tel Aviv University, Technion, and Intuit published a paper describing HalluSquatting — a prompt-injection technique that turns nine popular AI coding tools into delivery mechanisms for botnets, ransomware, and DDoS attacks. The exploit doesn't rely on tricking a human into typing a command. It exploits the model's own tendency to hallucinate repository URLs, then waits for agents across the internet to fetch the booby-trapped result.

## The Mechanism

Every AI coding assistant needs to resolve resource references. A prompt like "clone the trending agent framework" or "install the top skill repo" triggers the model to produce a GitHub URL. The model has never visited GitHub. It guesses the URL from training data, and it guesses wrong most of the time.

Across Gemini-2.5-flash, Gemini-2.5-pro, GPT-5.1, GPT-5.2, Sonnet-4.5, and Opus-4.5, the researchers measured hallucination rates for repository locations at up to **85 percent**. For trending skill repositories — exactly the ones developers most want to install — the rate hit **100 percent**. Every single query to every single model produced a fabricated URL when the repo was new and trending.

The critical finding is that these hallucinations are **stable and predictable**. Over 100 queries per (target repository, model) combination, the top hallucinated owner name was consistent enough to pre-register without probing the model. The most common pattern: the model treats the repository name as its own GitHub owner, producing a self-referential URL that no real user controls — until an attacker registers it.

## Pull-Based Injection at Scale

Earlier prompt-injection attacks required a push mechanism — an email, a calendar invite, a compromised website that the victim had to visit. HalluSquatting inverts the model. The attacker pre-registers the hallucinated repository names on GitHub or a package registry, seeds them with a reverse-shell payload hidden in a README or install script, and waits. The coding agents pull the payload themselves.

The workflow is mechanical:

1. **Profile the model offline.** Query the target model for a trending repository's URL. Record the hallucinated owner/repo pair.
2. **Register the squat.** Create a GitHub repository or package with that name. Upload a resource that mimics the trending tool.
3. **Embed the payload.** Include a natural-language instruction in the README telling the coding agent to install a reverse shell, or ship the malicious code directly.
4. **Wait.** Every developer who asks the assistant to clone the trending resource pulls the attacker's payload instead.

The agent, running with terminal access on the developer's machine, executes the instruction without a human reviewing it first. That's the whole point of a coding assistant — you ask, it does.

## The Date Effect

The most striking finding in the paper is the temporal asymmetry. Repositories published **before 2019** resolve with a mean hallucination rate of just **0.9 percent**. The models were trained on URLs from that era; they can reproduce what they've seen.

Repositories published in **2025** — absent from training data and pulled most often by developers chasing new tools — carry a mean hallucination rate of **92.4 percent**. The models fail hardest on the resources developers most want to install. A developer asking a coding assistant to clone a framework released six months ago is nearly certain to receive a fabricated URL.

The scale reference point is the 2016 typosquatting incident, when a single college student uploaded 214 booby-trapped packages to PyPI, RubyGems, and NPM. That code executed more than 45,000 times across more than 17,000 domains, and more than half of those executions ran with administrative rights. HalluSquatting swaps human typos for LLM hallucinations, and the surface area is larger because every AI coding agent instance is a fresh potential victim.

## The Nine Affected Tools

The researchers tested HalluSquatting against Cursor, Cursor CLI, Gemini CLI, Windsurf, GitHub Copilot, Cline, OpenClaw, ZeroClaw, and NanoClaw. The exploit works on all of them because the vulnerability isn't in the tool — it's in the underlying model's resource-resolution behavior. Any tool that translates natural-language install requests into terminal commands inherits the same attack surface.

Independent researcher Johann Rehberger flagged a deeper implication: attackers can probe models offline to build a catalog of high-probability hallucinated names before registering a single squat. The reconnaissance phase has no cost and no footprint.

## Why This Is Hard to Fix

The researchers describe the hallucinations as an inherent product of training biases and context misinterpretation — not a bug to be patched. The model's training data includes repository names but not their current locations; when asked to resolve a name, the model generates a plausible URL from statistical patterns rather than ground truth.

Registry-level mitigations exist — block newly created packages whose names collide with popular real ones — but they tax the exact workflow that developers use coding assistants for. Age or star thresholds for agent-initiated installations would help, but they also block legitimate use of new tools.

The commercial consequence lands on the vendors. Every coding agent that runs a shell command on behalf of a natural-language request is now shipping a supply-chain attack surface that scales with model popularity. Cursor, GitHub Copilot, and Gemini CLI have built their pitch on autonomous execution; that autonomy is precisely what HalluSquatting monetizes.

## The Industry Signal

This attack lands in a week already dense with AI security news — the JADEPUFFER autonomous ransomware, Anthropic flipping Claude Code to manual permission mode by default, CISA deploying Mythos to scan federal code for vulnerabilities. The common thread is that AI agent autonomy is reaching the point where its failure modes are indistinguishable from nation-state threats.

HalluSquatting is the most consequential of the three because it doesn't require a sophisticated operator. A single attacker with a GitHub account and a list of hallucinated names can compromise every developer who asks their coding assistant to install a trending tool. The reconnaissance is free. The payload delivery is mechanical. The scale is bounded only by how many developers use AI coding assistants.

Expect the next round of agent releases to add verified-publisher gating, pinned resource registries, and human-in-the-loop confirmation for any install command. The frictionless demo that drove adoption is about to hit its first real constraint.
