# 02: CAL Architecture (Content Atomization Layer)

**Atom ID:** cal-architecture
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Overview

The Content Atomization Layer (CAL) is the processing core that transforms raw conversations and documents into typed atomic knowledge units. It sits between the source ingestion layer and the storage/search layer.

## Component Map

```
Source Manager
      │
      ▼
┌─────────────────────────────────────┐
│          CONTENT ATOMIZATION LAYER   │
│                                      │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ Conversation  │  │  Document    │ │
│  │  Atomizer     │  │  Atomizer    │ │
│  │  (atomizer.ts)│  │  (doc-atom.) │ │
│  └──────┬───────┘  └──────┬───────┘ │
│         │                  │         │
│         ▼                  ▼         │
│  ┌─────────────────────────────────┐ │
│  │    Chunking Strategy Router      │ │
│  │                                  │ │
│  │  MarkdownSemantic  │ PdfSliding │ │
│  │  SingleChunk       │ CodeBlock  │ │
│  │  MessageLevel      │            │ │
│  └──────────┬──────────────────────┘ │
│             │                        │
│             ▼                        │
│  ┌─────────────────────────────────┐ │
│  │    Semantic Chunker              │ │
│  │    (semantic-chunker.ts)         │ │
│  │    - Content type detection      │ │
│  │    - Boundary identification     │ │
│  │    - Merge/split heuristics      │ │
│  │    - Confidence scoring          │ │
│  └──────────┬──────────────────────┘ │
│             │                        │
│             ▼                        │
│  ┌─────────────────────────────────┐ │
│  │    Unit Enrichment Pipeline      │ │
│  │    - Type classification         │ │
│  │    - Tag generation              │ │
│  │    - Category assignment         │ │
│  │    - Keyword extraction          │ │
│  │    - Title generation            │ │
│  └─────────────────────────────────┘ │
└──────────────────┬──────────────────┘
                   │
                   ▼
            SQLite + ChromaDB
```

## Chunking Strategies

### Strategy Selection Logic

The CAL selects a chunking strategy based on content characteristics:

```typescript
function selectStrategy(input: InputContent): ChunkingStrategy {
  if (input.type === 'conversation') return MessageLevelStrategy;
  if (input.format === '.pdf')       return PdfSlidingWindowStrategy;
  if (input.format === '.md')        return MarkdownSemanticStrategy;
  if (input.format === '.html')      return MarkdownSemanticStrategy;
  return SingleChunkStrategy;
}
```

### Strategy Specifications

| Strategy | Input | Split Boundary | Merge Threshold | Max Chunks |
|----------|-------|---------------|-----------------|------------|
| MessageLevel | Conversations | Per-message (>20 chars) | N/A | Unlimited |
| MarkdownSemantic | `.md`, `.txt`, `.html` | Headings + semantic | `CHUNK_MIN_TOKENS` (160) | `CHUNK_MAX_PER_DOC` (40) |
| PdfSlidingWindow | `.pdf` | Token window (500) | 50-token overlap | Configurable |
| CodeBlock | Any with fenced code | Triple-backtick fences | N/A | Per-block |
| SingleChunk | Fallback | None (entire content) | N/A | 1 |

## Unit Enrichment Pipeline

Every chunk passes through enrichment before storage:

1. **Type Classification:** Content heuristics assign one of five types
   - `question`: Contains `?` patterns
   - `code`: Contains code blocks or programming syntax
   - `decision`: Contains decision language ("decided", "chose", "will use")
   - `reference`: Contains URLs, citations, or bibliographic patterns
   - `insight`: Default for analytical/reflective content

2. **Tag Generation:** Frequency-based keyword detection + technology/language identification

3. **Category Assignment:** Five categories based on dominant content signals:
   - `programming`, `writing`, `research`, `design`, `general`

4. **Keyword Extraction:** Top N terms by frequency after stopword removal

5. **Title Generation:** First meaningful line, truncated to 80 characters

## Guardrails

- Maximum chunks per document: 40 (prevents over-fragmentation)
- Minimum chunk tokens: 160 (prevents noise atoms)
- Message minimum length: 20 characters (filters greetings and acknowledgments)
- Confidence threshold: Semantic chunker scores each boundary; low-confidence splits are merged

## Performance Characteristics

| Operation | Throughput | Bottleneck |
|-----------|-----------|------------|
| Message-level atomization | ~1,000 messages/sec | CPU (string processing) |
| Markdown semantic chunking | ~100 documents/sec | CPU (boundary detection) |
| PDF sliding window | ~50 pages/sec | I/O (PDF parsing) |
| Unit enrichment | ~500 units/sec | CPU (classification + tagging) |

## Related Documents

- `00_METHODOLOGY.md` -- Atomization as the second of four operations
- `01-core-principles.md` -- "Knowledge is Atomic" principle
- `src/atomizer.ts` -- Conversation atomizer implementation
- `src/document-atomizer.ts` -- Document atomizer implementation
- `src/chunking-strategies.ts` -- Strategy pattern implementations
- `src/semantic-chunker.ts` -- Semantic boundary detection
