# Omni-Dromenon Engine: Implementation Specification

**Atom ID:** omni-dromenon-engine-impl
**Status:** ACTIVE
**References:** 5 cross-references in knowledge base corpus
**Organ:** ORGAN-II (Poiesis) -- Generative art, performance systems, creative coding

---

## Overview

The Omni-Dromenon Engine is a performance systems architecture that connects generative art, interactive theatre, and movement notation into a unified runtime. It operates as the creative engine layer within the ORGANVM eight-organ model, where ORGAN-I (Theoria) provides the recursive knowledge structures and ORGAN-II (Poiesis) provides the generative execution surface.

This implementation specification defines how the knowledge base feeds the Omni-Dromenon Engine with atomized content, extracted insights, and relational graphs that become source material for performance generation.

## Architecture

```
Knowledge Base (ORGAN-I)           Omni-Dromenon Engine (ORGAN-II)
┌────────────────────┐             ┌────────────────────────────┐
│ Atomic Units       │────────────>│ Content Source Registry     │
│ Knowledge Graph    │────────────>│ Relational Topology         │
│ Extracted Insights │────────────>│ Thematic Seed Generator     │
│ Smart Tags         │────────────>│ Classification Index        │
└────────────────────┘             └────────────┬───────────────┘
                                                │
                                   ┌────────────▼───────────────┐
                                   │ Performance Runtime         │
                                   │  - Scene Graph              │
                                   │  - Movement Notation        │
                                   │  - Generative Audio         │
                                   │  - Visual Composition       │
                                   └────────────────────────────┘
```

## Data Flow: Knowledge Base to Engine

### 1. Content Ingestion

The knowledge base atomizes conversations into discrete units. The engine consumes these via the REST API:

```typescript
// Fetch thematically related atoms for scene generation
const response = await fetch('/api/search/hybrid', {
  method: 'POST',
  body: JSON.stringify({
    query: 'recursive structure transformation',
    limit: 20,
    types: ['insight', 'decision', 'reference']
  })
});
```

### 2. Relationship Traversal

The knowledge graph provides relational topology for narrative sequencing:

```typescript
// Traverse relationships to build scene sequences
const graph = await fetch('/api/graph/neighbors', {
  method: 'POST',
  body: JSON.stringify({
    unitId: seedAtomId,
    depth: 3,
    relationshipTypes: ['relates_to', 'contradicts', 'extends']
  })
});
```

### 3. Insight Extraction as Thematic Seeds

Phase 3 insights become generative seeds:
- **Themes** map to visual palettes and audio textures
- **Contradictions** generate dramatic tension points
- **Patterns** produce rhythmic structures and movement notation
- **Questions** create interactive audience engagement moments

## Implementation Components

### Content Source Registry

Manages connections between the knowledge base and the engine's content pipeline:

| Component | Source | Update Frequency |
|-----------|--------|-----------------|
| Atom feed | Knowledge Base REST API | On-demand |
| Tag index | Smart Tagger output | Batch (daily) |
| Relationship graph | RelationshipDetector output | Batch (daily) |
| Insight corpus | InsightExtractor output | Batch (weekly) |

### Scene Graph Generator

Converts knowledge graph topology into performable scene structures:

1. **Seed selection** -- Choose a root atom based on thematic criteria
2. **Neighborhood expansion** -- Traverse 2-3 levels of relationships
3. **Tension mapping** -- Identify contradictions and paradoxes as dramatic beats
4. **Sequence ordering** -- Arrange scenes by temporal or logical flow
5. **Output format** -- Scene graph JSON compatible with performance runtime

### Movement Notation Interface

Translates content patterns into movement notation:

| Content Pattern | Movement Mapping |
|----------------|-----------------|
| Recursive structures | Spiral/circular motifs |
| Binary decisions | Fork/diverge gestures |
| Accumulation (lists) | Additive layering |
| Contradiction | Opposition/inversion |

## Integration Points

- **Knowledge Base API** (this repo): REST endpoints at `/api/*`
- **Omni-Dromenon Engine** (`organvm-ii-poiesis/omni-dromenon-machina`): Performance runtime
- **Generative Art Algorithms** (skills): `generative-art-algorithms`, `algorithmic-art`
- **Movement Notation** (skills): `movement-notation-systems`
- **Interactive Theatre** (skills): `interactive-theatre-designer`

## Status

- Knowledge Base API: GRADUATED (production-ready)
- Engine content pipeline: DESIGN phase
- Scene graph generator: SPECIFICATION phase
- Movement notation interface: RESEARCH phase

## Related Documents

- `docs/ARCHITECTURE.md` -- Knowledge Base system design
- `docs/API_DOCUMENTATION.md` -- REST API reference
- `README.md` -- Project overview and core concepts
