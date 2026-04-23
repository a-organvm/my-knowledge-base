# 04: Governance Framework

**Atom ID:** governance-framework
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus
**Decision Context:** Option A -- "Create manifesto + governance framework now"

---

## Framework Purpose

This governance framework defines the structural rules that keep the knowledge base system coherent, its data trustworthy, and its evolution intentional. It synthesizes the authority framework (`02_AUTHORITY_FRAMEWORK.md`), governance specs (`03_GOVERNANCE_SPECS.md`), and governance manifesto (`03_MANIFESTO_REFRAMED.md`) into an actionable operational framework.

## Governance Layers

### Layer 1: Data Integrity

**Rule:** Data in the knowledge base is the operator's intellectual property. Its integrity is the system's primary obligation.

| Mechanism | Purpose | Implementation |
|-----------|---------|---------------|
| Automated backups | Recovery from corruption | `npm run backup` (timestamped SQLite copies) |
| Migration versioning | Schema evolution without data loss | Sequential, forward-only migrations |
| Additive intelligence | Prevent LLM output from corrupting source data | Phase 3 components write to separate tables |
| Deletion gates | Prevent accidental data loss | Dedup suggests, operator approves |

### Layer 2: API Contract Stability

**Rule:** External consumers of the API must not break when the system evolves.

| Mechanism | Purpose | Implementation |
|-----------|---------|---------------|
| Semantic versioning | Signal breaking changes | package.json version |
| Response format contract | Consistent API responses | `{ success, data, pagination?, timestamp }` |
| Additive field policy | Backward compatibility | New fields are optional; existing fields never removed |
| Deprecation period | Consumer migration time | 30 days minimum for breaking changes |

### Layer 3: Cost Governance

**Rule:** LLM operations must be cost-tracked and cost-bounded.

| Mechanism | Purpose | Implementation |
|-----------|---------|---------------|
| Prompt caching | 90% cost reduction | `ClaudeService` caching implementation |
| Token tracking | Cost visibility | `getTokenStats()` after every batch |
| Cost ceiling | Prevent runaway costs | $1/1,000 ops threshold |
| Batch checkpoints | Prevent wasted work on failure | Resumable batch processor |

### Layer 4: Quality Governance

**Rule:** Code quality and test coverage are non-negotiable gates.

| Mechanism | Purpose | Implementation |
|-----------|---------|---------------|
| Type checking | Compile-time error detection | TypeScript strict mode |
| Automated tests | Regression prevention | Vitest (1,463 tests) |
| Coverage tracking | Quality visibility | 62.7% coverage |
| Lint enforcement | Code style consistency | ESLint configuration |

## Governance Decision Tree

```
Is this a data change?
├── YES → Does it delete data?
│         ├── YES → Requires operator approval + backup
│         └── NO  → Does it modify existing atoms?
│                   ├── YES → Prohibited (intelligence is additive only)
│                   └── NO  → Proceed with standard pipeline
└── NO  → Is this a schema change?
          ├── YES → Create migration + update docs + test
          └── NO  → Is this an API change?
                    ├── YES → Backward compatible?
                    │         ├── YES → Proceed
                    │         └── NO  → Major version bump + deprecation
                    └── NO  → Standard code change process
```

## Governance Review Schedule

| Review | Frequency | Scope |
|--------|-----------|-------|
| Contradiction audit | Per major feature | All principles vs. implementation |
| Cost review | Monthly | LLM token usage and costs |
| Dependency audit | Quarterly | Security advisories, license compliance |
| Backup verification | Weekly | Restore test from latest backup |
| Performance benchmark | Per release | Latency, throughput, resource consumption |

## Related Documents

- `02_AUTHORITY_FRAMEWORK.md` -- Authority definitions
- `03_GOVERNANCE_SPECS.md` -- Technical specifications
- `03_MANIFESTO_REFRAMED.md` -- Governance philosophy
- `01-core-principles.md` -- Governing principles
