# 03: Cross-Genre Deployment

**Atom ID:** cross-genre-deployment
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Overview

Cross-genre deployment defines how the knowledge base serves multiple creative and analytical genres simultaneously. A single corpus of atomized knowledge feeds into programming projects, creative writing, research synthesis, performance design, and system architecture -- each genre drawing from the same atoms through different retrieval lenses.

## Genre Taxonomy

| Genre | Primary Atom Types | Search Mode | Downstream Consumer |
|-------|-------------------|-------------|-------------------|
| Programming | `code`, `decision` | FTS5 (precision) | IDE, CLI tools |
| Creative Writing | `insight`, `reference` | Semantic (meaning) | Essay pipeline, portfolio |
| Research | `reference`, `insight`, `question` | Hybrid (balanced) | Literature reviews, grant proposals |
| System Architecture | `decision`, `code` | FTS5 + graph traversal | ORGANVM organs, design docs |
| Performance Art | `insight`, `reference` | Semantic (associative) | Omni-Dromenon Engine |

## Retrieval Lens Configuration

Each genre activates a different retrieval configuration:

```typescript
interface GenreLens {
  name: string;
  atomTypes: AtomType[];        // Filter to these types
  searchMode: 'fts' | 'semantic' | 'hybrid';
  ftsWeight: number;            // 0.0-1.0, for hybrid mode
  semanticWeight: number;       // 0.0-1.0, for hybrid mode
  maxResults: number;
  sortBy: 'relevance' | 'recency' | 'connections';
}

const GENRE_LENSES: Record<string, GenreLens> = {
  programming: {
    name: 'Programming',
    atomTypes: ['code', 'decision'],
    searchMode: 'fts',
    ftsWeight: 0.8,
    semanticWeight: 0.2,
    maxResults: 20,
    sortBy: 'relevance'
  },
  creative: {
    name: 'Creative Writing',
    atomTypes: ['insight', 'reference'],
    searchMode: 'semantic',
    ftsWeight: 0.3,
    semanticWeight: 0.7,
    maxResults: 50,
    sortBy: 'connections'
  },
  research: {
    name: 'Research',
    atomTypes: ['reference', 'insight', 'question'],
    searchMode: 'hybrid',
    ftsWeight: 0.5,
    semanticWeight: 0.5,
    maxResults: 100,
    sortBy: 'relevance'
  }
};
```

## Cross-Genre Patterns

### Pattern 1: Code-to-Essay Pipeline

A programming decision atom ("Chose SQLite over Postgres for single-operator simplicity") becomes source material for an essay about technology selection philosophy. The knowledge base provides both the decision and its relational context (what alternatives were considered, what constraints applied).

### Pattern 2: Research-to-Architecture Pipeline

Research atoms about information retrieval theory ("Reciprocal Rank Fusion combines rankings from multiple retrieval systems") feed directly into architectural decisions for the hybrid search implementation. The connection is bidirectional: the architecture validates the research, and the research justifies the architecture.

### Pattern 3: Insight-to-Performance Pipeline

Abstract insights about recursive structures become thematic seeds for generative art and performance systems. The Omni-Dromenon Engine consumes insights through semantic search, finding atoms whose meaning-space proximity generates unexpected creative connections.

## Deployment Strategy Per Genre

| Genre | Deployment Target | Access Pattern | Update Frequency |
|-------|------------------|----------------|-----------------|
| Programming | CLI (`npm run search`) | Interactive, real-time | Continuous |
| Creative Writing | Web UI (graph view) | Exploratory, browsing | Session-based |
| Research | API (`/api/search/hybrid`) | Batch queries | Project-based |
| Architecture | API + CLI | Targeted queries | On-demand |
| Performance | API (streaming) | Associative traversal | Event-driven |

## Related Documents

- `01-core-principles.md` -- "Search Must Be Multi-Modal" principle
- `02-cal-architecture.md` -- Content Atomization Layer
- `04-precedent-analysis.md` -- Historical precedents for cross-genre systems
- `omni-dromenon-engine-implementation.md` -- Performance art integration
