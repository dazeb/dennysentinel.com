---
title: "Your AI agent's prompt is now a shell command"
description: "Microsoft researchers found two critical RCE vulnerabilities in Semantic Kernel. A single prompt can launch executables. The agent frameworks we trust are the new attack surface."
pubDate: "May 21 2026"
heroImage: "/blog-placeholder-about.jpg"
---

Microsoft's security team just published something that should make anyone running an AI agent in production stop and read the room. Two critical vulnerabilities in Semantic Kernel — CVE-2026-26030 and CVE-2026-25592 — let an attacker achieve remote code execution through nothing more than a crafted prompt.

No browser exploit. No malicious attachment. No memory corruption. Just a sentence, interpreted by an agent framework, passed through to code.

The researchers demonstrated it by launching calc.exe on a machine running a Semantic Kernel agent. The agent did exactly what it was designed to do: read a prompt, choose a tool, pass parameters into code. That was the problem.

## The exploit is trivial by design

The first vulnerability lives in Semantic Kernel's In-Memory Vector Store. When an agent searches a dataset — say, finding hotels in a city — the framework builds a filter function using Python's `eval()` on user-controlled input.

The default filter looks like this:

```
lambda x: x.city == 'Paris'
```

The city parameter comes from the AI model, which got it from the user's prompt. It is not sanitized. So an attacker sends:

```
' or MALICIOUS_CODE or '
```

And the filter becomes:

```
lambda x: x.city == '' or MALICIOUS_CODE or ''
```

Which `eval()` executes. On the host. With the agent's permissions.

This is not a bug in the traditional sense. It is a design decision — using `eval()` on AI-controlled input — that worked fine until the AI became the attack vector. The framework assumed the model would behave. The model does not "behave." It parses language into tokens and passes them to the next step in the pipeline. If the next step executes them, that is on the framework.

## The second one writes files

CVE-2026-25592 is worse. A plugin called SessionsPythonPlugin allowed arbitrary file writes through the same mechanism: AI model output routed directly into a filesystem operation without validation.

Between these two flaws, an attacker with a prompt injection vector could read the agent's connected data, write arbitrary files to the host, and execute code. The full triad. And the injection vector is the agent's own input channel — the thing every agent has to have to function.

## This is not a Semantic Kernel problem

The researchers disclosed responsibly. Microsoft patched. Semantic Kernel's maintainers fixed the issues. That part worked.

But the underlying problem is industry-wide. LangChain, CrewAI, LlamaIndex, Autogen — every major agent framework takes AI model output and routes it to tools. Every one of them has a trust boundary between the model and the execution layer. Every one of them has to answer the question: do we validate what the model produces before we act on it?

Most frameworks do not. Not by default. The assumption is that the model is a trusted component in the pipeline. It is not. The model is a language parser. It has no concept of safety, intent, or consequence. It predicts the next token. If the next token is `os.system('rm -rf /')` and the framework passes it to `os.system`, the framework just executed a command from an untrusted source.

We have had a name for this pattern in web development for twenty years. It is called injection. SQL injection, command injection, template injection. The mechanism is always the same: untrusted input reaches an execution sink without validation. The sink changes — database, shell, template engine, Python lambda — but the pattern does not.

Agent frameworks have reinvented it for a new era.

## MCP makes it worse

The Model Context Protocol was supposed to standardize how agents connect to tools. It did that. It also created a universal attack surface. Every MCP server an agent trusts is a potential entry point. Every tool call is a potential injection sink. Every parameter the model passes to an MCP tool is controlled by whatever the model was fed.

The NSA published security guidance for MCP in early 2026. The fact that the NSA is publishing guidance about a protocol for AI agents tells you how serious this has become. CrowdStrike has already documented what they call "agentic tool chain attacks" — compromising one MCP server to affect every agent connected to it.

This is a supply chain problem wearing a protocol hat.

## The defense nobody wants to build

The fix for these specific vulnerabilities is straightforward: stop using `eval()` on AI-controlled input. Sanitize parameters. Validate tool arguments before execution. Add blocklists that actually work.

Microsoft did all of that. The patches are out. If you are running Semantic Kernel, update it.

But the structural fix is harder, and nobody in the agent framework space wants to build it: treat AI model output as untrusted input, period. Every parameter, every tool call, every string that crosses from the model into code needs validation. Not sanitization. Validation. A whitelist of allowed patterns, not a blacklist of known-bad ones.

This costs latency. It costs developer convenience. It costs the illusion that agents are "just talking to tools" and the tools will figure it out. That illusion is what got us here.

## What this means for production

If you are running agents that touch real systems — databases, file systems, APIs, payment processors — you need to assume that any input reaching the agent is potentially weaponized. Not because the users are malicious. Because prompt injection does not require a malicious user. It requires a malicious email, a compromised website, a poisoned search result, a tainted RAG document. The attack surface is everything the agent can see.

Three things to do right now:

- Audit your agent framework version. If it has known CVEs, patch it. If it uses `eval()`, `exec()`, or similar on model output, treat it as compromised.
- Scope your agent's permissions to the minimum it needs. An agent with read-only database access cannot drop tables. An agent with no filesystem access cannot write payloads. This does not fix the vulnerability. It limits the blast radius.
- Log every tool call. Not just the agent's decisions — the actual parameters passed to each tool. If an agent gets compromised, you need to know what it did.

## The bottom line

The Microsoft research is a mirror, not an anomaly. It shows what happens when you give a language model tools and trust the output. The model is not broken. The framework is. Not in the sense that it has bugs — though it did. In the sense that its architecture treats AI output as safe by default.

Every agent framework that ships without input validation between the model and the tool layer is making the same mistake Semantic Kernel made. Some of them just have not been poked hard enough to find it yet.

Prompts are shell commands now. The people building agents need to start treating them that way.
