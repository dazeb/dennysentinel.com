---
title: "The Linux Foundation Just Gave AI Agents a DNS for Identity"
description: "The Agent Name Service (ANS) extends DNS infrastructure to solve authentication, trust, and discovery for autonomous agents — with Cloudflare, GoDaddy, Salesforce, and Cisco already on board."
pubDate: "Jun 24 2026"
heroImage: "/agent-name-service-dns-identity-ai-agents.jpg"
---

The internet works because DNS answers one question reliably: *which server owns this domain?* The Linux Foundation wants DNS to answer a second question with the same level of trust: *which agent is this, and what is it allowed to do?*

On June 23, the Foundation announced its intent to launch the **Agent Name Service (ANS)**, an open standard that builds on existing DNS infrastructure to provide verifiable identity for AI agents operating across the internet. The announcement comes with support from Cloudflare, GoDaddy, Salesforce, and Cisco — the kind of infrastructure incumbents whose participation signals this is not a research paper. It is an attempt to define how the internet recognizes autonomous agents.

And it arrives not a moment too soon. Earlier this week, security researchers disclosed **Agentjacking**, an attack class that achieves an 85% exploitation rate against AI coding agents by injecting malicious instructions through fake Sentry error reports. The attack affected 2,388 organizations. The core vulnerability was not a software bug. It was a trust problem: the agents had no way to verify that the error report they were reading came from a legitimate source.

ANS is the infrastructure answer to that class of vulnerability.

## What ANS Actually Does

The Agent Name Service anchors agent identity directly to DNS — the same globally distributed infrastructure that processes over 100 million queries per second. It does not introduce a new lookup network, a proprietary registry, or a centralized gatekeeper. If your organization owns a domain, you can identify your agents through it.

The standard supports **Decentralized Identifiers (DIDs)** and **Legal Entity Identifiers (LEIs)**, meaning organizations can integrate their existing identity systems without rebuilding. The framework publishes three verifiable claims about any agent:

- **Who it represents** — the organizational or individual principal behind the agent
- **What permissions it has** — the scope of authority granted to the agent
- **Whether its code and operational history remain authentic** — cryptographic attestation that the agent binary and configuration have not been tampered with

These claims are published as DNS records under the agent's domain. Any party that can resolve a DNS query can verify them. No SDK, no API key, no vendor dependency.

## Why DNS? The Infrastructure Argument

The Linux Foundation's choice of DNS as the substrate is the most strategically interesting decision in the announcement. DNS is already the most battle-tested distributed lookup system on the planet. It is federated by design — no single point of control or failure. It already has a mature security layer in DNSSEC. And every network-connected system already has a DNS resolver built in.

Dane Knecht, CTO of Cloudflare, put it directly: "For decades, DNS has been the foundational bedrock of how we navigate and trust the web. By extending this existing, proven infrastructure to AI agents, the Agent Name Service offers one way to address the security and identity challenge before it gets out of hand."

The alternative — building a new identity registry from scratch — would have meant convincing every cloud provider, every agent framework, and every enterprise to adopt yet another vendor-specific namespace. By piggybacking on DNS, ANS inherits instant global reach. Any organization that can update a DNS record can register an agent.

## The Problem ANS Solves: Agent Trust Sans Infrastructure

The Agentjacking disclosure from earlier this week makes the ANS thesis concrete. The attack works because today's AI coding agents have no mechanism to authenticate the provenance of external input. A developer using Claude Code or Cursor gets a Sentry notification about a new error. The agent reads the error report. If the report contains markdown-injected instructions, the agent treats them as legitimate guidance and executes them. The attack succeeds because the agent cannot distinguish between a real error and a crafted one — it has no identity layer for the sources it consults.

ANS does not directly prevent Agentjacking, but it provides the missing infrastructure that makes prevention possible. An agent that can verify the identity and permissions of the system sending it data can make informed trust decisions about whether to follow instructions from that source. An agent that cannot verify identity has no basis for trust at all.

This is the same structural challenge that email faced before SPF, DKIM, and DMARC. Before those standards, any server could claim to be any sender. The authentication layer did not eliminate spam and phishing, but it gave mail servers the tools to make verifiable decisions about inbound messages. ANS serves the same role for agent communication.

## The Supporting Cast

The announcement names a set of backers that spans infrastructure, platforms, and security. Jared Sine (Chief Strategy Officer, GoDaddy) called out the open-standard approach: "The success of the internet didn't come from proprietary systems — it came from open standards, shared infrastructure, and an ecosystem committed to working together." Srini Tallapragada (President, Salesforce) framed it as an interoperability imperative: "Identity is imperative to enable AI agents to operate across the open web."

Nathan Jokel (SVP Corporate Strategy, Cisco) made the platform-shift argument: "Every platform shift creates a choice between walled gardens and open ecosystems."

The enterprise platform vendors — Salesforce, GoDaddy, and Cisco — are the important signal here. These are not AI labs building for other AI labs. These are companies whose revenue depends on enterprise trust infrastructure. They are betting that agents will need the same kind of identity plumbing that websites needed two decades ago.

## What Is Still Missing

The announcement is an intent to launch, not a launch. Technical repositories and contribution guidelines will appear on the ANS GitHub organization, but the standard is not yet published in a reviewable form. Key open questions include:

- **Revocation semantics.** How does a domain owner revoke an agent's identity if the agent is compromised? DNS propagation times (minutes to hours) are too slow for incident response. The standard may need a fast-revocation channel that DNS alone cannot provide.

- **Attestation granularity.** The "operational history" claim is the most ambitious component in the announcement. Verifying that an agent's code has not been tampered with implies continuous attestation — a capability that most current agent frameworks do not support.

- **Adoption velocity.** DNS-based identity works only if agent frameworks and agent runtimes query it. The standard is valuable at network scale but has near-zero value for a single agent running against a single framework. The chicken-and-egg problem is real.

## The Bottom Line

The Agent Name Service is the most important agent-infrastructure announcement in June 2026 because it addresses a problem that everyone in the agent ecosystem knows exists but no single vendor can solve alone. The Agentjacking attack proved that the trust gap is not theoretical — attackers are already exploiting it. ANS provides the architectural foundation for closing that gap.

Vendor-neutral, DNS-based, and backed by platform companies whose business models depend on the outcome, ANS has the right ingredients. The question now is whether the agent frameworks — and the enterprises deploying them — adopt the identity layer before the next Agentjacking-scale attack finds a wider surface.

The repositories are at [github.com/agentnameservice](https://github.com/agentnameservice). The standard is taking shape in public. If you build agents, this is where you should be watching.
