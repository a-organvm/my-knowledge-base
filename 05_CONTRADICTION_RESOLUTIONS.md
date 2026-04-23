# 05: Contradiction Resolutions

**Atom ID:** contradiction-resolutions
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus
**Decision Context:** Option A selected -- "Create manifesto + governance framework now"

---

## Overview

During the design and implementation of the knowledge base, several contradictions emerged between competing design goals. This document records each contradiction, the resolution chosen, and the reasoning that governed the choice.

## Contradiction 1: Depth vs. Breadth of Atomization

**Tension:** Finer atomization produces more granular, retrievable units but increases noise. Coarser atomization preserves context but reduces retrievability.

**Resolution:** Configurable guardrails with conservative defaults.
- Minimum chunk tokens: 160 (rejects noise)
- Maximum chunks per document: 40 (prevents over-fragmentation)
- Message minimum length: 20 characters (filters greetings)

**Principle Applied:** Knowledge is Atomic (Principle 1), but atoms must be self-contained. A fragment that cannot stand alone is not an atom -- it is debris.

## Contradiction 2: Privacy vs. Searchability

**Tension:** Full-text indexing of personal AI conversations creates a searchable archive of potentially sensitive content. Privacy demands restriction; searchability demands openness.

**Resolution:** Local-first architecture. The database is a SQLite file on the operator's machine. No cloud sync, no telemetry, no external analytics. The API server binds to localhost by default. Production deployment is opt-in and requires explicit CORS configuration.

**Principle Applied:** The System Serves One Person (Principle 7). Privacy is structural, not feature-level.

## Contradiction 3: LLM Cost vs. Intelligence Quality

**Tension:** More LLM calls produce richer intelligence extraction but increase operational cost. Cost optimization risks shallow analysis.

**Resolution:** Prompt caching as a design requirement, not an optimization.
- 90% token savings via Anthropic prompt caching
- Batch processing with checkpoints for resumability
- Cost tracking via `ClaudeService.getTokenStats()`
- Hard ceiling: no feature exceeding $1/1,000 operations ships without justification

**Principle Applied:** Cost Efficiency is a Design Constraint (Principle 5).

## Contradiction 4: Multi-Source Federation vs. Schema Consistency

**Tension:** Different AI platforms export in radically different formats (ChatGPT JSON dump, Claude.app HTML scraping, Gemini browser automation). Normalizing to a single schema risks losing source-specific metadata.

**Resolution:** Two-layer normalization.
1. Source-specific parsers preserve all available metadata in a raw layer
2. The atomizer normalizes to the `AtomicUnit` schema, with source-specific fields stored in the `context` field as structured text

**Principle Applied:** Sources are Federated, Knowledge is Unified (Principle 2).

## Contradiction 5: Automation vs. Operator Control

**Tension:** Full automation (auto-ingest, auto-atomize, auto-tag) risks producing artifacts the operator did not intend. Manual control ensures quality but defeats the purpose of automation.

**Resolution:** Automation with audit trail.
- All operations are batch-invokable via CLI (operator initiates)
- All operations produce logs and statistics
- No operation modifies the source material -- atomization is additive
- Smart tags are additive (augment, never replace, existing tags)
- The operator reviews via web UI search and graph visualization

**Principle Applied:** Intelligence is Extracted, Not Imposed (Principle 4).

## Contradiction 6: Single-Operator vs. API Security

**Tension:** A single-operator tool should not need authentication. But an exposed REST API without auth is a vulnerability.

**Resolution:** Auth is available but optional.
- `ENABLE_AUTH=false` (default for local development)
- `ENABLE_AUTH=true` (required for production deployment)
- Rate limiting always active (protects against abuse even without auth)

**Principle Applied:** Everything is Versioned and Auditable (Principle 6). The system must be defensible regardless of deployment context.

## Open Contradictions

The following tensions remain unresolved and are tracked for future resolution:

1. **Real-time vs. Batch:** Should new conversations auto-atomize on export, or wait for batch processing? Current: batch only.
2. **Graph Completeness vs. Performance:** The relationship detector scales O(n^2) with corpus size. At what corpus size does this become prohibitive?
3. **Embedding Model Lock-in:** OpenAI `text-embedding-3-small` is the current default. Switching models requires re-embedding the entire corpus.

## Related Documents

- `01-core-principles.md` -- The principles referenced in each resolution
- `06_CHANGE_AUDIT.md` -- Audit trail of implementation changes
- `05_DecisionLog.md` -- Decision log with timestamps
