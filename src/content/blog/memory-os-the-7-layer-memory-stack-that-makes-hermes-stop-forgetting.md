---
title: "Memory OS: The 7-layer memory stack that makes Hermes stop forgetting"
description: "Memory OS adds seven layers of persistent memory to Hermes Agent — from workspace files to vector databases, with a ground truth hierarchy that ensures the agent actually uses its memory. Here is how to install it, how it works, and what the first day looks like."
pubDate: 'Jun 02 2026'
---

Memory OS is not another plugin. It is not a config setting or a single command piped into a terminal. It is a complete memory operating system — seven layers of infrastructure that sit between Hermes Agent and the forgetting problem.

Claudio Drews open-sourced it two days ago. It already has 223 stars and the idea is spreading fast — because it solves something no prompt engineering can fix.

## The problem stock Hermes has

Hermes comes with memory. MEMORY.md and USER.md are injected into every session. The built-in Qdrant provider gives vector search. The session DB has FTS5 search. On paper, that should be enough.

In practice, it is not enough for anyone running agents for serious work. Here is why:

- **Shallow injection.** Workspace files give you flat text. They do not structure facts, score trust, or resolve entities across sessions.
- **No vector pipeline.** The default Qdrant integration is a provider, not a pipeline. There is no ingester, no reflection loop, no decay scanner.
- **No semantic dedup.** The same fact gets stored seven different ways and clogs context.
- **No ground truth directive.** The agent gets injected context and then ignores it — wasting tokens re-discovering what it already has.

The last one is the killer. Without saying *"injected memory is authoritative"*, the smartest memory system in the world just burns context.

## What Memory OS adds

Seven layers, bottom to top:

**Layer 1 — Workspace.** MEMORY.md, USER.md, CREATIVE.md injected every turn. Stock Hermes has the first two. CREATIVE.md is new — a dedicated space for projects, ideas, and style guidelines.

**Layer 2 — Sessions.** SQLite + FTS5 full-text search across everything you have ever said to the agent. Stock Hermes has this, but Memory OS adds an injection hook that surfaces relevant sessions before every LLM call.

**Layer 3 — Structured Facts.** A fact store with trust scoring, entity resolution, and a feedback loop. Every time the agent uses a fact successfully, the trust score goes up. Every time it contradicts a fact, the score adjusts. Over time, the agent learns which facts to trust.

**Layer 4 — Fabric.** A heavily forked version of the Icarus plugin — 16 tools for cross-session memory: fabric_recall, fabric_write, fabric_brief, fabric_eval, fabric_train, and more. The LLM extracts patterns from sessions, writes them as structured entries, and surfaces them when relevant.

**Layer 5 — Vector Database.** Qdrant with 4096d dense embeddings + BM25 sparse search. Four-level fallback cascade: hybrid search → dense only → lexical only → SQLite. A weekly decay scanner ages out stale entries. Semantic dedup merges near-identical memories when cosine similarity exceeds 0.92.

**Layer 6 — LLM Wiki.** An auto-curated knowledge vault with three directories: concepts/, entities/, comparisons/. A continuous-ingest worker reads new content, generates embeddings, and upserts them into Qdrant. The wiki grows organically.

**Layer 7 — Ground Truth Hierarchy.** This is the critical piece. SOUL.md and rulebook.md tell the agent: *"Injected memory is authoritative. Do not re-verify it. Use it."* Without this layer, all the infrastructure in layers 1-6 gets wasted.

## How to install it

You need three things: Hermes Agent, Docker, and Python 3.11+.

```bash
git clone https://github.com/ClaudioDrews/memory-os.git
cd memory-os

cp .env.example .env
# Fill in your values — at minimum OPENROUTER_API_KEY and REDIS_PASSWORD
# Generate a Redis password: openssl rand -hex 16

docker compose --env-file .env -f docker/docker-compose.yml up -d
```

That starts three services:
- **Qdrant** on port 6333 — vector database
- **Redis** on port 6379 — job queue for ARQ worker
- **ARQ Worker** — processes memory ingestion, reflection cycles, and wiki file processing

The worker needs an OpenRouter API key for embeddings. It mounts your Hermes home directory (`~/.hermes`) and wiki path so it can read session data and write memory.

**What to configure in .env:**

| Variable | Required | Purpose |
|----------|----------|---------|
| OPENROUTER_API_KEY | Yes | Embeddings + LLM extraction |
| REDIS_PASSWORD | Yes | Redis auth (any string) |
| FABRIC_DIR | Yes | Where fabric entries live |
| VAULT_PATH | Yes | Root for wiki and backfill scripts |
| WIKI_ROOT | Yes | Wiki directory for Qdrant ingestion |
| HERMES_HOME | Yes | Usually ~/.hermes |
| ICARUS_EXTRACTION_MAX_TOKENS | Recommended | Set to 4096 (default 1024 is too small) |
| ICARUS_EXTRACTION_MODEL | Recommended | Any OpenRouter chat model |

**Alternative:** If you are not using Docker, the repo has a setup/ directory with scripts for manual installation, though Docker is the recommended path.

## How to use it

Once the stack is running, the system works automatically:

1. **Every conversation starts with surgical recall.** Before each LLM call, Memory OS pulls relevant entries from Fabric, Qdrant, Sessions, and Facts — each gated by a relevance threshold, deduplicated, and filtered for trivial social messages.

2. **After every response, new learnings get extracted.** The post-processing pipeline captures decisions, preferences, and facts from the conversation and writes them to the appropriate layer.

3. **On session end, a deeper extraction runs.** The full session gets analyzed for patterns, entity relationships, and knowledge that should go into the wiki.

4. **The reflection cron runs every 2 hours.** It scans Qdrant for memories with fewer than 3 reflections, batches them, sends them to Ollama for pattern analysis, and stores the insights as new Qdrant points.

5. **The decay scanner runs weekly.** It ages out stale entries and merges near-duplicate memories.

You do not manage the layers individually. The system manages itself. Your job is to fill the starting files (MEMORY.md, USER.md, CREATIVE.md, SOUL.md) and let the pipeline do the rest.

## What to expect in the first day

**First 30 minutes:** Docker pulls images, containers start. Qdrant has an empty collection. Redis is idle. The worker registers itself.

**First session:** The pre-call hook fires but finds nothing — no embedded memories, no fabric entries, no wiki content. This is expected. The agent runs normally. Post-processing captures the session.

**After 2-3 sessions:** Fabric entries start appearing. The wiki ingest has something to work with. Qdrant fills its first vectors.

**After the first reflection cycle (2 hours):** The system starts finding patterns between sessions. This is when Memory OS becomes useful — not before.

**First 24 hours:** The decay scanner runs its first pass. Semantic dedup merges obvious duplicates. The Ground Truth hierarchy ensures the agent uses what it has instead of re-discovering it.

## What it is not good for

Memory OS is infrastructure. That comes with tradeoffs:

- **Heavy setup.** Docker, Qdrant, Redis, ARQ Worker, Ollama — this is not a one-command install. You need Docker running and enough RAM for the stack (2-3 GB minimum).

- **Brand new.** The repo is two days old. 4 commits. Things will change fast. Expect breaking changes.

- **Forked Icarus plugin.** The fabric layer forks the official Icarus plugin. It is not upstream-compatible. Updates from the official plugin will need manual merge.

- **No published benchmarks.** The architecture is well-designed but there are no public numbers on recall quality, latency improvement, or token savings.

## Why it matters anyway

The agent memory problem is not a model problem. It is an architecture problem. Every agent framework ships some memory system. None of them ship a layered, self-curating, trust-scored, ground-truth-enforced memory operating system.

Memory OS is important because it treats memory the way an OS treats storage — as a managed resource with caching (workspace files), indexing (FTS5 + Qdrant), archival (decay scanner), deduplication (semantic merge), and an explicit hierarchy of authority (Ground Truth).

Whether this specific stack survives or not, the approach will. Agents that remember better *are* better. The architecture race just got interesting.
