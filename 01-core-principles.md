# 01: Core Principles

**Atom ID:** core-principles
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Governing Principles

These principles govern every design decision, feature addition, and architectural change in the knowledge base. They are not aspirational -- they are constraints that reject implementations violating them.

### 1. Knowledge is Atomic

Every piece of knowledge decomposes into the smallest self-contained unit that can stand alone. An atom must be:
- **Self-contained:** Understandable without reading its parent conversation
- **Typed:** Classified as `insight`, `code`, `question`, `reference`, or `decision`
- **Retrievable:** Findable via keyword, semantic, or hybrid search independently
- **Connectable:** Capable of forming typed relationships with other atoms

Corollary: If a piece of content cannot be classified into one of these types, the type system is incomplete, not the content.

### 2. Sources are Federated, Knowledge is Unified

The knowledge base ingests from Claude, Gemini, ChatGPT, and local files. Once atomized, provenance is metadata, not identity. An insight from Claude and an insight from ChatGPT occupy the same search index, the same relationship graph, and the same intelligence pipeline.

Corollary: Adding a new source requires implementing the ingestion interface only. The atomizer, search, and intelligence layers do not change.

### 3. Search Must Be Multi-Modal

No single retrieval mode suffices:
- **FTS5** finds what you said (lexical precision)
- **Semantic search** finds what you meant (embedding similarity)
- **Hybrid search** balances both via Reciprocal Rank Fusion

Corollary: Any feature that relies on search must use hybrid search by default, with single-mode fallbacks for debugging only.

### 4. Intelligence is Extracted, Not Imposed

The LLM intelligence layer (Phase 3) discovers what the corpus contains, not what the operator assumes it contains. InsightExtractor, SmartTagger, RelationshipDetector, and ConversationSummarizer are descriptive, not prescriptive.

Corollary: Intelligence outputs are never used to filter or suppress search results. They augment -- they do not gate.

### 5. Cost Efficiency is a Design Constraint

Every LLM call has a measurable cost. Prompt caching (90% token savings), batch processing with checkpoints, and resumability are not optimizations -- they are requirements.

Corollary: No feature ships without a cost estimate per 1,000 operations. Features exceeding $1/1,000 ops require explicit justification.

### 6. Everything is Versioned and Auditable

Database migrations are timestamped. Backups are automated. Configuration changes are tracked. No operation modifies state without leaving a recoverable trail.

Corollary: `npm run backup` must succeed at any point in the system lifecycle. Backup failure is a P0 incident.

### 7. The System Serves One Person

This is a personal epistemological tool, not a multi-tenant SaaS product. Design decisions optimize for single-operator depth over multi-user breadth. The authentication layer exists for API security, not user management.

Corollary: Features that add multi-tenancy complexity without single-operator benefit are rejected.

## Principle Hierarchy

When principles conflict, higher-numbered principles yield to lower-numbered ones:

1. Knowledge is Atomic (inviolable)
2. Sources are Federated (structural)
3. Search is Multi-Modal (functional)
4. Intelligence is Extracted (behavioral)
5. Cost Efficiency (operational)
6. Everything is Versioned (operational)
7. Single Operator (contextual)

## Related Documents

- `00_METHODOLOGY.md` -- Epistemological foundation and four operations
- `docs/ARCHITECTURE.md` -- Technical implementation of these principles
- `README.md` -- Problem statement these principles address
