# 06: Change Audit

**Atom ID:** change-audit
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus
**Decision Context:** Option A selected -- "Create manifesto + governance framework now"

---

## Purpose

This document maintains a chronological record of significant architectural, data model, and behavioral changes to the knowledge base system. Each entry records what changed, why, what it replaced, and what downstream effects were observed.

## Audit Format

Each entry follows this structure:

| Field | Description |
|-------|-------------|
| **Date** | When the change was applied |
| **Change ID** | Sequential identifier (CHG-NNN) |
| **Category** | `architecture`, `data-model`, `api`, `search`, `intelligence`, `deployment`, `security` |
| **Description** | What changed |
| **Rationale** | Why the change was made |
| **Replaced** | What the previous behavior was |
| **Downstream** | What was affected by this change |
| **Reversible** | Whether the change can be rolled back |

---

## Change Log

### CHG-001: Multi-Source Ingestion Pipeline

- **Date:** 2025-12 (Phase 1)
- **Category:** architecture
- **Description:** Added SourceManager with pluggable source interface supporting Claude.app, Gemini, ChatGPT, and local markdown
- **Rationale:** Single-source (Claude-only) limitation prevented corpus unification
- **Replaced:** Direct Claude.app scraper as sole ingestion pathway
- **Downstream:** Atomizer updated to handle normalized Conversation interface from any source
- **Reversible:** Yes (individual sources can be disabled without affecting others)

### CHG-002: Five-Strategy Atomization

- **Date:** 2025-12 (Phase 1)
- **Category:** architecture
- **Description:** Implemented strategy pattern with five chunking strategies dispatched by content type
- **Rationale:** Single-strategy atomization produced inconsistent quality across content types
- **Replaced:** Single monolithic atomization function
- **Downstream:** SemanticChunker introduced as sub-component; guardrails added (min tokens, max chunks)
- **Reversible:** Yes (can revert to single strategy by setting all dispatch to SingleChunkStrategy)

### CHG-003: Vector Search via ChromaDB

- **Date:** 2026-01 (Phase 2)
- **Category:** search
- **Description:** Added OpenAI embeddings (text-embedding-3-small) stored in ChromaDB for semantic search
- **Rationale:** FTS5 alone misses semantic similarity (synonyms, paraphrases, conceptual proximity)
- **Replaced:** FTS5-only search
- **Downstream:** HybridSearch introduced combining FTS5 + semantic via RRF; API endpoints updated
- **Reversible:** Partially (FTS5 remains functional without ChromaDB; semantic/hybrid search degrades)

### CHG-004: Hybrid Search with Reciprocal Rank Fusion

- **Date:** 2026-01 (Phase 2)
- **Category:** search
- **Description:** Combined FTS5 and semantic search results using RRF algorithm with configurable weighting
- **Rationale:** Neither retrieval mode alone produces optimal relevance
- **Replaced:** Separate FTS5 and semantic endpoints with no combination
- **Downstream:** Web UI default search mode changed to hybrid; API `/api/search` defaults to hybrid
- **Reversible:** Yes (weight parameters allow 100% FTS5 or 100% semantic)

### CHG-005: Claude Intelligence Layer (Phase 3)

- **Date:** 2026-01 (Phase 3)
- **Category:** intelligence
- **Description:** Added InsightExtractor, SmartTagger, RelationshipDetector, ConversationSummarizer using Anthropic SDK with prompt caching
- **Rationale:** Corpus contains implicit patterns invisible without LLM analysis
- **Replaced:** No prior intelligence layer
- **Downstream:** New database tables (unit_relationships, insights); new API endpoints; batch processor with checkpoints
- **Reversible:** Yes (intelligence layer is additive; removing it does not affect core search/storage)

### CHG-006: REST API (38 Endpoints)

- **Date:** 2026-01 (Phase 3)
- **Category:** api
- **Description:** Express.js REST API with CRUD, search, intelligence, graph, dedup, export, and WebSocket endpoints
- **Rationale:** Web UI and external consumers need programmatic access
- **Replaced:** CLI-only access
- **Downstream:** Rate limiting, CORS configuration, optional auth middleware
- **Reversible:** No (web UI depends on API)

### CHG-007: React Web UI

- **Date:** 2026-01 (Phase 4)
- **Category:** architecture
- **Description:** Tabbed React SPA with search, graph visualization (D3), tags browser, and settings
- **Rationale:** CLI insufficient for exploratory knowledge browsing and graph visualization
- **Replaced:** CLI as sole interface
- **Downstream:** `npm run web` starts Express server serving both API and static React build
- **Reversible:** Yes (CLI remains fully functional)

---

## Pending Changes

| Change ID | Category | Description | Status |
|-----------|----------|-------------|--------|
| CHG-008 | search | Query suggestion engine based on search analytics | DESIGNED |
| CHG-009 | intelligence | Automated re-embedding pipeline for new atoms | PROPOSED |
| CHG-010 | deployment | GitHub Actions CI/CD for automated testing | PROPOSED |

## Related Documents

- `05_CONTRADICTION_RESOLUTIONS.md` -- Resolutions that motivated several changes
- `05_CHANGELOG.md` -- User-facing changelog
- `DEVELOPMENT_ROADMAP.md` -- 235-item task list
