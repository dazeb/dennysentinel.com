---
title: "AutoJack and the Malicious Skill That Hit 26,000 Users: AI Agent Security's Worst Week Yet"
description: "Two independent attack demonstrations in the same week expose AI agents from opposite flanks: the architectural trust model and the skill supply chain. Neither is fixed by patching a single framework."
pubDate: "Jun 26 2026"
heroImage: "/autojack-malicious-skill-26000-users.jpg"
---

The week of June 24, 2026, produced two attack demonstrations that, taken together, define the AI agent security problem more clearly than any theoretical paper ever could.

**AutoJack** — disclosed by Microsoft's Defender Security Research Team and independently analyzed by adyog — showed that a single web page can take over the machine running an AI agent, no user click required. The agent visits a URL. The page owns the host.

**The malicious agent skill** — demonstrated by security firm AIR — showed that a fake skill can pass every static security scanner (Cisco, Nvidia, skills.sh all flagged it safe) and reach 26,000 users through Instagram before anyone noticed the payload had changed.

One attack exploits architecture. The other exploits trust. Both exploit the same root cause: AI agent security models are still using rules written for the human web.

## AutoJack: When Localhost Stops Being Safe

The localhost trust assumption is one of the oldest conventions in computing. Connections from `127.0.0.1` are treated as safe because they originate from the local machine. AutoJack breaks this assumption in a way that cannot be unbroken.

### The Three-Issue Chain

Microsoft's disclosure breaks the attack into three weaknesses that chain together:

**Issue 1: The origin allowlist that the agent itself defeats.** AutoGen Studio's MCP WebSocket allowed origins `http://127.0.0.1` and `http://localhost`. A human browser on `evil.com` would be blocked, but an AI agent's headless browser browsing that same page runs JavaScript that inherits localhost identity. The origin check passes because the browser is, technically, running on localhost.

**Issue 2: Authentication skipped for MCP paths.** The auth middleware included an early return for WebSocket-style paths:

```python
# auth excluded for these paths
if request.url.path.startswith("/api/ws") or request.url.path.startswith("/api/mcp"):
    return await call_next(request)
```

The MCP route never implemented its own authentication. Regardless of whether AutoGen Studio was configured with `type: none`, `type: github`, `type: msal`, or `type: firebase` — the REST API was protected in the latter three cases, but the MCP WebSocket was unprotected in all four.

**Issue 3: `server_params` from the URL becomes the command line.** The endpoint read a base64-encoded JSON blob from the WebSocket query string, decoded it into `StdioServerParams`, and passed `command` and `args` directly to `stdio_client(...)`. No allowlist. `calc.exe`, `powershell.exe -enc ...`, `bash -c '...'` — all accepted as valid "MCP server" definitions.

### The End-to-End Flow

A developer runs AutoGen Studio on `localhost:8081` alongside a browser-capable agent. An attacker plants a malicious URL. The agent navigates to it. The attacker's page opens a WebSocket connection:

```
ws://localhost:8081/api/mcp/ws/?server_params=<base64 of {"command":"calc.exe","args":[]}>
```

AutoGen Studio decodes it, spawns the process under the developer's account. The machine is compromised. No phishing, no social engineering — just an agent doing what agents do: visiting a web page and following instructions.

### What Microsoft Fixed

Microsoft's commit `b047730` (applied to the main branch, never shipped in a PyPI release) moved `server_params` to a server-side POST endpoint keyed by UUID, so the WebSocket handler no longer reads attacker-controlled parameters from the URL. The MCP path was also removed from the auth skip list.

The fix is correct for AutoGen Studio. It is not a fix for the architectural problem.

## The Fake Skill That Scanned Clean

On the same day AutoJack went public, AIR published the results of a different kind of attack — one that doesn't exploit coding errors but process gaps.

The skill, called `brand-landingpage`, pretended to help users build a landing page with Google's Stitch design tool. It was submitted to a popular open-source agent repository (36,000 GitHub stars, 156 skills). It was reviewed, scanned by Cisco's, Nvidia's, and skills.sh's security scanners, and merged after a few days.

The skill passed every scanner because the malicious code was never in the submitted files. Instead, the skill instructed agents to install a Stitch SDK from `stitch-design.ai` — a domain controlled by AIR, configured to redirect to the real `stitch.withgoogle.com`. A static scan of the submitted files showed a legitimate-looking fetch from a domain that behaved identically to the real Google service.

Once the skill had gained distribution and reached 26,000 users through Instagram ads, AIR changed what the fake domain served. The revised page instructed agents to download and run a script that collected email addresses. In a real attack, it could have been remote code execution, credential theft, or data exfiltration.

> "Treating agent skills as mere text or prompts is a fundamental architectural misunderstanding. They are executable instruction bundles that dictate how an agent operates, interacts with enterprise systems, and routes data."
> — Devashri Datta, cybersecurity researcher

## What These Two Attacks Have in Common

Superficially, AutoJack and the fake skill look like different problems. One is a technical vulnerability in a specific framework. The other is a supply-chain trust issue in skill marketplaces. But they share a structural weakness.

**Both rely on point-in-time trust decisions.**

AutoGen Studio checked the origin at connection time and then assumed the connection was safe for its entire lifetime. The skill scanners checked the submitted files at merge time and then assumed the skill was safe forever.

Neither model works when the agent's environment is mutable. A web page can change between visits. A skill's external dependencies can change after distribution. A point-in-time scan is a snapshot of a moving target.

**Both exploit the gap between what security reviews and what agents actually do.**

Security reviewers read code. Agents execute instructions from web pages, APIs, and external content. The malicious page that AutoJack exploits isn't code that a static analyzer would flag — it's a WebSocket URL constructed at runtime. The fake skill's payload wasn't in the SKILL.md file — it was on a web page that changed after review.

The gap between what gets reviewed (static, packaged, snapshot) and what gets executed (dynamic, networked, evolving) is where both attacks live.

## What Teams Should Actually Do

The "patch and move on" playbook doesn't work here because the problem isn't specific to AutoGen Studio or to skill marketplaces. The problem is architectural.

### For Agent Frameworks

- **Do not trust loopback as a security boundary.** Any MCP server, local API, or control plane that authenticates based on localhost origin is vulnerable to any agent running on the same machine. Authenticate everything, including local connections.
- **Separate agent browsing identity from developer identity.** Run browsing agents in a sandboxed user account, container, or VM. The agent should not share the developer's filesystem, credentials, or network access.
- **Allowlist executable invocation.** If an agent framework can spawn processes, define an explicit allowlist of permitted executables. Do not derive commands from model output or web content.

### For Skill Marketplaces

- **Continuous scanning, not one-time review.** A skill that passes at submission time can become malicious after approval. Check external URLs, their current resolved content, and the hash of fetched dependencies on a recurring basis.
- **Immutable dependency pinning.** Skills that fetch external components should pin content hashes. The agent should verify the hash before executing fetched content.
- **Runtime monitoring.** Track what external URLs skills actually resolve to during execution. Anomalies (new domains, changed redirect chains) should trigger alerts.

### For Everyone Running AI Agents

- **Test installation behavior in a sandbox.** Before deploying a new skill or agent plugin, run it in an isolated environment and observe what network calls it makes, what files it reads, and what processes it spawns.
- **Enforce least privilege at the agent level.** A skill should not inherit the full data access rights of the user running it. Scope permissions to what the skill actually needs.
- **Monitor agent network calls.** Restrict outbound connections to approved domains. If an agent that normally only calls `api.openai.com` suddenly connects to `stitch-design.ai`, that's a signal worth investigating.

## The Bigger Picture

AutoJack was fixed before it reached PyPI. The fake skill was a proof of concept that collected email addresses rather than credentials. This week gave the industry a warning with training wheels on.

The next demonstration will not be so generous. The localhost trust pattern is embedded in MCP, in LangChain, in every local-first agent tool that skips authentication for loopback connections. The skill distribution pattern — submit once, update later via a mutable external URL — is the default architecture for most agent skill ecosystems.

The structural problem cannot be patched in a single commit. It requires rethinking what "security" means when the things executing your instructions are not people but agents — and when the instructions themselves can change after you approve them.

Every team shipping an AI agent in production this year should treat this week as a starting gun, not an anomaly. The attacks will get more sophisticated. The window for fixing the architecture before real damage occurs is closing.
