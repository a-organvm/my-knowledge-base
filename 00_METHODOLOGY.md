# 00: Methodology

**Atom ID:** methodology-foundation
**Status:** ACTIVE
**References:** 4 cross-references in knowledge base corpus

---

## Epistemological Foundation

This knowledge base operates on a specific epistemological thesis: AI conversations are not disposable dialogue but raw material containing latent knowledge structures that become visible only through systematic decomposition. The methodology proceeds through four operations, each addressing a distinct failure mode of conventional knowledge management.

## The Four Operations

### 1. Export (Extraction from Silos)

**Problem:** Knowledge locked inside vendor UIs with no bulk export pathway.

**Method:** Multi-source scraping and parsing. Playwright-based browser automation for Claude.app and Gemini. JSON parsing for ChatGPT exports. Direct filesystem reads for local markdown.

**Principle:** All knowledge sources are treated as federated inputs to a single pipeline. The source is metadata, not identity -- an insight from Claude and an insight from ChatGPT enter the same atomization process with equal standing.

### 2. Atomization (Decomposition into Units)

**Problem:** Conversations are monolithic blobs mixing multiple knowledge types.

**Method:** Five-strategy atomization dispatched by content characteristics:
1. Message-level decomposition (per-message classification)
2. Code block extraction (regex-based parsing)
3. Markdown semantic chunking (heading-boundary splitting)
4. PDF sliding window (token-based windowing with overlap)
5. Single-chunk fallback (for indivisible content)

**Principle:** The atom is the fundamental epistemological unit. An atom is the smallest piece of knowledge that can stand alone, be retrieved independently, and form typed connections with other atoms. Every atom carries: type classification, auto-generated tags, category assignment, keyword extraction, and source provenance.

### 3. Multi-Modal Retrieval (Search Across Dimensions)

**Problem:** No cross-conversation, cross-platform, cross-time search capability.

**Method:** Three retrieval modes combined via Reciprocal Rank Fusion:
1. **Full-Text Search (FTS5):** Keyword precision, boolean operators, phrase matching
2. **Semantic Search (Vectors):** Meaning-based similarity via OpenAI embeddings + ChromaDB
3. **Hybrid Search (RRF):** Combines FTS5 and semantic rankings with configurable weighting

**Principle:** No single retrieval mode is sufficient. Keyword search finds what you explicitly said. Semantic search finds what you meant. Hybrid search balances precision and recall.

### 4. Intelligence Extraction (LLM-Powered Analysis)

**Problem:** Conversations contain implicit insights invisible without systematic analysis.

**Method:** Four Claude-powered analyzers running against the atomized corpus:
1. **InsightExtractor:** Identifies non-obvious patterns, recurring themes, latent contradictions
2. **SmartTagger:** Context-aware tagging beyond keyword detection
3. **RelationshipDetector:** Discovers connections between atoms across conversations
4. **ConversationSummarizer:** Generates multi-level summaries

**Principle:** The corpus knows more than any individual conversation reveals. Intelligence extraction surfaces the delta between what was explicitly articulated and what the corpus implicitly contains.

## Validation Criteria

Each operation is validated against measurable outcomes:

| Operation | Metric | Target |
|-----------|--------|--------|
| Export | Source coverage | All 4 providers supported |
| Atomization | Unit type distribution | No single type exceeds 60% |
| Retrieval | Search relevance (MRR@10) | > 0.7 |
| Intelligence | Insight novelty rate | > 30% non-obvious findings |

## Philosophical Grounding

The methodology draws from three traditions:

1. **Epistemological atomism** (Russell, Wittgenstein): Knowledge decomposes into atomic propositions that are independently verifiable
2. **Information retrieval theory** (Salton, Robertson): Relevance is a function of both term frequency and semantic proximity
3. **Hermeneutic circulation** (Gadamer): Understanding the whole requires understanding the parts, and vice versa -- hence the iterative atomize-retrieve-analyze loop

## Related Documents

- `README.md` -- System overview and problem statement
- `docs/ARCHITECTURE.md` -- Technical system design
- `01-core-principles.md` -- Core operating principles
