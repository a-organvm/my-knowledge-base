# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Status

**See [`DEVELOPMENT_ROADMAP.md`](./DEVELOPMENT_ROADMAP.md) for the complete 235-item task list.**

Current status: **187/235 tasks completed (80%)**
- Phase 1-3 + API: 100% complete
- Web UI: Complete (20/20)

## Project Overview

A TypeScript knowledge base that exports Claude.app conversations, atomizes them into knowledge units, and provides multi-layered search and AI-powered intelligence extraction.

**Stack:** Node.js + TypeScript (ESM) | SQLite + ChromaDB | Anthropic SDK + OpenAI SDK | Vitest

## Build & Development Commands

```bash
# Build & Run
npm run build              # Compile TypeScript to dist/
npm run dev                # Run with tsx (development)
npm run start              # Run compiled JavaScript
npm run web                # Start web server

# Database
npm run migrate            # Run database migrations
npm run prepare-db         # migrate + seed (runs automatically before start/web/test)

# Export & Ingestion
npm run export:dev         # Export conversations from claude.app (browser required)
npm run export:dev -- --source=gemini   # Export from specific source only
npm run generate-embeddings -- --yes    # Generate embeddings for all units

# Search
npm run search "query"           # Full-text search (FTS5)
npm run search:semantic "query"  # Semantic search via embeddings
npm run search:hybrid "query"    # Hybrid search (FTS + semantic combined)

# Testing
npm test                   # Run all tests
npm test -- src/api.test.ts         # Run single test file
npm test -- --watch        # Watch mode
npm run test:ui            # Vitest UI
npm run test:coverage      # Coverage report
```

## Phase 3 Intelligence Commands (Claude-powered)

```bash
# Core batch operations (progress bars, checkpoints, resumability)
npm run extract-insights all --save --parallel 3    # Extract insights
npm run smart-tag --limit 100 --save --parallel 4   # Context-aware tagging
npm run find-relationships --save                   # Detect connections
npm run summarize all --save                        # Summarization
```

## Architecture

### Three-Phase System

**Phase 1: Foundation** - Export & Atomization
- Playwright scrapes Claude.app/Gemini or reads local markdown
- SourceManager ingests from multiple sources
- KnowledgeAtomizer breaks content into atomic units (5 strategies)

**Phase 2: Semantic Intelligence** - Vector Search
- OpenAI text-embedding-3-small vectors stored in ChromaDB
- HybridSearch combines FTS5 + semantic via Reciprocal Rank Fusion

**Phase 3: Claude Intelligence** - Advanced Analysis
- InsightExtractor, SmartTagger, RelationshipDetector, ConversationSummarizer
- Prompt caching: 90% token savings (~$0.034 vs $0.32 per operation)

### Data Model

**AtomicUnit** (core entity)
```typescript
{
  id: UUID
  type: 'insight' | 'code' | 'question' | 'reference' | 'decision'
  title: string               // auto-generated from first line
  content: string             // main knowledge
  context: string             // surrounding context
  tags: string[]              // auto-generated
  category: 'programming' | 'writing' | 'research' | 'design' | 'general'
  timestamp: Date
  embedding?: number[]        // Phase 2: vector embedding
  conversationId?: string     // source reference
  relatedUnits: string[]      // Phase 3: connections
}
```

### Database Tables
- `atomic_units` - Core knowledge units
- `units_fts` - Full-text search index (SQLite FTS5)
- `tags`, `unit_tags` - Tagging relationships
- `unit_relationships` - Phase 3: relationship graph
- `conversations`, `documents` - Source metadata

## Project Structure

```
src/
├── database.ts              # SQLite operations, schema
├── atomizer.ts              # Conversation atomization
├── document-atomizer.ts     # Document atomization
├── types.ts                 # TypeScript interfaces
├── export.ts                # Main orchestration
├── sources/                 # Source integrations
│   ├── manager.ts           # Unified ingestion
│   ├── claude.ts            # Claude.app scraper
│   ├── gemini.ts            # Gemini scraper
│   ├── chatgpt.ts           # ChatGPT export parser
│   └── local.ts             # Local markdown
├── analytics/               # Search analytics
│   ├── spell-checker.ts
│   ├── query-suggestions.ts
│   └── search-analytics.ts
├── embeddings-service.ts    # OpenAI embeddings
├── vector-database.ts       # ChromaDB storage
├── hybrid-search.ts         # FTS + semantic (RRF)
├── claude-service.ts        # Anthropic SDK + prompt caching
├── insight-extractor.ts     # Phase 3: insights
├── smart-tagger.ts          # Phase 3: auto-tagging
├── relationship-detector.ts # Phase 3: connections
├── conversation-summarizer.ts
├── batch-processor.ts       # Progress + checkpoints
├── api.ts                   # REST API endpoints
├── web-server.ts            # Express server
└── *-cli.ts                 # CLI entry points
```

## Key Patterns

### Atomization Strategy
1. Infers unit type from content (question marks → 'question', code blocks → 'code')
2. Auto-generates titles from first line (80 char max)
3. Extracts keywords via frequency analysis
4. Auto-tags by detecting technologies/languages
5. Categorizes into 5 categories

### Cost Optimization
- **Embeddings**: ~$0.02 per 1M tokens
- **Claude Phase 3**: Prompt caching at 0.1x read rate → 90% savings
- Track usage via `ClaudeService.getTokenStats()`

### Adding New Features

**New Phase 3 Analyzer:**
1. Create class similar to InsightExtractor
2. Use ClaudeService for API calls with caching
3. Add CLI script in `src/<name>-cli.ts`
4. Track tokens via getTokenStats()

**New Source:**
1. Add in `src/sources/` implementing KnowledgeSource interface
2. Register in SourceManager
3. Normalize output to Conversation or KnowledgeDocument

## REST API (38 endpoints)

See [`docs/API_ENDPOINTS_SUMMARY.md`](./docs/API_ENDPOINTS_SUMMARY.md) for full reference.

**Categories:** Core CRUD (12) | Search (6) | Intelligence (6) | Graph (8) | Dedup (4) | Export (5) | WebSocket (3) | Rate Limiting (4)

**Response format:** `{ success, data, pagination?, timestamp }`

## Environment Variables

```bash
OPENAI_API_KEY=     # Required for Phase 2 embeddings
ANTHROPIC_API_KEY=  # Required for Phase 3 Claude intelligence
```

## Documentation

- `docs/API_DOCUMENTATION.md` - API overview
- `docs/ARCHITECTURE.md` - System design
- `docs/DATABASE_SCHEMA.md` - Database structure
- `docs/DEPLOYMENT.md` - Docker and deployment

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-I (Theory) | **Tier:** standard | **Status:** GRADUATED
**Org:** `organvm-i-theoria` | **Repo:** `my-knowledge-base`

### Edges
- **Produces** → `unspecified`: theory

### Siblings in Theory
`recursive-engine--generative-entity`, `organon-noumenon--ontogenetic-morphe`, `auto-revision-epistemic-engine`, `narratological-algorithmic-lenses`, `call-function--ontological`, `sema-metra--alchemica-mundi`, `cognitive-archaelogy-tribunal`, `a-recursive-root`, `radix-recursiva-solve-coagula-redi`, `.github`, `nexus--babel-alexandria`, `4-ivi374-F0Rivi4`, `cog-init-1-0-`, `linguistic-atomization-framework`, `scalable-lore-expert` ... and 6 more

### Governance
- Foundational theory layer. No upstream dependencies.

*Last synced: 2026-03-25T22:27:06Z*

## Session Review Protocol

At the end of each session that produces or modifies files:
1. Run `organvm session review --latest` to get a session summary
2. Check for unimplemented plans: `organvm session plans --project .`
3. Export significant sessions: `organvm session export <id> --slug <slug>`
4. Run `organvm prompts distill --dry-run` to detect uncovered operational patterns

Transcripts are on-demand (never committed):
- `organvm session transcript <id>` — conversation summary
- `organvm session transcript <id> --unabridged` — full audit trail
- `organvm session prompts <id>` — human prompts only


## Active Directives

| Scope | Phase | Name | Description |
|-------|-------|------|-------------|
| system | any | prompting-standards | Prompting Standards |
| system | any | research-standards-bibliography | APPENDIX: Research Standards Bibliography |
| system | any | phase-closing-and-forward-plan | METADOC: Phase-Closing Commemoration & Forward Attack Plan |
| system | any | research-standards | METADOC: Architectural Typology & Research Standards |
| system | any | sop-ecosystem | METADOC: SOP Ecosystem — Taxonomy, Inventory & Coverage |
| system | any | autonomous-content-syndication | SOP: Autonomous Content Syndication (The Broadcast Protocol) |
| system | any | autopoietic-systems-diagnostics | SOP: Autopoietic Systems Diagnostics (The Mirror of Eternity) |
| system | any | background-task-resilience | background-task-resilience |
| system | any | cicd-resilience-and-recovery | SOP: CI/CD Pipeline Resilience & Recovery |
| system | any | community-event-facilitation | SOP: Community Event Facilitation (The Dialectic Crucible) |
| system | any | context-window-conservation | context-window-conservation |
| system | any | conversation-to-content-pipeline | SOP — Conversation-to-Content Pipeline |
| system | any | cross-agent-handoff | SOP: Cross-Agent Session Handoff |
| system | any | cross-channel-publishing-metrics | SOP: Cross-Channel Publishing Metrics (The Echo Protocol) |
| system | any | data-migration-and-backup | SOP: Data Migration and Backup Protocol (The Memory Vault) |
| system | any | document-audit-feature-extraction | SOP: Document Audit & Feature Extraction |
| system | any | dynamic-lens-assembly | SOP: Dynamic Lens Assembly |
| system | any | essay-publishing-and-distribution | SOP: Essay Publishing & Distribution |
| system | any | formal-methods-applied-protocols | SOP: Formal Methods Applied Protocols |
| system | any | formal-methods-master-taxonomy | SOP: Formal Methods Master Taxonomy (The Blueprint of Proof) |
| system | any | formal-methods-tla-pluscal | SOP: Formal Methods — TLA+ and PlusCal Verification (The Blueprint Verifier) |
| system | any | generative-art-deployment | SOP: Generative Art Deployment (The Gallery Protocol) |
| system | any | market-gap-analysis | SOP: Full-Breath Market-Gap Analysis & Defensive Parrying |
| system | any | mcp-server-fleet-management | SOP: MCP Server Fleet Management (The Server Protocol) |
| system | any | multi-agent-swarm-orchestration | SOP: Multi-Agent Swarm Orchestration (The Polymorphic Swarm) |
| system | any | network-testament-protocol | SOP: Network Testament Protocol (The Mirror Protocol) |
| system | any | open-source-licensing-and-ip | SOP: Open Source Licensing and IP (The Commons Protocol) |
| system | any | performance-interface-design | SOP: Performance Interface Design (The Stage Protocol) |
| system | any | pitch-deck-rollout | SOP: Pitch Deck Generation & Rollout |
| system | any | polymorphic-agent-testing | SOP: Polymorphic Agent Testing (The Adversarial Protocol) |
| system | any | promotion-and-state-transitions | SOP: Promotion & State Transitions |
| system | any | recursive-study-feedback | SOP: Recursive Study & Feedback Loop (The Ouroboros) |
| system | any | repo-onboarding-and-habitat-creation | SOP: Repo Onboarding & Habitat Creation |
| system | any | research-to-implementation-pipeline | SOP: Research-to-Implementation Pipeline (The Gold Path) |
| system | any | security-and-accessibility-audit | SOP: Security & Accessibility Audit |
| system | any | session-self-critique | session-self-critique |
| system | any | smart-contract-audit-and-legal-wrap | SOP: Smart Contract Audit and Legal Wrap (The Ledger Protocol) |
| system | any | source-evaluation-and-bibliography | SOP: Source Evaluation & Annotated Bibliography (The Refinery) |
| system | any | stranger-test-protocol | SOP: Stranger Test Protocol |
| system | any | strategic-foresight-and-futures | SOP: Strategic Foresight & Futures (The Telescope) |
| system | any | styx-pipeline-traversal | SOP: Styx Pipeline Traversal (The 7-Organ Transmutation) |
| system | any | system-dashboard-telemetry | SOP: System Dashboard Telemetry (The Panopticon Protocol) |
| system | any | the-descent-protocol | the-descent-protocol |
| system | any | the-membrane-protocol | the-membrane-protocol |
| system | any | theoretical-concept-versioning | SOP: Theoretical Concept Versioning (The Epistemic Protocol) |
| system | any | theory-to-concrete-gate | theory-to-concrete-gate |
| system | any | typological-hermeneutic-analysis | SOP: Typological & Hermeneutic Analysis (The Archaeology) |
| unknown | any | gpt-to-os | SOP_GPT_TO_OS.md |
| unknown | any | index | SOP_INDEX.md |
| unknown | any | obsidian-sync | SOP_OBSIDIAN_SYNC.md |

Linked skills: cicd-resilience-and-recovery, continuous-learning-agent, evaluation-to-growth, genesis-dna, multi-agent-workforce-planner, promotion-and-state-transitions, quality-gate-baseline-calibration, repo-onboarding-and-habitat-creation, structural-integrity-audit


**Prompting (Anthropic)**: context 200K tokens, format: XML tags, thinking: extended thinking (budget_tokens)


## Ecosystem Status

- **delivery**: 0/2 live, 0 planned
- **content**: 0/1 live, 0 planned

Run: `organvm ecosystem show my-knowledge-base` | `organvm ecosystem validate --organ I`


## External Mirrors (Network Testament)

- **technical** (2): microsoft/TypeScript, vitest-dev/vitest

Convergences: 20 | Run: `organvm network map --repo my-knowledge-base` | `organvm network suggest`


## Task Queue (from pipeline)

**21** pending tasks | Last pipeline: unknown

- `436374a8d6ad` Validate fixes: Run portfolio quality job locally, test knowledge-base API endpoint [astro, cloudflare, express]
- `c1ed142313f1` Document infrastructure configuration as SOP (Fly.io binding, Cloudflare Pages CORS, relative paths in production) [astro, cloudflare, express]
- `553216f68637` Add CI health check for bundle budget ratchet drift (monitor alignment with vendor sizes) [astro, cloudflare, express]
- `5e7ee0daabe6` Monitor Lighthouse CI performance under new archetype sampling strategy (verify 3-min target maintained) [astro, cloudflare, express]
- `17a5559e7595` API endpoints (URL, method, params, auth) [express, fastapi, vercel]
- `d9dfd047f4f8` Data models (schema, fields, relationships) [express, fastapi, vercel]
- `83755ab667b2` Federation code (client, request patterns, error handling) [express, fastapi, vercel]
- `577578020fe5` Environment variables (required, optional, defaults) [express, fastapi, vercel]
- ... and 13 more

Cross-organ links: 66 | Top tags: `python`, `bash`, `mcp`, `pytest`, `express`

Run: `organvm atoms pipeline --write && organvm atoms fanout --write`


## Entity Identity (Ontologia)

**UID:** `ent_repo_01KKKX3RVHQGN3355V4KTCTJ4R` | **Matched by:** primary_name

Resolve: `organvm ontologia resolve my-knowledge-base` | History: `organvm ontologia history ent_repo_01KKKX3RVHQGN3355V4KTCTJ4R`


## Live System Variables (Ontologia)

| Variable | Value | Scope | Updated |
|----------|-------|-------|---------|
| `active_repos` | 64 | global | 2026-03-25 |
| `archived_repos` | 54 | global | 2026-03-25 |
| `ci_workflows` | 106 | global | 2026-03-25 |
| `code_files` | 0 | global | 2026-03-25 |
| `dependency_edges` | 60 | global | 2026-03-25 |
| `operational_organs` | 8 | global | 2026-03-25 |
| `published_essays` | 29 | global | 2026-03-25 |
| `repos_with_tests` | 0 | global | 2026-03-25 |
| `sprints_completed` | 33 | global | 2026-03-25 |
| `test_files` | 0 | global | 2026-03-25 |
| `total_organs` | 8 | global | 2026-03-25 |
| `total_repos` | 127 | global | 2026-03-25 |
| `total_words_formatted` | 0 | global | 2026-03-25 |
| `total_words_numeric` | 0 | global | 2026-03-25 |
| `total_words_short` | 0K+ | global | 2026-03-25 |

Metrics: 9 registered | Observations: 15536 recorded
Resolve: `organvm ontologia status` | Refresh: `organvm refresh`


## System Density (auto-generated)

AMMOI: 56% | Edges: 41 | Tensions: 33 | Clusters: 5 | Adv: 7 | Events(24h): 23754
Structure: 8 organs / 127 repos / 1654 components (depth 17) | Inference: 98% | Organs: META-ORGANVM:64%, ORGAN-I:55%, ORGAN-II:47%, ORGAN-III:55% +4 more
Last pulse: 2026-03-25T22:27:04 | Δ24h: +3.5% | Δ7d: n/a


## Dialect Identity (Trivium)

**Dialect:** FORMAL_LOGIC | **Classical Parallel:** Logic | **Translation Role:** The Grammar — defines well-formedness in any dialect

Strongest translations: III (formal), IV (formal), META (formal)

Scan: `organvm trivium scan I <OTHER>` | Matrix: `organvm trivium matrix` | Synthesize: `organvm trivium synthesize`

<!-- ORGANVM:AUTO:END -->


## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.
