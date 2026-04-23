# 01: Contradiction Audit

**Atom ID:** contradiction-audit
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Purpose

This audit identifies contradictions between stated design principles, implemented behavior, and documented decisions. A contradiction is not a bug -- it is a tension between legitimate design goals that has not been explicitly resolved.

## Audit Methodology

1. Extract all stated principles from `01-core-principles.md`
2. Extract all design decisions from `05_CONTRADICTION_RESOLUTIONS.md`
3. Compare principles and decisions against actual implementation
4. Classify each finding as: RESOLVED, OPEN, or TOLERATED

## Findings

### Finding 1: Atomic Self-Containment vs. Context Dependency

- **Principle:** "An atom must be self-contained: understandable without reading its parent conversation" (Principle 1)
- **Implementation:** Atoms include a `context` field that stores surrounding conversation context
- **Tension:** If the context field is necessary for understanding, the atom is not truly self-contained
- **Status:** TOLERATED
- **Rationale:** The `context` field provides provenance, not meaning. The atom's `content` field must stand alone. Context is metadata for tracing, not comprehension.

### Finding 2: Cost Ceiling vs. Comprehensive Intelligence

- **Principle:** "No feature exceeding $1/1,000 ops ships without justification" (Principle 5)
- **Implementation:** RelationshipDetector at scale (10,000+ atoms) may exceed this threshold due to O(n^2) pair comparisons
- **Tension:** Full relationship detection at corpus scale could cost $4-8 per 1,000 operations
- **Status:** OPEN
- **Resolution Path:** Implement sampling-based relationship detection for corpora exceeding 5,000 atoms. Full detection available as an opt-in flag.

### Finding 3: Source Neutrality vs. Source-Specific Features

- **Principle:** "Once atomized, provenance is metadata, not identity" (Principle 2)
- **Implementation:** Export commands expose source-specific flags (`--source=claude`, `--source=gemini`)
- **Tension:** CLI ergonomics require source-awareness; principle demands source-blindness
- **Status:** RESOLVED
- **Rationale:** Source-awareness is an ingestion concern, not a storage or retrieval concern. The principle applies to post-atomization operations. Search, intelligence, and graph operations are genuinely source-agnostic.

### Finding 4: Versioning Commitment vs. Embedding Immutability

- **Principle:** "Everything is Versioned and Auditable" (Principle 6)
- **Implementation:** Embedding vectors are stored in ChromaDB without version history. Re-embedding overwrites the previous vector.
- **Tension:** Vector updates are not auditable or reversible
- **Status:** OPEN
- **Resolution Path:** Add embedding generation timestamp to ChromaDB metadata. Store model identifier alongside vectors so re-embedding is detectable.

### Finding 5: Single-Operator Design vs. API Authentication

- **Principle:** "The System Serves One Person" (Principle 7)
- **Implementation:** Full authentication middleware with API keys, rate limiting, CORS
- **Tension:** Single-operator tools do not need multi-user auth infrastructure
- **Status:** RESOLVED
- **Rationale:** Auth exists for API security (preventing unauthorized network access), not user management. A single operator's API server exposed to the network still needs access control.

## Audit Summary

| Status | Count |
|--------|-------|
| RESOLVED | 3 |
| OPEN | 2 |
| TOLERATED | 1 |
| **Total** | **6** |

## Next Audit

Schedule: After next major feature addition or architecture change.

## Related Documents

- `01-core-principles.md` -- Principles audited
- `05_CONTRADICTION_RESOLUTIONS.md` -- Formal contradiction resolutions
- `02_UNIFIED_PRINCIPLE.md` -- Unified governing principle
