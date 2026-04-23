# 02: Authority Framework

**Atom ID:** authority-framework
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Purpose

This framework defines who has authority over what within the knowledge base system. In a single-operator system, authority is not about user roles -- it is about which components have the right to modify which data, and under what conditions.

## Authority Domains

### Domain 1: Data Authority

| Component | Read | Write | Delete | Scope |
|-----------|------|-------|--------|-------|
| Operator (CLI/Web UI) | All | All | All | Full corpus |
| Export pipeline | Sources | Conversations, documents | None | Ingestion only |
| Atomizer | Conversations, documents | Atomic units, tags | None | Processing only |
| Search engine | Atomic units, vectors | Search analytics | None | Read + analytics |
| Intelligence layer | Atomic units | Insights, relationships, smart tags | None | Additive only |
| API server | All (via endpoints) | All (via endpoints) | All (via endpoints) | Rate-limited |

### Domain 2: Configuration Authority

| Setting | Authority | Change Mechanism |
|---------|-----------|-----------------|
| API keys | Operator only | `.env` file (never committed) |
| Database path | Operator only | `.env` or CLI flag |
| Search weights | Operator (via Settings UI) | API call to `/api/settings` |
| Atomization guardrails | Source code only | Code change + rebuild |
| Embedding model | Source code only | Code change + full re-embedding |
| Rate limits | Source code only | Code change + rebuild |

### Domain 3: Schema Authority

| Schema Element | Authority | Migration Path |
|----------------|-----------|---------------|
| SQLite tables | `database.ts` | Versioned migrations (`npm run migrate`) |
| API response format | `api.ts` + `types.ts` | Backward-compatible changes only |
| Atom type enum | `types.ts` | Additive only (never remove a type) |
| Tag vocabulary | Open (auto-generated) | No controlled vocabulary |
| Category vocabulary | Closed (5 categories) | Change requires review |

## Authority Principles

### Principle 1: Additive-Only Intelligence

The intelligence layer (Phase 3) may add insights, tags, and relationships. It may never modify or delete existing atoms, tags, or relationships. Intelligence is augmentation, not correction.

### Principle 2: Operator Override

Any automated decision (type classification, tag assignment, category assignment) can be overridden by the operator via the API. Operator authority supersedes algorithmic authority in all cases.

### Principle 3: Schema Stability

The `AtomicUnit` interface is a contract. Adding optional fields is permitted. Removing fields or changing field types is a breaking change requiring a major version bump and migration.

### Principle 4: Deletion Requires Human Agency

No automated process may delete atoms, conversations, or documents. Deletion is always operator-initiated. The deduplication system (`/api/dedup`) identifies candidates; the operator approves.

## Violation Handling

| Violation | Severity | Response |
|-----------|----------|----------|
| Automated deletion of atoms | Critical | Restore from backup; patch code |
| Intelligence overwriting atoms | High | Revert to checkpoint; audit batch processor |
| Schema breaking change without migration | High | Rollback deploy; create migration |
| Unauthorized API access | Medium | Review CORS/auth configuration |

## Related Documents

- `01-core-principles.md` -- "Intelligence is Extracted, Not Imposed"
- `04_GOVERNANCE_FRAMEWORK.md` -- Governance structure
- `05_CONTRADICTION_RESOLUTIONS.md` -- "Automation vs. Operator Control"
