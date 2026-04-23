# 01: Origin Script

**Atom ID:** origin-script
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## The Genesis Narrative

### The Problem That Started This

It began with a search. A search for something said three months ago in a Claude conversation about recursive data structures. The conversation existed -- somewhere in the Claude.app history, behind a vendor UI, unsearchable by any external tool.

The search failed. The knowledge was lost.

This is not a rare event. It is the default state of AI-assisted knowledge work. Every practitioner who uses Claude, Gemini, or ChatGPT regularly has experienced this: the certainty that a valuable insight exists somewhere in their conversation history, combined with the impossibility of finding it.

### The First Attempt

The first version was a simple scraper. Playwright opening Claude.app, scrolling through conversations, dumping HTML into markdown files. It worked -- conversations were now local files -- but it solved only one of four problems. The files were searchable via `grep`, but:

- Each file was a monolithic blob mixing multiple knowledge types
- There was no way to find semantically similar content across files
- The corpus grew but revealed nothing about its own patterns

### The Atomization Insight

The breakthrough was recognizing that conversations are not the natural unit of knowledge. A conversation is a container -- a temporal artifact of a synchronous exchange. The knowledge within it decomposes into smaller units: insights, code patterns, decisions, questions, references. Each of these can stand alone, be retrieved independently, and form connections with units from other conversations.

This is the atomization principle. It transforms a collection of conversations into a knowledge graph.

### The Architecture That Emerged

From this insight, the system's architecture followed:

1. **Export** -- Get the conversations out of vendor silos
2. **Atomize** -- Decompose conversations into typed units
3. **Index** -- Build multi-modal search (keyword + semantic + hybrid)
4. **Analyze** -- Apply LLM intelligence to the corpus

Each layer addresses a specific failure mode. Each is independently valuable. Together they produce something no existing tool offers: a searchable, interconnected, self-analyzing knowledge corpus built from the raw material of AI conversations.

### The Name

"My Knowledge Base" -- deliberately plain. Not a brand, not a metaphor, not a system with a Greek name. The name describes exactly what it is: a base of knowledge, belonging to the person who built it. The modesty is intentional. The ambition lives in the architecture, not the branding.

### What It Became

Over six phases of development:

| Phase | Capability | Tasks |
|-------|-----------|-------|
| 1 | Export + Atomization | Multi-source scraping, five-strategy chunking |
| 2 | Semantic Search | OpenAI embeddings, ChromaDB, hybrid search with RRF |
| 3 | Intelligence | Insight extraction, smart tagging, relationship detection |
| 4 | Web UI | React SPA with D3 graph visualization |
| 5 | Advanced Ingestion | Apple Notes, iCloud, bookmarks |
| 6 | Production | Docker, Fly.io, CI/CD |

187 of 235 tasks completed. 80% of the roadmap delivered. The system works.

## Related Documents

- `01_MANIFESTO_REFRAMED.md` -- The thesis in declarative form
- `00_METHODOLOGY.md` -- The four operations in methodological detail
- `DEVELOPMENT_ROADMAP.md` -- The 235-item task list
