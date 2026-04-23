# 03: Manifesto Reframed (Governance Edition)

**Atom ID:** manifesto-reframed-governance
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus
**Decision Context:** Option A selected -- "Create manifesto + governance framework now"

---

## The Governance Manifesto

### Why Governance Matters for a Personal Tool

A single-operator knowledge base does not need bureaucratic process. It needs structural integrity. Governance for this system is not about approvals and committees -- it is about ensuring that the system's behavior remains predictable, its data remains trustworthy, and its evolution remains coherent.

### The Five Governance Commitments

#### 1. The Schema is a Contract

The `AtomicUnit` interface, the database schema, and the API response format are contracts. Changing them has consequences. Adding is permitted. Removing is breaking. Breaking requires a major version bump and migration.

This is not bureaucracy. This is engineering discipline applied to a data system that stores the operator's intellectual output.

#### 2. Intelligence is Additive, Never Destructive

The Phase 3 intelligence layer (InsightExtractor, SmartTagger, RelationshipDetector) may add to the corpus. It may never modify or delete existing content. If an LLM-generated insight is wrong, the operator deletes it. The system never auto-corrects its own output.

This prevents feedback loops where bad intelligence corrupts good data.

#### 3. Deletion Requires Human Agency

No automated process deletes atoms. The deduplication system identifies candidates. The operator approves. Batch operations create backups before executing. Every deletion is reversible within the backup retention window.

#### 4. Cost is Tracked, Not Assumed

Every LLM call reports its token usage and cost. Batch operations display running totals. The system never makes unbounded API calls. Cost tracking is not an optimization -- it is a requirement.

#### 5. Versioning is Non-Negotiable

Every database state is recoverable via backup. Every code change is tracked via git. Every migration is forward-only and timestamped. The system can be rolled back to any prior state.

### The Anti-Governance Commitment

What this governance framework explicitly does NOT require:

- No approval workflows (single operator -- decisions are immediate)
- No code review process (self-review via tests and type checking)
- No release committees (deploy when ready)
- No access control matrix (one user, full access)
- No compliance reporting (MIT license, no regulatory burden)

The governance framework exists to protect the data, not to slow the operator.

## Related Documents

- `01_MANIFESTO_REFRAMED.md` -- The epistemological manifesto
- `03_GOVERNANCE_SPECS.md` -- Technical governance specifications
- `04_GOVERNANCE_FRAMEWORK.md` -- Structural governance framework
