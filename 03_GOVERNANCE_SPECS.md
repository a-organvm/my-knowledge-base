# 03: Governance Specifications

**Atom ID:** governance-specs
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Purpose

This document specifies the governance rules for the knowledge base system: how decisions are made, how changes are approved, and how the system maintains integrity as it evolves.

## Decision Categories

| Category | Authority | Approval Process | Reversibility |
|----------|-----------|-----------------|---------------|
| Bug fix | Developer | Direct commit | Easy (revert commit) |
| Feature addition | Developer + design review | PR with tests | Medium (feature flag) |
| Schema change | Architect | Migration review + backward compatibility check | Hard (data migration) |
| Principle change | Owner (operator) | Document in principles, audit implications | Hard (cascading effects) |
| Dependency addition | Developer | Security review + license check | Medium (npm uninstall) |
| API breaking change | Architect | Major version bump, deprecation period | Hard (consumer migration) |

## Change Governance

### Code Changes

1. All changes go through version control (git)
2. Tests must pass before merge (`npm test`)
3. TypeScript must compile cleanly (`npm run build`)
4. Commit messages follow Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`

### Schema Changes

1. Changes to database schema require a versioned migration in the migrations directory
2. Migrations must be forward-only (no `ALTER TABLE ... DROP COLUMN` in SQLite)
3. New tables/columns must be documented in `docs/DATABASE_SCHEMA.md`
4. The `AtomicUnit` interface in `types.ts` is a contract: fields can be added (optional) but never removed

### API Changes

1. New endpoints: documented in `docs/API_ENDPOINTS_SUMMARY.md`
2. Breaking changes: major version bump, minimum 30-day deprecation notice
3. Response format changes: backward-compatible (add fields, never remove)
4. Rate limiting changes: document in deployment guide

### Principle Changes

1. New principles added to `01-core-principles.md` with rationale
2. Existing principles amended (never deleted) with change date and justification
3. Contradiction audit (`01_CONTRADICTION_AUDIT.md`) updated to reflect new tensions
4. All affected documents updated to reference amended principle

## Quality Gates

### Pre-Merge

- [ ] All tests pass
- [ ] TypeScript compiles without errors
- [ ] No new lint warnings
- [ ] Database migrations tested (up + down where applicable)
- [ ] API changes documented

### Pre-Release

- [ ] All quality gates pass
- [ ] CHANGELOG.md updated
- [ ] Version bumped in package.json
- [ ] Benchmark report confirms no performance regression
- [ ] Backup taken before production deploy

### Post-Deploy

- [ ] Health check passes (`/api/health`)
- [ ] Search functionality verified
- [ ] Database integrity check (table counts, index health)
- [ ] Monitoring active (logs, error rates)

## Dependency Governance

### Approved Dependencies

| Category | Approved | Justification |
|----------|----------|---------------|
| Database | better-sqlite3 | Performance, no native deps on common platforms |
| Vector DB | chromadb | Open-source, local-first, good Node.js SDK |
| Embeddings | openai (SDK) | Industry standard, cost-effective models |
| Intelligence | @anthropic-ai/sdk | Prompt caching, Claude model quality |
| Testing | vitest | Fast, ESM-native, good TypeScript support |
| Web framework | express | Minimal, well-understood, stable |

### Dependency Review Criteria

1. MIT or Apache-2.0 license (mandatory)
2. Active maintenance (commits within 6 months)
3. No native compilation requirements that break cross-platform
4. Bundle size impact assessed
5. Security advisory history reviewed

## Related Documents

- `02_AUTHORITY_FRAMEWORK.md` -- Authority definitions
- `04_GOVERNANCE_FRAMEWORK.md` -- Broader governance framework
- `CONTRIBUTING.md` -- Contributor guidelines
