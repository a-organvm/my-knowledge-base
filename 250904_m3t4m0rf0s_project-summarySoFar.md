# M3T4M0RF0S Project Summary

**Atom ID:** m3t4m0rf0s-summary
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus
**Context:** Omni-Dromenon Engine development history

---

## Overview

M3T4M0RF0S (Metamorfos) is the working codename for the creative-systems layer of the ORGANVM project, encompassing the Omni-Dromenon Engine and its generative performance subsystems. This document summarizes the project's trajectory from inception through its current state within the knowledge base integration.

## Project Identity

| Field | Value |
|-------|-------|
| Codename | M3T4M0RF0S (Metamorfos) |
| Organ | ORGAN-II (Poiesis) |
| Organization | omni-dromenon-machina |
| Domain | Generative art, performance systems, creative coding |
| Relationship to Knowledge Base | Consumer of atomized knowledge for performance generation |

## Genesis

The project originated from the intersection of three interests:
1. **Generative art** -- algorithmic visual and audio composition
2. **Performance systems** -- interactive theatre, movement notation, live coding
3. **Recursive architecture** -- systems that transform their own structure through operation

The central thesis: creative output can be generated from knowledge structures. If a knowledge base atomizes conversations into typed units with relational connections, those atoms become source material for generative systems -- themes for visual composition, tensions for dramatic structure, patterns for musical rhythm.

## Architecture Within ORGANVM

```
ORGAN-I (Theoria)                     ORGAN-II (Poiesis)
┌─────────────────────────┐          ┌─────────────────────────┐
│ My Knowledge Base       │          │ M3T4M0RF0S / ODE        │
│ ├── Atomic Units        │ -------> │ ├── Content Sources     │
│ ├── Knowledge Graph     │ -------> │ ├── Scene Graph         │
│ ├── Extracted Insights  │ -------> │ ├── Thematic Seeds      │
│ └── Smart Tags          │ -------> │ └── Classification      │
└─────────────────────────┘          └─────────────────────────┘
                                      │
                                      ├── Generative Art Algorithms
                                      ├── Movement Notation Systems
                                      ├── Interactive Theatre Designer
                                      ├── Modular Synthesis Philosophy
                                      └── Three.js Interactive Builder
```

## Development Phases

### Phase 1: Conceptual Foundation

- Defined the recursive performance architecture
- Established the connection between knowledge atomization and generative output
- Mapped atom types to creative output modalities:
  - `insight` atoms --> thematic seeds for visual/textual composition
  - `code` atoms --> algorithmic pattern sources
  - `decision` atoms --> dramatic tension points
  - `question` atoms --> audience interaction triggers
  - `reference` atoms --> contextual grounding material

### Phase 2: Engine Design

- Designed the Omni-Dromenon Engine runtime
- Specified the content source registry connecting knowledge base API to engine
- Defined scene graph generation from knowledge graph topology
- Established movement notation mappings from content patterns

### Phase 3: Integration with Knowledge Base

- Knowledge Base REST API provides content feed
- Hybrid search enables thematic content discovery
- Relationship graph provides narrative sequencing data
- Smart tags provide classification for content routing

## Current Status

| Component | Status | Location |
|-----------|--------|----------|
| Knowledge Base (content source) | GRADUATED | ORGAN-I / my-knowledge-base |
| Omni-Dromenon Engine (runtime) | DESIGN | ORGAN-II / omni-dromenon-machina |
| Scene graph generator | SPECIFICATION | Part of ODE |
| Movement notation interface | RESEARCH | Part of ODE |
| Generative art algorithms | AVAILABLE (skill) | generative-art-algorithms |
| Interactive theatre designer | AVAILABLE (skill) | interactive-theatre-designer |

## Key Decisions

1. **Knowledge base as content source, not co-processor:** The engine consumes knowledge base output via API. It does not modify the knowledge base. Unidirectional data flow (ORGAN-I --> ORGAN-II).

2. **Scene graph from knowledge graph:** The topology of relationships between atoms determines the structure of generated performances, not a predefined narrative template.

3. **Semantic search for associative connections:** The engine uses semantic search (not keyword search) to find thematically related atoms, enabling unexpected creative associations.

## Forward Path

1. Complete Omni-Dromenon Engine specification
2. Implement content source registry consuming knowledge base API
3. Build scene graph generator prototype
4. Test with live knowledge base data (real atoms, real relationships)
5. Deploy first generative output (visual composition from knowledge atoms)

## Related Documents

- `omni-dromenon-engine-implementation.md` -- Engine implementation specification
- `03-cross-genre-deployment.md` -- Cross-genre knowledge deployment
- `docs/ARCHITECTURE.md` -- Knowledge base architecture (source system)
- `README.md` -- Knowledge base overview
