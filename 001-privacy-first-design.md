# ADR-001: Privacy-First Design

**Atom ID:** adr-001-privacy-first
**Status:** ACCEPTED
**References:** 2 cross-references in knowledge base corpus
**Context:** spec-kit integration for the knowledge base

---

## Status

Accepted

## Context

The knowledge base ingests, atomizes, and stores personal AI conversations. These conversations contain:
- Personal projects and plans
- Code implementations (potentially proprietary)
- Intellectual exploration and decision-making processes
- References to specific people, organizations, and events

The system must handle this content without exposing it to unauthorized access, leaking it through telemetry, or creating dependencies on third-party services that could access the data.

## Decision

The knowledge base adopts a privacy-first architecture:

1. **Local-first storage.** All data lives in a SQLite file on the operator's machine. No cloud database, no managed service, no data leaving the machine unless explicitly deployed.

2. **No telemetry.** The system sends no usage data, analytics, or crash reports to any external service.

3. **API keys are operator-provided.** OpenAI and Anthropic API calls use the operator's own keys. The system has no backend service that proxies these calls.

4. **Localhost binding by default.** The web server binds to `127.0.0.1:3000` in development mode. Production deployment requires explicit CORS configuration.

5. **Optional authentication.** Auth middleware exists (`ENABLE_AUTH=true`) but is disabled by default for local use.

6. **No third-party analytics.** No Google Analytics, no Sentry, no Segment. The web UI is self-contained.

7. **Embeddings are API calls, not stored externally.** OpenAI embeddings are generated via API but stored locally in ChromaDB on disk. The embedding vectors never persist on OpenAI's servers beyond the API call.

## Consequences

### Positive
- Operator retains full control over their knowledge corpus
- No vendor lock-in beyond API key providers (which are swappable)
- No data breach surface beyond the operator's own machine
- Compliant with GDPR and similar regulations by default (no data processing by third parties)

### Negative
- No cloud sync between machines (operator must handle backup/restore)
- No collaborative features (by design -- single-operator tool)
- Deployment to production requires explicit security hardening

## Related Documents

- `05_CONTRADICTION_RESOLUTIONS.md` -- "Privacy vs. Searchability" contradiction
- `002-multi-format-strategy.md` -- Multi-format handling decisions
- `docs/DEPLOYMENT.md` -- Production security configuration
