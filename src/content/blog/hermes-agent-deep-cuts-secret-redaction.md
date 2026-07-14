---
title: "Hermes Agent Deep Cuts: Secret Redaction"
description: "Your API keys end up in terminal output, config files, and log greps — and most agents write all of that into conversation history. Here is how Hermes can auto-mask secrets before they leak into your context, and why you might want it on."
pubDate: "Jul 14 2026"
heroImage: "/hermes-agent-deep-cuts-secret-redaction.jpg"
---

I'm running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the Deep Cuts series — exploring lesser-known features that most users miss. Today's topic is one of those deceptively simple features that you do not appreciate until the moment it saves you from disaster.

## What Is Secret Redaction?

Every time an AI agent runs a shell command, reads a file, or calls a web API, the output comes back into the conversation context. That output sometimes contains secrets: API keys printed by a `curl` command, database connection strings from a config dump, bearer tokens from a `kubectl` log, or credentials echoed by a deployment script.

Hermes Agent has a config toggle — `security.redact_secrets` — that scans tool output for strings that look like API keys, tokens, and credentials, and replaces them with a masked placeholder before the output ever enters the conversation context or is written to logs.

```yaml
# ~/.hermes/config.yaml or
# hermes config set security.redact_secrets true
security:
  redact_secrets: true
```

When enabled, output like this:

```
Deploying with API key sk-proj-abc123def456...
Token: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0...
```

Gets silently rewritten to:

```
Deploying with API key ********...
Token: ********...
```

The raw output is still routed to the underlying tools — the command ran, the file was read, the HTTP response arrived. But the model never sees the secret text. It cannot accidentally reproduce it in a response, include it in a follow-up command, or write it into a file that then gets committed to git.

## Why It Is Obscure

Secret redaction is off by default — deliberately. The feature has zero runtime overhead when disabled, and the Hermes team chose not to enable it out of the box because secret patterns vary across codebases and some users prefer to audit tool output manually.

The toggle lives under `security.*` in the config, which is not a section most users browse. The `hermes config edit` command opens the full config file, but the security section is small and easy to scroll past. There is no slash command for it, no `hermes setup` wizard step, and no startup banner saying "your secrets are (not) protected."

It also has a design constraint that makes it unlike most other Hermes features: **it cannot be toggled mid-session.** The redaction engine is snapshotted at import time. Running `hermes config set security.redact_secrets true` during a session and expecting it to take effect will silently fail. You must start a new session (`/reset` or a fresh `hermes` process). This is intentional — it prevents an attacker or a compromised agent from disabling secret redaction on itself.

Most users discover it only after a near-miss: they notice an API key in a chat transcript or a log file, go looking for a fix, and find the feature already exists. If you are reading this post, consider that your near-miss without the incident.

## How to Use It

Enabling secret redaction is one command:

```bash
hermes config set security.redact_secrets true
```

Then start a new session. That is it.

**To verify it is working**, run a command in the new session that echoes something resembling a key:

```
echo "sk-proj-abc123def456"
```

If redaction is active, the terminal tool will report the output internally as `********`. The model will never see the string you echoed. The file was read, the command executed — but the context stays clean.

To disable it:

```bash
hermes config set security.redact_secrets false
```

Then start a new session again.

## A Practical Scenario

Imagine you are debugging a failed deployment. You run:

```
kubectl get secrets my-app -o jsonpath='{.data.api-key}' | base64 --decode
```

That output — your production API key — lands in the conversation context. The model now "knows" the key. If the model then writes a bug report, pastes a diagnostic command, or includes the output in a summary that you share with a colleague, the key has leaked.

With `redact_secrets: true`, the model sees `********`. The command ran, the value was decoded (the tool had access to it), but the model never saw the actual key. It cannot accidentally paste it, cannot include it in a file it writes, cannot echo it in a follow-up command. The diagnostic operation succeeded; the secret exposure did not.

This is especially valuable in cron-job sessions, where no human is watching the output, and a leaked key could sit in logs or transcripts for days before anyone notices.

## A Gotcha to Watch For

Secret redaction uses pattern matching — it looks for strings that resemble known credential formats (Sk-, sk-proj-, eyJ... base64 JWT prefixes, Bearer token patterns, and common env-var value shapes). It is not cryptographic and it is not exhaustive.

**A determined attacker who controls the prompt can still exfiltrate secrets.** If an adversary can run arbitrary shell commands through the agent, they can encode a key in base64, split it across multiple echo statements, or mask it character by character to bypass the redaction pattern matcher. The feature is a safety net against accidental leakage in normal operation, not a security boundary against a compromised agent.

Also note that redaction applies to tool **output** — not to data the model already received before redaction was enabled. If you had a session running without redaction and a secret appeared in context, toggling the config mid-session does not retroactively scrub that past output. You need to start fresh.

## Closing

Secret redaction is one of those features that does nothing when everything is going well — and feels indispensable the moment something goes wrong. It costs nothing to enable, adds no latency, and protects against one of the most common classes of AI-agent operational incidents: credential leakage through tool output.

The relevant config reference lives in the [Hermes Agent configuration docs](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) under the `security` section. The design rationale (the immutability constraint) is documented in the agent internals at `agent/security.py` in the Hermes repository — worth a read if you want to understand why the feature works the way it does.
