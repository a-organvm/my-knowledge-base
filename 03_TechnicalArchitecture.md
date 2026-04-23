# 03: Technical Architecture

**Atom ID:** technical-architecture
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ React UI │  │   CLI    │  │ REST API │  │WebSocket │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       └──────────────┴─────────────┴─────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Export      │  │   Search     │  │ Intelligence │      │
│  │   Pipeline    │  │   Engine     │  │   Layer      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐      │
│  │  Atomizer    │  │ Hybrid Search│  │ Claude       │      │
│  │  (5 strat.)  │  │  (FTS+Sem)   │  │ Service      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │  ChromaDB    │  │ File System  │      │
│  │  (FTS5)      │  │  (Vectors)   │  │  (Backups)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Runtime | Node.js (v20+ LTS) | Server-side JavaScript execution |
| Language | TypeScript (strict, ESM) | Type safety and module system |
| Database | SQLite via better-sqlite3 | Primary data store + FTS5 search |
| Vector DB | ChromaDB | Embedding storage and similarity search |
| Embeddings | OpenAI text-embedding-3-small | 1536-dimensional vectors |
| Intelligence | Anthropic Claude (via SDK) | Insight extraction, tagging, relationships |
| Web Framework | Express.js | REST API + static file serving |
| Frontend | React | Tabbed SPA (Search, Graph, Tags, Settings) |
| Visualization | D3.js | Knowledge graph visualization |
| Testing | Vitest | Unit and integration tests |
| Scraping | Playwright | Browser automation for Claude.app and Gemini |

### Data Flow

```
SOURCE → PARSE → NORMALIZE → ATOMIZE → ENRICH → STORE → INDEX → SERVE
  │         │         │          │         │        │        │       │
  │     Format-    Conversation/ Type     Tags    SQLite   FTS5    API
  │     specific   Document    classify   +       +        +      +
  │     parser     interface   +keyword  category ChromaDB Vector  Web
  │                            extract                            UI
  │
  └── Claude.app (Playwright)
  └── Gemini (Playwright)
  └── ChatGPT (JSON parse)
  └── Local files (fs.readFile)
  └── Apple Notes (JXA/osascript)
```

### Module Dependencies

```
types.ts (no deps)
  ├── database.ts (better-sqlite3)
  ├── atomizer.ts (types)
  │   └── semantic-chunker.ts
  │   └── chunking-strategies.ts
  ├── document-atomizer.ts (types, chunking-strategies)
  ├── sources/
  │   ├── manager.ts (types)
  │   ├── claude.ts (playwright)
  │   ├── gemini.ts (playwright)
  │   ├── chatgpt.ts (types)
  │   └── local.ts (fs)
  ├── embeddings-service.ts (openai)
  ├── vector-database.ts (chromadb)
  ├── hybrid-search.ts (database, vector-database)
  ├── claude-service.ts (@anthropic-ai/sdk)
  │   ├── insight-extractor.ts
  │   ├── smart-tagger.ts
  │   ├── relationship-detector.ts
  │   └── conversation-summarizer.ts
  ├── batch-processor.ts (types)
  ├── api.ts (express, database, hybrid-search, claude-service)
  └── web-server.ts (api, static files)
```

### Concurrency Model

- **Single-threaded Node.js event loop** for API serving and search
- **Async/await** for I/O-bound operations (API calls, file reads)
- **Configurable parallelism** for batch operations (`--parallel N`)
- **Checkpoint-based resumability** for interrupted batch jobs
- **No worker threads** (CPU-bound operations are fast enough single-threaded)

### Error Handling Strategy

1. **API errors:** Wrapped in consistent response format `{ success: false, error: string }`
2. **Batch errors:** Logged and skipped; processing continues with remaining items
3. **Database errors:** Fail-fast with descriptive error message
4. **External API errors:** Retry with exponential backoff (3 attempts)
5. **Source scraping errors:** Logged with conversation ID; non-fatal to batch

## Related Documents

- `docs/ARCHITECTURE.md` -- Detailed architecture with ASCII diagrams
- `docs/DATABASE_SCHEMA.md` -- Database table definitions
- `docs/API_DOCUMENTATION.md` -- API endpoint reference
- `02-cal-architecture.md` -- Content Atomization Layer detail
