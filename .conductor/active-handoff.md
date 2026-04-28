# Active Handoff: ORGAN-I Theory Work → Gemini

**Created:** 2026-04-28
**Origin agent:** Claude Opus 4.7 (1M context), session "typed-hejlsberg"
**Target agent:** Gemini (CLI v0.38.x or 3-Pro)
**Authority:** User directive 2026-04-28 — *"all theory work as gemini"* (Action → all theory work as gemini)
**Cross-verification:** REQUIRED — Gemini's output will be verified by Claude via `conductor fleet verify` before merge.

---

## Scope

**Domain:** ORGAN-I (Theoria) — foundational theory, recursive engines, symbolic computing.

**Repos in scope:**
- `~/Workspace/organvm/my-knowledge-base` (this repo — Phase 5 ingestion flagship)
- `~/Workspace/organvm/tmp_organvm-i-theoria.github.io` (theoria org pages)
- `~/Workspace/organvm/organvm-i-theoria/*` (~20 sibling repos under the theoria organ)
- Cross-link surface: `meta-organvm/organvm-corpvs-testamentvm/INST-INDEX-RERUM-FACIENDARUM.md` (governance index, read-only consume)
- Cross-link surface: `meta-organvm/praxis-perpetua/library/` (SOPs / standards reference)

**Locked / out-of-scope:**
- Any repo outside the theoria organ (Ergon products, Poiesis art, Logos publishing, etc.) — *do not modify*.
- Anything in `~/Workspace/4444J99/` (personal scope) — *do not modify*.
- The `events.jsonl` corpus pipeline files — *gitignored, treat as read-only*.

---

## Concrete Task List

Ranked by zero-dependency / lowest-friction entry first. Pick any one to start; cross-task dependencies are noted.

### T1 — SOP Operational Master Index
**IRF:** IRF-SYS-080
**Status:** Open. 23 SOPs in `meta-organvm/praxis-perpetua/orchestration-start-here/docs/`, 99 in `meta-organvm/praxis-perpetua/library/`. No unified registry.
**Deliverable:** A single JSON or YAML index covering every SOP across both directories, with fields: `id`, `name`, `scope`, `lifecycle_stage`, `path`, `last_modified`.
**Output location:** `meta-organvm/praxis-perpetua/library/SOP-MASTER-INDEX.{json,yaml}` (pick one; YAML preferred for human-readability).
**Dependencies:** None. Pure inventory + serialization.

### T2 — UMFAS Monad Merge Decision
**IRF:** IRF-SYS-085 (PARTIALLY ADVANCED)
**Status:** Monad synthesizer built on branch `S-2026-04-06`; 27/27 entities CANONICAL; merge decision pending.
**Deliverable:** Decision document at `organvm-i-theoria/recursive-engine--generative-entity/docs/umfas-merge-verdict.md` recording: empirical comparison against main, merge plan, rollback plan, lifecycle pipeline automation hooks.
**Dependencies:** Read existing branch + main; produce verdict. Empirical comparison required (do not merge without).

### T3 — Phase 5 Apple Notes Adapter
**Status:** Phase 5 Omni-Source Ingestion in progress; LocalFileSource working, Dropbox indexed (26 docs). Apple Notes adapter not yet built.
**Deliverable:** Adapter implementation in `my-knowledge-base/src/adapters/apple-notes/` with: connection (read-only), per-note extraction → atom JSONL, semantic-search verification.
**Constraints:** Read-only access (no Notes mutation). No LaunchAgent — on-demand CLI invocation only (HARD RULE).

### T4 — Knowledge Graph Confidence Propagation
**Status:** `relationship-detector.ts` built with 5 types (related, prerequisite, expands-on, contradicts, implements). Graph traversal optimization and confidence propagation pending.
**Deliverable:** Confidence-propagation algorithm + tests in `my-knowledge-base/src/graph/confidence/`.
**Dependencies:** Read existing relationship-detector to understand the type system before designing propagation.

### T5 — Embedding Model Benchmark Expansion
**Status:** Phase 2 complete with OpenAI text-embedding-3-small. Cohere, local Llama/Mistral, multi-modal pending.
**Deliverable:** Benchmark suite covering 4+ embedding providers with shared dataset, output `my-knowledge-base/benchmarks/embeddings/results-2026-04-28.md`.
**Constraints:** Local models via on-demand CLI invocation only.

### T6 — Theory-to-Concrete Handoff Governance Integration
**IRF:** IRF-SYS-078
**Status:** Triple Reference Principle formalized; 27/27 entities at 3/3 heartbeats. Integration into `governance-rules.json` + org-wide compliance audit pending.
**Deliverable:** Updated `meta-organvm/organvm-corpvs-testamentvm/governance-rules.json` with triple-reference enforcement rules + a compliance audit report at `meta-organvm/organvm-corpvs-testamentvm/docs/audits/2026-04-triple-reference-compliance.md`.

### T7 — Prompt Atomization Second-Pass Triage Protocol
**Status:** 11,980 intentions in backlog (session 2026-04-23). First-pass triage built. Second-pass + dedup pipeline + human-AI review cascade pending.
**Deliverable:** Protocol document at `meta-organvm/praxis-perpetua/library/SOP--prompt-atomization-second-pass.md` + reference implementation in `my-knowledge-base/src/prompt-pipeline/triage-v2/`.

---

## Optional Theory-Substrate Specs (T8–T10)

These specs exist but are unbuilt. Gemini may pick any/all if T1–T7 are progressing well; otherwise leave them queued.

### T8 — Layer G Meta-Process Repetition (Second-Order Generative)
**Spec:** `~/.claude/plans/2026-04-27-meta-process-repetition-second-order-generative.md` (mirrored at chezmoi ref 1e7e9d4).
**Deliverable:** 6 initial YAMLs for runtime instantiation. Highest-leverage substrate work per origin-session notes.

### T9 — Layer E Filter Substrate (Alchemical Distillation)
**Spec:** `~/.claude/plans/2026-04-27-filter-substrate-alchemical-distillation.md`.
**Deliverable:** Distillation operator producing canonical atoms; requires `classifications.jsonl` sidecar + generative-form extraction.

### T10 — Titan-Keeper Architecture
**Spec:** `~/.claude/plans/2026-04-25-titan-keeper-architecture.md`.
**Deliverable:** Reference implementation. Architectural blueprint exists; not yet executed.

---

## Constraints (HARD RULES)

These are non-negotiable. Violating any of these will trigger cross-verification failure.

1. **No LaunchAgents.** Every prior LaunchAgent froze the machine. On-demand CLI invocation only. (`feedback_no_launchagents.md`)
2. **No plan overwrites.** Plans are sculpture — versioned suffixes (`-v2.md`, `-v3.md`), never overwrite. (`feedback_plans_are_sculpture.md`)
3. **Atoms are permanent.** Never batch-close atoms. Stale ≠ dead. Only the human closes. (`feedback_atoms_are_permanent.md`)
4. **Triple reference required.** Every entity must exist in ≥3 locations (IRF row + repo file + GitHub issue). (`feedback_triple_reference`)
5. **Nothing local only.** Every artifact must be git-tracked AND pushed. "On disk" = not done.
6. **Fix bases, not outputs.** Modify the template/source/pipeline, never patch generated outputs.
7. **No human-impersonating outbound messages.** Drafts only — the human sends.
8. **Never overwrite production data files wholesale.** Read before write; targeted edits only. Protected: `registry-v2.json`, `governance-rules.json`, `system-metrics.json`, every `seed.yaml`.

---

## Provenance (what came before)

- 2026-04-28 prior Claude session — shipped 3 commits (corpus-extract patch, iMessage drafts mirror, IRF-SEC-010 audit) but stranded 4 untracked items at the seam.
- 2026-04-28 Gemini CLI session — was redirected to "all theory work as gemini" but only oriented (file history audit + theoria mapping); never produced a handoff envelope. **This file closes that loop.**
- 2026-04-28 Claude session "typed-hejlsberg" (this one) — routed all 4 stranded items, shipped 6 commits across 3 repos, fixed the global pre-commit hook architecturally, then composed this envelope.

---

## Verification Hooks

When Gemini completes any task above:

1. **Self-test:** Tests pass locally (where applicable).
2. **Triple-reference:** Each new entity must appear in IRF row + repo file + GitHub issue.
3. **Cross-verify:** Run `conductor fleet verify` before claiming completion. Claude will independently verify.
4. **Memory write:** Save artifact-level memory (`project_artifact_*.md`) per the `Working State Capture` SOP in `~/CLAUDE.md`.

---

## Communication

If Gemini gets blocked or needs clarification: write to `.conductor/handoff-questions.md` in this repo. The next Claude session will reconcile.

If Gemini completes all of T1–T7: rename this file to `.conductor/handoff-completed-2026-04-28.md` and write a fresh `active-handoff.md` with new scope (or delete if no follow-on).

*— end envelope —*
