# Literature Review

**Atom ID:** literature-review
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Overview

This literature review surveys the academic and industry foundations underlying the My Knowledge Base system. It covers four domains: knowledge atomization theory, information retrieval, AI-assisted knowledge management, and personal knowledge management systems.

## 1. Knowledge Atomization and Epistemological Foundations

### Logical Atomism

- **Russell, B. (1918).** "The Philosophy of Logical Atomism." *The Monist*, 28(4), 495-527.
  - Foundation: Knowledge decomposes into atomic propositions independently verifiable against the world. The knowledge base's `AtomicUnit` type directly inherits this epistemological commitment -- each unit must stand alone as a self-contained piece of knowledge.

- **Wittgenstein, L. (1921).** *Tractatus Logico-Philosophicus.* Translated by C.K. Ogden.
  - Relevance: "The world is the totality of facts, not of things" (1.1). The atomizer treats conversations as totalities that decompose into facts (atoms), not as indivisible things.

### Chunking and Segmentation

- **Miller, G.A. (1956).** "The Magical Number Seven, Plus or Minus Two." *Psychological Review*, 63(2), 81-97.
  - Relevance: Cognitive chunking theory. The knowledge base's chunk size guardrails (min 160 tokens, max 40 chunks per document) are calibrated to produce units within human cognitive processing limits.

- **Hearst, M.A. (1997).** "TextTiling: Segmenting Text into Multi-paragraph Subtopic Passages." *Computational Linguistics*, 23(1), 33-64.
  - Relevance: Algorithmic text segmentation based on lexical cohesion. The `SemanticChunker` uses similar boundary detection principles, splitting on structural markers (headings, code fences) rather than pure lexical shift.

## 2. Information Retrieval

### Full-Text Search

- **Robertson, S.E. & Zaragoza, H. (2009).** "The Probabilistic Relevance Framework: BM25 and Beyond." *Foundations and Trends in Information Retrieval*, 3(4), 333-389.
  - Relevance: BM25 is the ranking function underlying SQLite FTS5. The knowledge base inherits its term frequency / inverse document frequency weighting.

### Semantic Search and Embeddings

- **Mikolov, T. et al. (2013).** "Efficient Estimation of Word Representations in Vector Space." *arXiv:1301.3781*.
  - Relevance: Word2Vec introduced dense vector representations. Modern embedding models (OpenAI text-embedding-3-small) extend this to sentence/document level.

- **Reimers, N. & Gurevych, I. (2019).** "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks." *EMNLP 2019*.
  - Relevance: Established sentence-level embedding as viable for semantic search. The knowledge base's semantic search layer operates on this principle.

### Hybrid Search and Rank Fusion

- **Cormack, G.V., Clarke, C.L.A., & Buettcher, S. (2009).** "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods." *SIGIR '09*.
  - Directly implemented: RRF is the fusion algorithm combining FTS5 and semantic search results in `hybrid-search.ts`. The algorithm requires no score normalization, making it suitable for combining heterogeneous ranking systems.

## 3. AI-Assisted Knowledge Management

### LLM-Powered Analysis

- **Brown, T. et al. (2020).** "Language Models are Few-Shot Learners." *NeurIPS 2020*.
  - Relevance: Establishes that large language models can perform sophisticated analysis tasks (classification, extraction, summarization) with minimal task-specific training. The knowledge base's Phase 3 intelligence layer relies on this capability.

### Prompt Engineering and Caching

- **Anthropic. (2024).** "Prompt Caching." *docs.anthropic.com*.
  - Directly implemented: 90% cost reduction by caching system prompts and reusing them across batch operations. The `ClaudeService` class implements this pattern.

### Knowledge Graph Construction

- **Ji, S. et al. (2022).** "A Survey on Knowledge Graphs: Representation, Acquisition, and Applications." *IEEE TNNLS*, 33(2), 494-514.
  - Relevance: The `RelationshipDetector` constructs a knowledge graph from atomic units. The relationship types (`relates_to`, `contradicts`, `extends`, `depends_on`) follow established knowledge graph relation taxonomies.

## 4. Personal Knowledge Management

### The PKM Problem Space

- **Davies, S. (2011).** "Still Building the Memex." *Communications of the ACM*, 54(2), 80-88.
  - Relevance: Traces the Memex vision (Bush, 1945) through modern PKM tools. Identifies the persistent gap between the vision of associative knowledge retrieval and the reality of manual note-taking.

- **Ahrens, S. (2017).** *How to Take Smart Notes.* Sextant Publishing.
  - Relevance: The Zettelkasten method -- atomic notes with typed connections -- is the closest analog to the knowledge base's data model. Key difference: the knowledge base automates the decomposition that Zettelkasten requires humans to perform.

### Existing Systems Analysis

See `04-precedent-analysis.md` for a detailed comparison of Obsidian, Notion, Logseq, Readwise, Mem.ai, and Reflect against the four operations framework.

## Gaps in the Literature

1. **AI conversation as knowledge source.** No academic work treats AI conversations as a distinct epistemological category requiring specialized processing pipelines.

2. **Cross-platform conversation federation.** No existing system or paper addresses the problem of unifying knowledge from multiple AI platforms into a single searchable corpus.

3. **LLM-on-LLM analysis.** Using one LLM (Claude) to analyze conversations from multiple LLMs (Claude, GPT, Gemini) is a novel application with no established methodology.

## Related Documents

- `00_METHODOLOGY.md` -- Methodology grounded in this literature
- `04-precedent-analysis.md` -- Practical system comparisons
- `01-core-principles.md` -- Principles derived from these foundations
