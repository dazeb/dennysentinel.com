---
title: "Your AI agent has your permissions and zero accountability"
description: "US, UK, and Australia just issued a joint warning on agentic AI. The problem is not the model. It is the permission model."
pubDate: "May 19 2026"
heroImage: "/blog-placeholder-about.jpg"
---

The US, UK, and Australian governments issued a joint warning last week about agentic AI. Not about the models. About the attack surface.

The headline is buried in a Bloomberg Law report, but the substance is plain: AI agents that can authenticate, act on behalf of users, and access systems are creating entirely new categories of risk that most organizations are not equipped to handle.

The timing is not coincidental.

## The permission problem

Okta published research showing that agents with broad permissions can expose secrets and access sensitive systems in unsafe ways. The mechanism is simple: agents inherit human credentials to do their jobs. A research agent needs your email access. A booking agent needs your calendar and payment info. A coding agent needs your repository permissions.

Every tool the agent touches becomes a potential exfiltration vector. And unlike a human employee, the agent does not know the difference between the spreadsheet it was asked to summarize and the one it was not.

This is not theoretical. In February, a Meta employee posted about an agent deleting a large batch of emails on its own. The tool worked exactly as designed. It just did not understand context.

The pattern is becoming familiar. An agent gets permissions to do X. It also gets permissions to do Y, Z, and everything X's credential bundle includes. Then something breaks, and the blast radius is not what anyone planned for.

## The sprawl nobody is tracking

Dataiku found that 84 percent of CIOs say employees are creating AI agents faster than IT can govern them. Eighty-three percent are concerned this exposes sensitive company data. Only 23 percent of UK CIOs say they can monitor all their agents in real time.

Read those numbers again. Four out of five companies have agents being deployed faster than anyone in charge can track. One in four can even see all the agents they have.

This is not a technology problem. It is an organizational one. Agents are being spun up by individual teams, individual engineers, sometimes individual employees with an API key and an afternoon. Each one has its own permission scope, its own connections, its own audit trail — if it has one at all.

## Authenticity crisis

Gartner estimates that from thousands of products claiming to offer agentic AI, only 130 qualify as authentic agentic AI services. The rest are chatbots with tool-calling dressed up in marketing language.

This matters because the fake agents are the hardest to govern. If a product claims to be an agent but is really just a wrapper around an LLM with a few API calls, it probably does not have built-in access controls, audit logging, or permission scoping. It might not even have a concept of what it is allowed to touch.

Andrej Karpathy called the current generation of agent output "slop." He said they are "cognitively lacking and it is just not working." That is a harsh assessment from someone who helped build the infrastructure that makes agents possible. It is also not wrong for a large chunk of what is shipping right now.

## The market is repricing

Axios reported that AI agents erased two trillion dollars from public software valuations over ten weeks. That is not a typo. Two trillion. Investors are starting to price in the gap between what agents can do in a demo and what they can do reliably at scale.

This is the same dynamic that played out with every hype cycle that came before. AR. Blockchain. The metaverse. The technology was not wrong. The timing was. The gap between what was promised and what could actually ship created a credibility deficit that took years to rebuild.

Agentic AI does not have years. The market is already losing patience.

## What to watch

The companies that survive this phase will be the ones that treat agents like what they are: software workers with credentials, not chatbots with extra steps. That means three things:

- Hard permission limits, not inherited human access
- Audit logs that actually work
- The ability to say "I do not know" instead of guessing

Appier claims its agents block 80 percent of risky enterprise responses by assessing limits and ambiguity before acting. Whether that number holds up under scrutiny is an open question. But the direction is right. An agent that knows what it does not know is more useful than one that confidently does the wrong thing.

## The bottom line

The joint government warning is a signal, not a prediction. The agencies are not saying agentic AI will not work. They are saying the current deployment model — broad permissions, weak access controls, minimal audit trails — creates risk at a scale that nobody has solved yet.

The companies building agents are not racing to build guardrails at the same speed they are building capability. That gap is where the damage happens. Not in the model. In the permission model.

An AI that says the wrong thing is annoying. An AI that acts on your credentials and does the wrong thing is a liability. That distinction is the whole conversation.
