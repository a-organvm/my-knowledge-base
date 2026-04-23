# 05: Decision Log

**Atom ID:** decision-log
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Purpose

This log records significant technical and architectural decisions with context, alternatives considered, and rationale. Each decision is timestamped and immutable -- new decisions amend, never overwrite, previous entries.

## Decision Format

| Field | Description |
|-------|-------------|
| **DEC-ID** | Sequential identifier |
| **Date** | Decision date |
| **Title** | Brief description |
| **Context** | What prompted the decision |
| **Decision** | What was decided |
| **Alternatives** | What else was considered |
| **Rationale** | Why this option was chosen |
| **Status** | ACTIVE, SUPERSEDED, REVERSED |

---

## Decisions

### DEC-001: TypeScript over Python

- **Date:** 2025-11
- **Context:** Choosing implementation language for the knowledge base
- **Decision:** TypeScript (strict mode, ESM)
- **Alternatives:** Python (with FastAPI), Go, Rust
- **Rationale:** TypeScript provides type safety with JavaScript ecosystem access (Playwright for scraping, better-sqlite3 for SQLite, npm for distribution). Python was a strong candidate but TypeScript's strict mode catches more errors at compile time for this scale of project.
- **Status:** ACTIVE

### DEC-002: SQLite over PostgreSQL

- **Date:** 2025-11
- **Context:** Choosing primary data store
- **Decision:** SQLite via better-sqlite3
- **Alternatives:** PostgreSQL, MongoDB, DuckDB
- **Rationale:** Single-operator system with no concurrent write requirements. SQLite is zero-configuration, file-based (easy backup), and includes FTS5 for full-text search. PostgreSQL adds operational complexity without benefit for a single-user deployment.
- **Status:** ACTIVE

### DEC-003: OpenAI Embeddings over Local Models

- **Date:** 2025-12
- **Context:** Choosing embedding model for semantic search
- **Decision:** OpenAI text-embedding-3-small (1536 dimensions)
- **Alternatives:** sentence-transformers (local), Cohere, Voyage AI
- **Rationale:** text-embedding-3-small provides high-quality embeddings at $0.02/1M tokens. Local models (sentence-transformers) require GPU or produce lower quality on CPU. The cost is negligible for a personal corpus (<$1 for 50,000 units).
- **Status:** ACTIVE

### DEC-004: ChromaDB over Pinecone/Weaviate

- **Date:** 2025-12
- **Context:** Choosing vector database for embedding storage
- **Decision:** ChromaDB (local, open-source)
- **Alternatives:** Pinecone (managed), Weaviate (self-hosted), pgvector
- **Rationale:** Local-first principle requires local vector storage. ChromaDB runs embedded in the Node.js process, requires no external service, and provides a clean Python/JS SDK. Pinecone violates local-first. Weaviate adds operational complexity.
- **Status:** ACTIVE

### DEC-005: Reciprocal Rank Fusion for Hybrid Search

- **Date:** 2026-01
- **Context:** Combining FTS5 and semantic search results
- **Decision:** RRF (Cormack et al., 2009)
- **Alternatives:** Linear combination of scores, learned-to-rank, CombMNZ
- **Rationale:** RRF requires no score normalization (FTS5 and ChromaDB use different scoring scales). It is simple to implement, well-studied, and performs comparably to more complex fusion methods for this use case.
- **Status:** ACTIVE

### DEC-006: Claude over GPT-4 for Intelligence Layer

- **Date:** 2026-01
- **Context:** Choosing LLM for Phase 3 intelligence extraction
- **Decision:** Claude (via Anthropic SDK) with prompt caching
- **Alternatives:** GPT-4 (via OpenAI SDK), Gemini (via Google SDK), local LLM
- **Rationale:** Prompt caching provides 90% cost reduction for batch operations (same system prompt across hundreds of units). Claude's long context window handles large conversation summaries. The ORGANVM system is built on Claude infrastructure.
- **Status:** ACTIVE

### DEC-007: Express over Fastify/Hono

- **Date:** 2026-01
- **Context:** Choosing web framework for REST API
- **Decision:** Express.js
- **Alternatives:** Fastify, Hono, Koa
- **Rationale:** Express is the most widely understood Node.js framework. The API has 38 endpoints but modest throughput requirements (single operator). Fastify's performance advantage is irrelevant at this scale. Express's middleware ecosystem (CORS, rate limiting, auth) is mature.
- **Status:** ACTIVE

### DEC-008: Vitest over Jest

- **Date:** 2025-11
- **Context:** Choosing test framework
- **Decision:** Vitest
- **Alternatives:** Jest, Mocha, Node.js native test runner
- **Rationale:** Vitest is ESM-native (no transformation needed for ESM imports), fast, and provides a UI mode for interactive debugging. Jest's ESM support is still experimental and requires configuration.
- **Status:** ACTIVE

### DEC-009: React over Vanilla JS for Web UI

- **Date:** 2026-01
- **Context:** Choosing frontend framework for web UI
- **Decision:** React (SPA with tabbed interface)
- **Alternatives:** Vanilla JS, Svelte, htmx
- **Rationale:** D3.js graph visualization requires DOM manipulation that benefits from React's component model. The tabbed interface (Search, Graph, Tags, Settings) maps naturally to React components. Vanilla JS was prototyped first but became unwieldy at the Settings tab complexity level.
- **Status:** ACTIVE

---

## Decision Statistics

| Status | Count |
|--------|-------|
| ACTIVE | 9 |
| SUPERSEDED | 0 |
| REVERSED | 0 |

## Related Documents

- `05_CONTRADICTION_RESOLUTIONS.md` -- Decisions that resolved contradictions
- `06_CHANGE_AUDIT.md` -- Changes resulting from these decisions
- `01-core-principles.md` -- Principles that constrained these decisions
