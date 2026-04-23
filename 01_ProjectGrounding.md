# 01: Project Grounding

**Atom ID:** project-grounding
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | My Knowledge Base |
| **Organ** | ORGAN-I (Theoria) |
| **Organization** | organvm-i-theoria |
| **Tier** | standard |
| **Status** | GRADUATED |
| **License** | MIT |
| **Language** | TypeScript (ESM) |
| **Stack** | Node.js, SQLite, ChromaDB, Anthropic SDK, OpenAI SDK, Vitest |

## Problem Domain

Personal epistemological infrastructure. The system converts AI conversations into durable, searchable, interconnected knowledge with multi-modal retrieval and LLM-powered intelligence extraction.

## Position Within ORGANVM

```
ORGAN-I (Theoria) -- Foundational theory, recursive engines, symbolic computing
  └── my-knowledge-base -- Epistemological infrastructure for AI conversation corpus
      ├── Produces → theory (for downstream organs)
      ├── Siblings: recursive-engine, organon-noumenon, auto-revision-engine, ...
      └── No upstream dependencies (foundational layer)
```

The knowledge base is a foundational component of ORGAN-I. It generates the raw knowledge substrate that downstream organs (Poiesis, Ergon) consume through their own processing pipelines.

## Stakeholders

| Stakeholder | Role | Relationship |
|-------------|------|-------------|
| Operator (Anthony Padavano) | Primary user, architect | Direct |
| ORGANVM system | Consumer of theory output | Produces → theory |
| Omni-Dromenon Engine | Consumer of content atoms | Via REST API |

## Success Criteria

1. All four AI platforms (Claude, Gemini, ChatGPT, local) are exportable
2. Atomization produces self-contained, typed, tagged units
3. Hybrid search returns relevant results (MRR@10 > 0.7)
4. Intelligence extraction surfaces non-obvious patterns (>30% novelty rate)
5. System operates within cost constraints ($1/1,000 ops ceiling)

## Current State

- **Development progress:** 187/235 tasks (80%)
- **Test coverage:** 62.7% (1,463 tests passing)
- **Database:** ~50,000 atomic units
- **API:** 38 endpoints (REST + WebSocket)
- **Web UI:** React SPA with D3 graph visualization

## Constraints

1. **Single operator:** Not a multi-tenant system. All design decisions optimize for individual depth.
2. **Local-first:** SQLite + local ChromaDB. No cloud database dependency.
3. **Cost-conscious:** Prompt caching required for all LLM calls. No unbounded API costs.
4. **Memory-constrained environment:** Development machine has 16 GB RAM. Batch operations must be parallelism-aware.

## Related Documents

- `README.md` -- Public-facing overview
- `CLAUDE.md` -- Agent context for Claude Code
- `seed.yaml` -- ORGANVM automation contract
- `DEVELOPMENT_ROADMAP.md` -- 235-item task list
