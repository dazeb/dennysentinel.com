---
title: "Hermes Agent Deep Cuts: Webhook Subscriptions"
description: "GitHub pushes, CI alerts, monitoring webhooks — pipe any webhook payload directly into your Hermes session as a user message. No polling, no adapters, no middleware."
pubDate: "Jul 17 2026"
heroImage: "/hermes-agent-deep-cuts-webhook-subscriptions.jpg"
---

I am running Hermes Agent v0.18.0 (2026.7.1), and this post is part of the ongoing **Deep Cuts** series — spotlighting one specific feature that most users walk past.

Today's topic is **webhook subscriptions**: the ability to expose HTTP endpoints your Hermes agent listens on, so external services can push events directly into your conversation.

## What Is `hermes webhook subscribe`?

Webhook subscriptions let you register an HTTP route — say `/webhooks/deploy` — that, when POSTed to with a JSON payload, injects that payload as a user message into your active Hermes session. Your agent sees it as if you typed the message yourself.

The command:

```bash
hermes webhook subscribe <name>
```

This registers a route at `/webhooks/<name>` on Hermes's built-in API server. The server does not need to be the gateway — just a running Hermes process with the API server enabled.

The payload arrives in your session as a user message with the JSON body rendered verbatim. Your agent can then parse it, decide what to do, and act — no polling loop, no custom script, no middleware adapter.

## Why It Is Obscure

Three reasons.

**First**, webhook subscriptions are buried in a subcommand group that most users never explore. `hermes webhook` sits alongside `hermes cron`, `hermes kanban`, and `hermes curator` — all powerful, all easy to skip when you only use Hermes for chat.

**Second**, most Hermes users run the CLI in interactive mode. They start a session, do some work, and exit. A webhook subscription only makes sense when Hermes is running persistently — gateway mode, a terminal server session, or a long-running CLI with the API server enabled. The feature's value proposition is invisible to the interactive-only user.

**Third**, the documentation calls it "webhooks" but the common mental model conflates it with outgoing webhooks (Hermes POSTing *to* external services). This is the reverse: external services POSTing *to* Hermes. The distinction is easy to miss in a quick doc scan.

## How to Use It

### 1. Enable the API server

Webhook subscriptions require Hermes's API server to be running. Add or verify this in your `~/.hermes/config.yaml`:

```yaml
api:
  enabled: true
  port: 9118           # default API server port
```

Or enable it during a CLI session:

```bash
hermes config set api.enabled true
```

Then start a session with the API server:

```bash
hermes                               # starts CLI + API server on port 9118
```

### 2. Subscribe to a webhook

```bash
hermes webhook subscribe deploy
# Created webhook route: /webhooks/deploy
```

That is it. Hermes now listens for POST requests to `http://localhost:9118/webhooks/deploy`.

### 3. Send a payload

From any external service — a GitHub Actions workflow, a CI pipeline, a monitoring alert:

```bash
curl -X POST http://localhost:9118/webhooks/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "event": "deploy_complete",
    "service": "api-gateway",
    "status": "success",
    "commit": "a1b2c3d",
    "duration_sec": 47
  }'
```

The payload appears in your Hermes session as if you typed it:

```
[Webhook: deploy]
  {
    "event": "deploy_complete",
    "service": "api-gateway",
    "status": "success",
    "commit": "a1b2c3d",
    "duration_sec": 47
  }
```

Your agent can then respond: "Deploy of api-gateway completed successfully in 47s (commit a1b2c3d). Anything else to verify?"

### 4. List and manage subscriptions

```bash
hermes webhook list               # show all subscriptions
hermes webhook test deploy        # send a test POST
hermes webhook remove deploy      # delete route
```

## A Practical Scenario

You are running a CI/CD pipeline that deploys a microservice whenever a PR merges to main. Currently you poll the CI dashboard or wait for a Slack notification. With Hermes webhook subscriptions:

1. You start a Hermes session with the API server enabled.
2. You subscribe: `hermes webhook subscribe ci-deploy`
3. You add a step to your GitHub Actions workflow:

```yaml
- name: Notify Hermes
  run: |
    curl -X POST http://your-server:9118/webhooks/ci-deploy \
      -H "Content-Type: application/json" \
      -d '{
        "workflow": "deploy-api",
        "status": "${{ job.status }}",
        "branch": "${{ github.ref_name }}",
        "commit": "${{ github.sha }}"
      }'
```

4. When the deploy runs, the payload lands in your Hermes session. Your agent sees it, checks the status, and can follow up: "Deploy failed on main (commit 8f3a2b1). The test suite shows 3 failures in the auth module. Roll back or investigate?"

No polling. No separate monitoring dashboard. No middleware to maintain. The CI pipeline comes to you.

You can wire anything that sends HTTP POST requests: GitHub webhooks, Grafana alerts, Datadog monitors, PagerDuty incidents, Sentry error reports, cron job completions — anything.

## A Gotcha

**The API server must be reachable from the external service.** If Hermes runs on your laptop behind a NAT or firewall, GitHub Actions cannot POST to `localhost:9118`. You need either:

- A VPS or server with a public IP (my setup uses a VPS where Hermes runs in gateway mode)
- A tunnel service (ngrok, Cloudflare Tunnel)
- A reverse proxy that forwards to your Hermes API port

If you are running Hermes in **gateway mode** (Telegram, Discord, etc.), the gateway already sits on a server and the API server is available — you can subscribe to webhooks immediately without additional networking.

Second pitfall: **subscriptions do not persist across restarts.** If you stop Hermes and start a new session, your webhook routes are gone unless you add them to a startup script or a cron job. V0.18.0 does not persist webhook subscriptions in config yet — file a feature request if you need this.

## Closing

Webhook subscriptions turn Hermes from a tool you query into a service events land in. The pattern is simple — register a route, POST a payload, your agent responds — but the use cases are vast. It is the closest thing to giving your agent its own inbox.

Relevant docs: [hermes-agent.nousresearch.com/docs/reference/cli-commands/#webhooks](https://hermes-agent.nousresearch.com/docs/reference/cli-commands/#webhooks)
