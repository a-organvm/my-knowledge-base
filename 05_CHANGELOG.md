# 05: Changelog (Detailed)

**Atom ID:** changelog-detailed
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Purpose

This changelog provides a detailed, phase-by-phase record of features, fixes, and changes. For the user-facing summary, see `CHANGELOG.md` at the project root.

## Phase 1: Foundation (Export + Atomization)

### Features
- Multi-source export pipeline (Claude.app, Gemini, ChatGPT, local markdown)
- Playwright-based browser automation for Claude.app and Gemini scraping
- ChatGPT JSON export parser
- Local markdown/text file ingestion
- Five-strategy atomization engine:
  - Message-level decomposition
  - Code block extraction
  - Markdown semantic chunking
  - PDF sliding window
  - Single-chunk fallback
- Semantic chunker with boundary detection and confidence scoring
- Unit enrichment pipeline: type classification, tag generation, category assignment, keyword extraction
- SQLite database with FTS5 full-text search index
- CLI tools for export and search

### Infrastructure
- TypeScript project setup (strict mode, ESM)
- Vitest test framework
- Database migration system
- npm scripts for all operations

## Phase 2: Semantic Intelligence (Vector Search)

### Features
- OpenAI embedding generation (text-embedding-3-small, 1536 dimensions)
- ChromaDB vector database integration
- Semantic search via embedding similarity
- Hybrid search combining FTS5 + semantic via Reciprocal Rank Fusion (RRF)
- Configurable search weighting (FTS vs. semantic balance)
- Batch embedding generation with progress tracking

### Infrastructure
- OpenAI SDK integration
- ChromaDB client configuration
- Embedding cost tracking

## Phase 3: Claude Intelligence (Advanced Analysis)

### Features
- InsightExtractor: LLM-powered insight discovery across the corpus
- SmartTagger: Context-aware tagging beyond keyword detection
- RelationshipDetector: Cross-conversation relationship discovery
- ConversationSummarizer: Multi-level conversation summaries
- Batch processor with checkpoints and resumability
- Prompt caching (90% cost savings)
- Token usage tracking and cost reporting

### Infrastructure
- Anthropic SDK integration with prompt caching
- Batch processor with progress bars and checkpoint files
- New database tables: unit_relationships, insights

## Phase 3+: REST API

### Features
- 38 REST API endpoints across 8 categories:
  - Core CRUD (12 endpoints)
  - Search (6 endpoints)
  - Intelligence (6 endpoints)
  - Graph (8 endpoints)
  - Deduplication (4 endpoints)
  - Export (5 endpoints)
  - WebSocket (3 endpoints)
  - Rate Limiting (4 endpoints)
- Consistent response format: `{ success, data, pagination?, timestamp }`
- Rate limiting (configurable per endpoint)
- CORS configuration
- Optional authentication middleware
- Audit logging for write operations

### Infrastructure
- Express.js server
- WebSocket support
- Request validation middleware

## Phase 4: Web UI

### Features
- React SPA with tabbed interface
- Search tab: hybrid search with filters and result display
- Graph tab: D3.js knowledge graph visualization
- Tags tab: tag browsing and filtering
- Settings tab: system stats, API status, configuration
- Responsive design

### Infrastructure
- React build pipeline
- Static file serving from Express
- D3.js integration

## Phase 5: Advanced Ingestion

### Features
- Apple Notes integration (via JXA/osascript)
- iCloud Drive document indexing
- Browser bookmark ingestion (Chrome, Safari)
- Source configuration via `config/sources.yaml`

### Infrastructure
- macOS permission handling
- JXA scripting interface

## Phase 6: Production (Planned)

### Features (Planned)
- Docker deployment (Dockerfile + docker-compose.yml)
- Fly.io deployment (fly.toml)
- GitHub Actions CI/CD
- Automated backup scheduling
- Health monitoring

### Infrastructure (Planned)
- Docker multi-stage build
- Fly.io persistent volumes
- CI/CD pipeline

## Related Documents

- `CHANGELOG.md` -- User-facing changelog summary
- `DEVELOPMENT_ROADMAP.md` -- 235-item task list
- `06_CHANGE_AUDIT.md` -- Architectural change audit
