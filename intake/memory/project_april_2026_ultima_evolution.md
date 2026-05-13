---
name: April 2026 Ultima Evolution
description: Canonical close-out artifact for the April 2026 session corpus — base tables + projection views + ULTIMA doc
type: project
originSessionId: fdbffc8c-ab0d-4f4c-a245-0e389f2eb624
---
The April 2026 corpus has been frozen as a canonical baseline for the close-out sequence. Future months get measured against these rates.

**Why:** User directive 2026-04-27 — "apply sequence to gathering all sessions from april" + "everything should be combined and broken apart as base function (one of); for viewing as sessions based, as linear timeline, by domain, etc." Storage one; views many.

**How to apply:** April rates DEFINE what "normal" hygiene looks like. May/June/etc. should run the same pipeline (`apply-sequence-extract-events` + the inline scripts in plans v2) and compare deviation against April.

## Artifacts (working state)

- **Plan v1:** `/Users/4jp/.claude/plans/apply-sequence-to-gathering-polymorphic-spring.md`
- **Plan v2 (base+projections):** `/Users/4jp/.claude/plans/apply-sequence-to-gathering-polymorphic-spring-v2.md`
- **Driver script:** `/Users/4jp/.local/bin/apply-sequence-extract-events`
- **Enumeration:** `/Users/4jp/.claude/plans/april-corpus/01-enumeration.jsonl` (287 sessions, 663 MB)
- **Base tables (frozen):** `/Users/4jp/Workspace/organvm/organvm-corpvs-testamentvm/data/corpus/april-2026/`
  - `events.jsonl` — 38,190 records (18 MB)
  - `atoms.jsonl` — 48,633 records (16 MB)
  - `entities.jsonl` — 1,115 unique
  - `verdicts.jsonl` — 2,583 records (287 × 9 predicates)
  - `session-index.jsonl` — 287 records
- **ULTIMA (canonical doc):** `~/Workspace/organvm/organvm-corpvs-testamentvm/docs/corpus/APRIL-2026-ULTIMA.md`
- **Projection views:** `~/Workspace/organvm/organvm-corpvs-testamentvm/docs/corpus/april_views/`
  - A-by-session.md (293 lines)
  - B-timeline.md (32 lines)
  - C-by-domain.md (330 lines)
  - D-by-scope.md (378 lines)
  - E-by-predicate.md (252 lines)

## Standardization baseline (extracted)

- **287 April-2026 sessions** across 18 scopes, 663 MB transcripts, mtime range Apr 4 → Apr 27
- **Unsafe close: 42/287 (14.6%)** — 37 case-1 (user prompted last, no reply) + 5 case-2 (mid-response in today's Warp restart kill window 11:48–11:55 UTC)
- **Hall-monitor failures: 82/287 (28.6%)** — rambling or all-talk-no-shipping patterns
- **Parity failures: 16** — sessions left dirty git working trees
- **Commit-push failures: 16** — same set, unpushed commits
- **Vacuum violations in written files: 0** — N/A patterns only appear in discussion text, not as actual field values
- **IRF cross-references: 110/287** — sessions touched IRF-tagged paths
- **Sisyphus PASS: 243/287 (84.7%)** — sessions closed substantively

## State / Pending

**State:** shipped 2026-04-27. Base tables frozen (re-runs go to a new run-dated dir). ULTIMA doc and projection views are canonical.

**Pending follow-up:**
1. Commit + push the corpus dir (chezmoi auto-push concern still applies — user authorizes manually)
2. Implement predicate #6 (additive) properly via git-diff history when ready
3. Implement predicate #9 (universal_context) cross-reference in a Stage 4 follow-up
4. Recover the 42 unsafe-close sessions one-by-one from § III of ULTIMA (resume commands present)
5. Run same pipeline against March 2026, then May, to populate the multi-month baseline

**Next session must know:**
- The 5 today-killed sessions (8bac99ae, 5ebeebd3, ac066cac, 116a45d8, f6adcad7) are in scope `-Users-4jp`. Resume commands at ULTIMA § III.
- The pipeline driver is `/Users/4jp/.local/bin/apply-sequence-extract-events` (events extractor only — atoms/entities/verdicts logic is inlined in shell, not yet refactored into a single CLI).
