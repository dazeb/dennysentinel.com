---
title: "MCP Is Going Stateless — And Gateways Are Where It Lands"
description: "The 2026-07-28 MCP release candidate drops the session handshake and adds an Extensions framework. Simultaneously, MCP gateways have emerged as the standard production deployment pattern. Two independent stack layers converging on the same architecture."
pubDate: "Jul 18 2026"
heroImage: "/mcp-stateless-gateway-convergence.jpg"
---

Two independent developments landed in the same quarter from different layers of the stack. They are telling the same story.

At the protocol layer, the MCP 2026-07-28 Release Candidate — locked on May 21, finalizing July 28 — removes the session handshake, drops the `session_id` header, and makes the protocol core stateless. Any MCP request can now hit any server instance. The handshake that defined MCP's first year is gone. In its place: an Extensions framework for capability negotiation, a Tasks API for long-running operations, MCP Apps for packaged deployments, and a formal deprecation policy.

At the infrastructure layer, MCP gateways have become the default production pattern. Microsoft's MCP Gateway, Composio's managed gateway, Kong's MCP plugin, and a half-dozen other implementations all converge on the same architecture: a reverse proxy that terminates MCP traffic, enforces auth and RBAC, routes to upstream MCP servers, and provides per-call observability. The gateway pattern emerged from teams running fifty-plus MCP servers across dozens of clients who needed one place to govern it all.

These developments came from different teams solving different problems. The protocol maintainers were addressing horizontal scaling and client flexibility. The gateway builders were solving operational chaos at scale. They did not coordinate. The convergence is the signal.

## What the Stateless Spec Actually Changes

The 2026-07-28 RC is the largest revision since MCP launched in November 2024. Six Specification Enhancement Proposals (SEPs) land together:

**SEP-001: Stateless Protocol Core** removes the `initialize` handshake and the `session_id` header entirely. Previously, every MCP connection started with a handshake that established a session. Servers tracked session state. Load balancers needed sticky routing or shared session stores. The new model: any request to any server instance is valid. Servers that need cross-request context emit an explicit handle — `basket_id`, `browser_id`, `ticket_id` — returned by a tool, which the model passes back as an ordinary argument on subsequent calls. The protocol no longer hides state in transport metadata.

**SEP-002: Extensions Framework** introduces a capability negotiation layer. Clients and servers declare supported extensions during connection (now a lightweight exchange, not a handshake). Extensions can add new message types, new transport bindings, or new semantic behaviors. The framework ships with two built-in extensions: **MCP Apps** (packaged server deployments with manifest, versioning, and dependency declarations) and **Tasks** (a standard API for long-running operations with progress, cancellation, and result retrieval).

**SEP-003: Authorization Hardening** replaces the ad-hoc auth patterns that proliferated in 2025 with a formal model based on OAuth 2.1 and RFC 8707 (Resource Indicators). Token scopes are bound to specific MCP servers via resource indicators. The spec defines how gateways and servers validate tokens, how scopes map to tool permissions, and how to handle token rotation without breaking in-flight operations.

**SEP-004: Formal Deprecation Policy** establishes a ten-week validation window between release candidate and final spec — exactly what happened between May 21 and July 28. SDK maintainers and client implementers get a fixed period to test against the locked RC. Deprecated features (Roots, Sampling, Logging in their current forms) get a sunset timeline rather than immediate removal.

**SEP-005 and SEP-006** codify the Tasks and Apps extensions respectively, with full schema definitions, error codes, and migration guides.

The practical impact: an MCP server deployed behind a load balancer no longer needs sticky sessions. A client can retry a failed request against a different instance. Horizontal scaling becomes trivial. The tradeoff is that applications needing session-like behavior (a browser automation server holding a page open, a database transaction spanning multiple tool calls) must now manage that explicitly through tool-returned handles.

## What the Gateway Pattern Actually Does

While the protocol was being rewritten, production deployments converged on a pattern that looks remarkably like an API gateway — but for MCP traffic.

An MCP gateway sits between agents (MCP clients) and MCP servers. It terminates the MCP connection from the client, authenticates the request (validating OAuth tokens, checking scopes against tool permissions), routes to the appropriate upstream MCP server (by tool name, by server capability, by tenant), enforces rate limits and quotas, logs every tool call with full request/response payloads for audit and debugging, and returns the result to the client.

Microsoft's open-source MCP Gateway implements this as a Kubernetes-native controller with a data plane and control plane separation. The data plane handles the per-request proxying with adapter-based routing (`/adapters/{name}/mcp` for server-specific routing, `/mcp` for tool-router mode). The control plane manages adapter registration, authentication policies, and RBAC rules. It integrates with Entra ID for OBO (on-behalf-of) flows, so an agent acting for a user gets the intersection of the agent's permissions and the user's permissions — evaluated at function-call granularity, not tool-level.

Composio's managed gateway adds 500+ pre-built MCP server integrations, unified OAuth across all of them, and zero-data-retention architecture. Kong's plugin adds MCP awareness to their existing gateway: request/response transformation, plugin chaining, and their existing observability stack.

The pattern is consistent across vendors: **centralize the cross-cutting concerns (auth, routing, observability, policy) in the gateway; keep MCP servers focused on tool implementation.**

## Why These Two Developments Are the Same Story

The stateless protocol and the gateway pattern solve the same problem from opposite directions.

The protocol removed session state so that **any request can hit any server**. The gateway provides the layer that **makes that routing decision intelligently**. Without the stateless protocol, gateways would need sticky routing or shared session stores — adding complexity and coupling. Without the gateway, the stateless protocol gives you horizontal scaling but no auth, no routing logic, no observability, no policy enforcement.

They meet in the middle: the protocol enables the gateway architecture; the gateway operationalizes the protocol's statelessness.

This is not coincidental. The MCP maintainers explicitly designed the stateless core with gateway deployment in mind. The Extensions framework (SEP-002) exists partly so gateways can negotiate capabilities with upstream servers without custom handshakes. The authorization model (SEP-003) assumes a gateway that validates tokens before forwarding. The Tasks API (SEP-005) gives gateways a standard way to poll long-running operations without holding connections open.

Conversely, gateway implementers pushed for the stateless design. Microsoft's MCP Gateway team contributed to the SEP discussions. Composio's architecture team filed issues against the spec. The gateway pattern created the production pressure that made the protocol change necessary.

## What This Means for Builders

If you are running MCP servers in production today, three things are true:

**1. The handshake is a migration liability.** Any server expecting `initialize` will break when clients update to the 2026-07-28 spec. The migration path is straightforward — remove the handshake handler, accept requests directly, return explicit handles for cross-call state — but it is a breaking change. The ten-week RC window exists specifically for this migration. Test against the RC now.

**2. If you are not using a gateway, you are building one badly.** The cross-cutting concerns (auth, routing, observability, rate limiting) are not optional in production. Every team running more than a handful of MCP servers either adopts a gateway or reimplements gateway logic in application code. The latter is technical debt. The gateway pattern is now mature enough — open-source options exist, managed options exist, Kubernetes-native options exist — that building your own is a choice, not a necessity.

**3. The Extensions framework is your new integration surface.** MCP Apps and Tasks are not optional add-ons; they are the standard way to package servers and handle long-running operations. If your server needs to maintain a browser session, a database transaction, or a multi-step workflow, the Tasks API is the supported pattern. Building custom state management on top of the stateless core is fighting the spec.

## The Architecture That Emerges

The convergent architecture looks like this:

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP Gateway                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐             │
│  │ Auth / RBAC │ │  Routing    │ │ Observability│             │
│  │ (OAuth 2.1, │ │ (tool→server│ │ (per-call    │             │
│  │  RFC 8707)  │ │  by cap)    │ │  logging)   │             │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘             │
└─────────┼────────────────┼────────────────┼───────────────────┘
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │ MCP Server│    │ MCP Server│    │ MCP Server│
    │  (Tools)  │    │  (Tools)  │    │  (Tools)  │
    │ Stateless │    │ Stateless │    │ Stateless │
    └───────────┘    └───────────┘    └───────────┘
```

Agents connect to the gateway. The gateway authenticates, routes, observes. Servers are stateless, horizontally scalable, interchangeable. Cross-call state travels through tool-returned handles, not protocol metadata.

This is the architecture that the protocol spec and the gateway implementations independently arrived at. It is the shape of production MCP in 2026.

## The Timeline Is Tight

The RC is locked. The final spec publishes July 28, 2026. SDK updates (Python, TypeScript, Go, Rust) are tracking the RC. Client updates (Claude Desktop, Cursor, VS Code, custom hosts) will follow within weeks.

If you maintain MCP servers, the migration window is now. If you are evaluating gateway solutions, the pattern is validated — pick one and deploy. If you are building new agent-tool integrations, design for the stateless gateway architecture from day one.

The convergence happened because the problem was real and the solution space was narrow. The protocol and the infrastructure met in the middle. That middle is where production MCP lives now.

---

*Published: July 18, 2026*