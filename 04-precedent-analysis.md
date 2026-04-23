# 04: Precedent Analysis

**Atom ID:** precedent-analysis
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Overview

This document surveys existing systems that address aspects of the knowledge base problem space. Each precedent is evaluated against the four operations defined in `00_METHODOLOGY.md`: Export, Atomization, Retrieval, and Intelligence Extraction.

## Category 1: Note-Taking and Knowledge Management

### Obsidian

- **Export:** Manual entry only. No AI conversation ingestion.
- **Atomization:** User-driven. Each note is a manual atom.
- **Retrieval:** Full-text search + backlinks. No semantic search.
- **Intelligence:** None. Plugin ecosystem exists but no LLM-native intelligence.
- **Gap:** Requires the human to do all decomposition work. The labor this system automates is exactly the labor Obsidian demands.

### Notion

- **Export:** Limited API. No conversation import pathway.
- **Atomization:** Block-level structure, but not auto-typed.
- **Retrieval:** Full-text only. Recently added AI features but no vector search.
- **Intelligence:** AI summarization exists but operates on individual pages, not corpus-wide.
- **Gap:** Multi-tenant SaaS model. Optimizes for team collaboration, not single-operator epistemic depth.

### Logseq

- **Export:** Local-first, open format (markdown + EDN).
- **Atomization:** Block-level with outliner structure.
- **Retrieval:** Full-text + graph queries.
- **Intelligence:** None native. Community plugins exist.
- **Gap:** Closest to our atomic model, but still requires manual entry and manual connection.

## Category 2: AI Conversation Management

### Readwise / Reader

- **Export:** Imports highlights from various sources. No AI conversation support.
- **Atomization:** Highlight-level (user-selected passages).
- **Retrieval:** Full-text + tag-based filtering.
- **Intelligence:** Spaced repetition surfacing.
- **Gap:** Excellent for reading highlights but does not address AI conversation export, atomization, or cross-conversation intelligence.

### Mem.ai

- **Export:** Proprietary format.
- **Atomization:** None -- stores notes as blobs.
- **Retrieval:** "Self-organizing" AI search (semantic-ish).
- **Intelligence:** AI-powered connections (opaque algorithm).
- **Gap:** Closest competitor in spirit, but proprietary, cloud-dependent, and does not ingest AI conversations natively.

### Reflect

- **Export:** Markdown export available.
- **Atomization:** None.
- **Retrieval:** AI-powered search.
- **Intelligence:** Backlink suggestions.
- **Gap:** Good for daily notes. No conversation ingestion, no atomization, no corpus-level analysis.

## Category 3: Search and Retrieval Systems

### Elasticsearch / OpenSearch

- **Relevance:** Production-grade full-text search with BM25 ranking.
- **Gap:** Requires significant infrastructure. No atomization pipeline. No LLM intelligence layer.

### ChromaDB / Pinecone / Weaviate

- **Relevance:** Vector databases for semantic search.
- **Gap:** Storage and retrieval only. No ingestion pipeline, no atomization, no intelligence extraction.

### Hybrid Search (academic)

- **Reciprocal Rank Fusion (RRF):** Cormack et al. (2009). Combines rankings from multiple systems without requiring score normalization.
- **Relevance:** The theoretical foundation for our hybrid search implementation.

## Category 4: LLM-Powered Analysis Tools

### ChatGPT Memory

- **Relevance:** Persistent memory across conversations.
- **Gap:** Opaque, user cannot query or export the memory graph. Single-source (OpenAI only).

### Claude Projects

- **Relevance:** Persistent context within a project scope.
- **Gap:** Manual document upload. No atomization. No cross-project intelligence.

## Precedent Matrix

| System | Export | Atomize | Retrieve | Intelligence | Score |
|--------|--------|---------|----------|-------------|-------|
| Obsidian | 0 | 0 | 1 | 0 | 1/4 |
| Notion | 0 | 0.5 | 1 | 0.5 | 2/4 |
| Logseq | 1 | 0.5 | 1 | 0 | 2.5/4 |
| Readwise | 0 | 0.5 | 1 | 0.5 | 2/4 |
| Mem.ai | 0 | 0 | 1 | 0.5 | 1.5/4 |
| Reflect | 0.5 | 0 | 1 | 0.5 | 2/4 |
| **My Knowledge Base** | **1** | **1** | **1** | **1** | **4/4** |

No existing system addresses all four operations. Each addresses at most two, leaving the others to manual labor or external tooling.

## Related Documents

- `00_METHODOLOGY.md` -- The four operations used as evaluation criteria
- `literature-review.md` -- Academic literature survey
- `benchmark-report.md` -- Performance benchmarks against comparable tools
