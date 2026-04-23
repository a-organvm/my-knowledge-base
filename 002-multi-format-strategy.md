# ADR-002: Multi-Format Strategy

**Atom ID:** adr-002-multi-format
**Status:** ACCEPTED
**References:** 2 cross-references in knowledge base corpus
**Context:** spec-kit integration for the knowledge base

---

## Status

Accepted

## Context

The knowledge base must ingest content from multiple sources that produce radically different formats:

| Source | Format | Structure |
|--------|--------|-----------|
| Claude.app | HTML (scraped) | Conversation turns with markdown content |
| Gemini | HTML (scraped) | Conversation turns |
| ChatGPT | JSON (bulk export) | Nested conversation objects |
| Local files | Markdown, plain text | Unstructured or heading-structured |
| Documents | PDF, HTML | Format-specific structure |

A single processing pipeline must handle all formats without format-specific code paths polluting the atomization logic.

## Decision

Implement a two-layer normalization strategy:

### Layer 1: Source-Specific Parsers

Each source has a dedicated parser in `src/sources/` that handles format-specific extraction:

```typescript
interface KnowledgeSource {
  name: string;
  export(): Promise<Conversation[] | KnowledgeDocument[]>;
}
```

Parsers are responsible for:
- Authentication and data access
- Format parsing (HTML, JSON, PDF, etc.)
- Normalizing output to `Conversation` or `KnowledgeDocument` interface
- Preserving source-specific metadata

### Layer 2: Unified Atomization

The atomizer receives normalized objects and applies format-agnostic processing:
- Type classification
- Tag generation
- Category assignment
- Keyword extraction

Source-specific metadata is preserved in the `context` field of each `AtomicUnit` as structured text, not as typed fields. This prevents the atomizer schema from growing unboundedly with each new source.

## Consequences

### Positive
- Adding a new source requires only a new parser implementing `KnowledgeSource`
- Atomization logic remains source-agnostic
- All atoms enter the same search index regardless of origin
- Source metadata is preserved without schema bloat

### Negative
- Source-specific metadata in the `context` field is not queryable via typed fields (must use FTS)
- Two-layer normalization adds processing overhead (minor)
- Each new source requires understanding its export format (no universal parser)

## Alternatives Considered

1. **Single universal parser:** Rejected. Formats are too different for a single parser to handle without unacceptable quality loss.
2. **Per-source atom schemas:** Rejected. Would fragment the search index and complicate hybrid search.
3. **External ETL tool (dbt, Airbyte):** Rejected. Overkill for the current source count and adds infrastructure dependency.

## Related Documents

- `001-privacy-first-design.md` -- Privacy constraints on format handling
- `02-cal-architecture.md` -- Content Atomization Layer architecture
- `src/sources/` -- Source parser implementations
