# Personal Knowledge Database System

**Project Type:** Node.js / TypeScript / SQLite
**Purpose:** A comprehensive system for exporting, atomizing, archiving, and intelligently searching conversation history from Claude.ai.

## Project Overview

This project is a sophisticated knowledge management tool that transforms raw conversation exports from Claude into a structured, searchable database. It evolves in phases, adding layers of intelligence:

1.  **Phase 1 (Foundation):** Automated export via Playwright, atomization into "Knowledge Units" (markdown/JSON), and SQLite storage with Full-Text Search (FTS5).
2.  **Phase 2 (Semantic Intelligence):** Vector embeddings (OpenAI), semantic search, and hybrid search (Reciprocal Rank Fusion) using ChromaDB.
3.  **Phase 3 (Claude Intelligence):** Intelligent insight extraction, smart auto-tagging, relationship detection, and summarization using the Anthropic API.
4.  **Phase 4 (Web UI & Export):** Visual knowledge graph, hybrid search interface, REST API, and Obsidian export.
5.  **Phase 5 (Omni-Source Ingestion):** Unified ingestion architecture for ChatGPT, Gemini, Grok, Apple Notes, and cloud drives (Dropbox/Drive/iCloud).

## Key Technologies

*   **Runtime:** Node.js, TypeScript (`tsx`)
*   **Database:** SQLite (`better-sqlite3`), ChromaDB (Vector Store)
*   **AI/ML:** OpenAI (Embeddings), Anthropic (Intelligence/Insights)
*   **Automation:** Playwright (Browser automation for exports)
- **Federated Knowledge System (Phase 5):** The system has transitioned to a "Zero-Copy" architecture.
    - **Configuration:** `config/sources.yaml` manages "Watch Roots" (Local, Dropbox, iCloud).
    - **Ingestion:** `LocalFileSource` indexes files in-place using stable path hashes.
    - **PDF Support:** Implemented `pdf-parse` for text extraction from binary files.
    - **Real-Time Watcher:** Implemented `chokidar` for live updates (`npm run watch`).
    - **Status:** Dropbox `padavano-mdc` indexed successfully (26 docs). `Local Projects` scanned.
    - **Next:** Semantic Search verification, Apple Notes Adapter.
- A Cigna medical document was recovered from local Documents and is staged in 'production/rolling_submissions/B02_MEDICAL'.
- An Omni-Search was completed across iCloud, local directories, and Mail.app, resulting in 78 prioritized medical email leads and 'key' files dropped in all visited directories for future sorting.

## Setup & Configuration

Ensure you have a `.env` file in the root directory with the following keys (see `.env.example`):

```env
OPENAI_API_KEY=sk-...      # Required for Phase 2 (Embeddings)
ANTHROPIC_API_KEY=sk-...   # Required for Phase 3 (Intelligence)
```

## Core Workflows & Usage

### 1. Exporting Conversations
Automate the retrieval of chat history from Claude.app.

```bash
# Automated export (Headless)
npm run export:dev
```

### 2. Cloud Sync (Rclone)
Sync files from Dropbox, Drive, etc. into the system.

1.  Install Rclone: `brew install rclone`
2.  Configure remotes: `rclone config`
3.  Edit `scripts/sync-cloud.sh` to map your folders.
4.  Run sync:
    ```bash
    npm run sync
    ```

### 3. Searching Knowledge
Retrieve information using different search strategies.

```bash
# Full-Text Search (Fast, Keyword-based)
npm run search "search query"

# Semantic Search (Concept-based using embeddings)
npm run search:semantic "search query"

# Hybrid Search (Recommended: Combines FTS + Semantic)
npm run search:hybrid "search query"
```

### 3. Enhancing Knowledge (Phase 3)
Apply AI to extract structure and meaning from existing data.

```bash
# Extract key insights
npm run extract-insights all --save

# Generate smart tags based on context
npm run smart-tag --limit 100 --save

# Detect relationships between units
npm run find-relationships --limit 10 --save

# Summarize conversations
npm run summarize all --save
```

### 4. Database Maintenance

```bash
# Generate embeddings for existing non-vectorized data
npm run generate-embeddings -- --yes
```

## Directory Structure

*   `src/`: TypeScript source code.
    *   `atomizer.ts`: Logic for breaking conversations into atomic units.
    *   `database.ts`: SQLite interaction layer.
    *   `export.ts`: Main export script using Playwright.
    *   `search*.ts`: Various search implementations.
    *   `*-cli.ts`: CLI entry points for specific tasks.
*   `raw/`: Raw JSON exports from Claude.app.
*   `atomized/`: Processed data in human/machine-readable formats.
    *   `markdown/`: Knowledge units as Markdown files.
    *   `json/`: Knowledge units as JSON files.
*   `db/`: SQLite database file (`knowledge.db`).

## Development

*   **Build:** `npm run build` (Compiles TS to `dist/`)
*   **Dev Run:** Use `npm run dev` or run specific scripts via `tsx` (e.g., `tsx src/index.ts`).

## Documentation References

*   **[PHASE2.md](PHASE2.md)**: Semantic Search Implementation.
*   **[PHASE3.md](PHASE3.md)**: Claude Intelligence Layer.
*   **[PHASE4.md](PHASE4.md)**: Web UI & Export.
*   **[PHASE5.md](PHASE5.md)**: Omni-Source Ingestion Roadmap.

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-I (Theory) | **Tier:** standard | **Status:** PUBLIC_PROCESS
**Org:** `organvm-i-theoria` | **Repo:** `my-knowledge-base`

### Edges
- **Produces** → `unspecified`: theory

### Siblings in Theory
`recursive-engine--generative-entity`, `organon-noumenon--ontogenetic-morphe`, `auto-revision-epistemic-engine`, `narratological-algorithmic-lenses`, `call-function--ontological`, `sema-metra--alchemica-mundi`, `system-governance-framework`, `cognitive-archaelogy-tribunal`, `a-recursive-root`, `radix-recursiva-solve-coagula-redi`, `.github`, `nexus--babel-alexandria-`, `reverse-engine-recursive-run`, `4-ivi374-F0Rivi4`, `cog-init-1-0-` ... and 4 more

### Governance
- Foundational theory layer. No upstream dependencies.

*Last synced: 2026-03-08T20:11:34Z*

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
| system | any | research-standards | METADOC: Architectural Typology & Research Standards |
| system | any | sop-ecosystem | METADOC: SOP Ecosystem — Taxonomy, Inventory & Coverage |
| system | any | autopoietic-systems-diagnostics | SOP: Autopoietic Systems Diagnostics (The Mirror of Eternity) |
| system | any | cicd-resilience-and-recovery | SOP: CI/CD Pipeline Resilience & Recovery |
| system | any | cross-agent-handoff | SOP: Cross-Agent Session Handoff |
| system | any | document-audit-feature-extraction | SOP: Document Audit & Feature Extraction |
| system | any | essay-publishing-and-distribution | SOP: Essay Publishing & Distribution |
| system | any | market-gap-analysis | SOP: Full-Breath Market-Gap Analysis & Defensive Parrying |
| system | any | pitch-deck-rollout | SOP: Pitch Deck Generation & Rollout |
| system | any | promotion-and-state-transitions | SOP: Promotion & State Transitions |
| system | any | repo-onboarding-and-habitat-creation | SOP: Repo Onboarding & Habitat Creation |
| system | any | research-to-implementation-pipeline | SOP: Research-to-Implementation Pipeline (The Gold Path) |
| system | any | security-and-accessibility-audit | SOP: Security & Accessibility Audit |
| system | any | session-self-critique | session-self-critique |
| system | any | source-evaluation-and-bibliography | SOP: Source Evaluation & Annotated Bibliography (The Refinery) |
| system | any | stranger-test-protocol | SOP: Stranger Test Protocol |
| system | any | strategic-foresight-and-futures | SOP: Strategic Foresight & Futures (The Telescope) |
| system | any | typological-hermeneutic-analysis | SOP: Typological & Hermeneutic Analysis (The Archaeology) |
| unknown | any | gpt-to-os | SOP_GPT_TO_OS.md |
| unknown | any | index | SOP_INDEX.md |
| unknown | any | obsidian-sync | SOP_OBSIDIAN_SYNC.md |

Linked skills: evaluation-to-growth


**Prompting (Google)**: context 1M tokens (Gemini 1.5 Pro), format: markdown, thinking: thinking mode (thinkingConfig)

<!-- ORGANVM:AUTO:END -->


## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.
