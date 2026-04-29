# Refactor: Raw Dump → Cascading Workstreams

**Plan date:** 2026-04-29
**Plan slug:** `cascading-workstreams-refactor`
**Project-scoped destination (post-approval):** `~/Workspace/organvm/my-knowledge-base/.gemini/plans/2026-04-29-cascading-workstreams-refactor.md`

---

## Context

The user pasted a ~200-line raw dump comprising three tangled layers:
1. **Claude Code session titles** (24 distinct, system-generated cosmetic labels).
2. **Editor-tab bleed from Gemini Antigravity** — the same 19 file paths repeated ~10× because the IDE's open-files panel cycled while pasted.
3. **~25 unique file paths** spanning 3 active repos (`my-knowledge-base`, `sovereign-systems--elevate-align`, `hokage-chess`) plus contamination/historical cruft (Feb 2026 hang fix, Gemini chat JSONs, glitched filenames, an empty buffer).

The dump is a *symptom* of supersession failure: v1+v2 plan files co-exist with no archive marker; `~/.gemini/antigravity/brain/<UUID>/artifacts/*.resolved` deliverables persist forever; drafts and consolidated outputs share `intake/drafts/`. A previous Apr 28 refactor (`brain/5efe471b/.../refactored_workstreams.md.resolved`) cleanly separated **W1 (Maddie Spiral)** and **W2 (Rob/hokage-chess)** but explicitly declared "two completely independent workstreams" — it missed **W3 (knowledge-base wiki consolidation)** entirely. The Apr 29 `gap_tracker.md.resolved` audited the previous refactor against disk reality and surfaced 28 actionable gaps (3 phantoms, 36 orphans, byte-identical duplicates, two oversized session dumps that will corrupt `wiki-compiler.ts` ingestion).

**This plan extends — does not replace — the Apr 28 refactor.** It adopts W1+W2 verbatim from `refactored_workstreams.md.resolved`, adds the four missing streams (W3–W6), folds the gap_tracker's actionable items into W3's checklist, and produces a single canonical artifact that can be promoted into the repo and linked from `TOTAL_RECORD.md`.

**Intended outcome:** One canonical document `my-knowledge-base/CASCADING_WORKSTREAMS.md` holding W1–W6; `~/.gemini/antigravity/brain/<UUID>/` artifacts promoted to repo paths; v1 plans archived; oversized files triaged before `wiki-compiler` runs; `TOTAL_RECORD.md` updated with the 5 missing links (U1–U5).

---

## Triage Verdicts (every line of the dump)

### Session titles → workstream routing

| Title | Workstream | Disposition |
|-------|-----------|-------------|
| Inactive Repository Hygiene Audit (sovereign-systems--elevate-align) | W5 | Memo to audit index |
| Installing Whisper Speech Recognition | **W4** | Recovery search |
| Designing Modular Repository Architectures | W5 | Cross-cut memo |
| Visualizing Workspace Recursive Abstractions | W5 | Cross-cut memo |
| Auditing Workspace Timezone Configuration | W5 | Memo |
| Implementing macOS Voice Bridge (sign-signal--voice-synth) | **W4** | Recovery search |
| Auditing Terminal Session History (the-actual-news) | W5 | Memo (note: separate repo) |
| Closing Maddie's Spiral Gaps | W1 | Subsumed by `spiral_audit_and_forms` |
| Refactoring Spiral Project Documentation | W1 | Subsumed |
| Consolidating Disparate Project Artifacts | W3 | TOTAL_RECORD §3 |
| Auditing Workspace Activity Logs | W3+W5 | TOTAL_RECORD §1 |
| Synthesizing Symbol Graph Artifacts | UNKNOWN | Investigate before routing |
| Auditing Maddie Spiral Architecture | W1 | Subsumed |
| Cataloging Spiral And Node Wishes | W1 | Subsumed by `maddie_spiral_wishes` |
| Auditing Editor File History | W3 | TOTAL_RECORD §1 |
| Compiling Knowledge Base Wiki | W3 | Active task — blocked by oversized files |
| Finalizing Maddie Trailing Catalog | W1 | Subsumed |
| Compiling Disparate Person-Tied Trails | W3 | TOTAL_RECORD §3 |
| Potentials Cataloging and Routing | W3 | Already at `docs/routing/` |
| Formalizing Person-Tied Project Architectures | **W6** | Pattern extraction |
| Streamlining Rob-Maddie Project Artifacts | W1+W2 cross-cut | Subsumed by previous refactor |
| Initializing Warm-Clock Project Integration | UNKNOWN | Investigate |
| Distilling Person-Project Macro Patterns | **W6** | Already at `docs/patterns/` |

### File paths → verdicts

| Path | Verdict | Action |
|------|---------|--------|
| `my-knowledge-base/.gemini/plans/2026-04-28-master-file-mapping-and-assembly.md` | W3 plan v1 — **SUPERSEDED** | Archive to `.gemini/plans/archive/2026-04/` |
| `my-knowledge-base/.gemini/plans/2026-04-28-master-file-map-v2.md` | W3 plan v2 — **CURRENT** | Keep |
| `my-knowledge-base/.gemini/plans/2026-04-28-total-record-consolidation.md` | W3 companion plan | Keep |
| `my-knowledge-base/.gemini/plans/Untitled-1` | NOISE — 331-byte bootstrap breadcrumb | Delete |
| `my-knowledge-base/TOTAL_RECORD.md` | W3 hub — **CANONICAL** | Update with U1–U5 + W4–W6 links |
| `my-knowledge-base/config/sources.yaml` | W3 scaffolding | Keep |
| `sovereign-systems--elevate-align/.gemini/plans/2026-04-28-spiral-catalog-audit-and-brainstorming-forms.md` | W1 plan | Keep |
| `sovereign-systems--elevate-align/docs/process-extraction/2026-04-04-reusable-processes.md` | W6 source | Keep |
| `~/.gemini/antigravity/brain/f0c19e07-.../artifacts/maddie_spiral_wishes.md.resolved` | W1 source | **Promote** → `sovereign-systems--elevate-align/docs/intake/maddie_spiral_wishes.md` |
| `~/.gemini/antigravity/brain/4feea892-.../artifacts/spiral_audit_and_forms.md.resolved` | W1 source | **Promote** → `sovereign-systems--elevate-align/docs/audits/spiral_audit_and_forms.md` |
| `~/.gemini/antigravity/brain/2bdd447b-.../master_file_map.md.resolved` | Near-duplicate of gap_tracker | Archive (keep gap_tracker) |
| `~/.gemini/antigravity/brain/5efe471b-.../artifacts/gap_tracker.md.resolved` | W3 audit | **Promote** → `my-knowledge-base/docs/audits/gap_tracker.md` |
| `~/.gemini/antigravity/brain/5efe471b-.../walkthrough.md.resolved` | NOISE — Gemini meta-narrative | Archive to `docs/archive/gemini-meta/` |
| `~/.gemini/antigravity/brain/5efe471b-.../artifacts/refactored_workstreams.md.resolved` | W1+W2 prior synthesis | **Promote + extend** → `my-knowledge-base/CASCADING_WORKSTREAMS.md` (with W3–W6 added) |
| `~/Downloads/Distilling Person-Project Macro Patterns.md` | W6 | Move → `my-knowledge-base/docs/patterns/` |
| `~/Downloads/Streamlining Rob-Maddie Project Artifacts.md` | **PHANTOM** — gap_tracker confirmed missing | Strike from any plan that references it |
| `~/Workspace/4444J99/hokage-chess/hokage-2026-04-28-114108-audit.txt` | W2 raw transcript | ✓ Already archived per gap_tracker S2 |
| `~/Workspace/4444J99/hokage-chess/⏺ I'll audit every claimed artifact on d.ini` | NOISE — glitched filename | ✓ Already archived |
| `~/.gemini/plans/2026-02-18-fix-claude-hang.md` | HISTORICAL — Feb, unrelated | Move to `~/.gemini/plans/archive/2026-02/` |
| `~/.gemini/tmp/4jp/chats/session-2026-04-28T06-38-af959950.json` | NOISE — 1.4MB chat log | Confirm gitignored; never paste |
| `settingseditor` (literal, repeated) | NOISE — Gemini editor tab leak | N/A |

---

## The Six Cascading Workstreams

```
TIER 0 — substrate (BLOCKS DOWNSTREAM)
   W3: Knowledge Base Wiki Consolidation
   ├── Triage 2 oversized session dumps
   ├── Dedup 35 byte-identical draft pairs
   └── Then `wiki-compiler.ts` can run safely
                         │
                         ▼
TIER 1 — active client/collaborator (parallel)
   W1: Maddie Sovereign Spiral ──┐
   W2: Rob/Anthony hokage-chess  │
                                 │
                                 ▼
TIER 2 — recovery (isolated)
   W4: Voice Synthesis ◄─── needs revival
                                 │
                                 ▼
TIER 3 — extraction (retrospective)
   W6: Macro Pattern Extraction ◄─── consumes W1+W2 outputs
                                 │
                                 ▼
TIER 4 — meta (observes all, blocks none)
   W5: Workspace System Hygiene
```

### W1 — Maddie Sovereign Spiral
**Status:** ACTIVE · 8 client blockers · architecture LOCKED at 13 nodes
**Source:** Adopted verbatim from `refactored_workstreams.md.resolved` §A (Apr 28)

**Summary.** 13-node interactive spiral on `elevatealign.com`. Phases ELEVATE/ALIGN/UNLOCK. Three sessions (Apr 27–28) cataloged client wishes, audited completeness against 15 source documents, produced 7 brainstorming forms. Awaiting Maddie's decisions on Q1–Q8 questionnaire (sent Apr 20, unanswered).

**Canonical locations:**
- Catalog: `sovereign-systems--elevate-align/docs/intake/maddie_spiral_wishes.md` *(TO PROMOTE from `brain/f0c19e07/`)*
- Audit + 7 Forms: `sovereign-systems--elevate-align/docs/audits/spiral_audit_and_forms.md` *(TO PROMOTE from `brain/4feea892/`)*
- Project plan: `sovereign-systems--elevate-align/.gemini/plans/2026-04-28-spiral-catalog-audit-and-brainstorming-forms.md` ✓
- Live config: `sovereign-systems--elevate-align/src/data/hub.config.ts`

**Governance:**
- Architecture LOCKED — node count and phase assignments don't change without explicit Maddie decision
- G3 (emoji drift) and G4 (Node 11 phase mismatch) are fixable without client input — fix in `hub.config.ts`
- Forms 1–6 require Maddie binary decisions before next iteration; Form 7 studio-drafted

**Checklist:**
- [ ] Promote `maddie_spiral_wishes.md.resolved` → repo `docs/intake/`
- [ ] Promote `spiral_audit_and_forms.md.resolved` → repo `docs/audits/`
- [ ] Send Forms 1–6 to Maddie (vibe + binary decisions)
- [ ] Fix G3 (emoji drift) in `hub.config.ts`
- [ ] Fix G4 (Node 11 phase = UNLOCK in code) in `hub.config.ts`
- [ ] Rotate CF API token (5 min, unblocks CI/CD)
- [ ] Wait on Maddie: GHL quiz URL · affiliate URLs · video · 104 content atoms · CF dashboard · Q1–Q8

**Cascades into:** W6 (process IP → `2026-04-04-reusable-processes.md`)

---

### W2 — Rob/Anthony hokage-chess + Lawsuit Substrate
**Status:** ACTIVE · forms staged for offline execution · 56/56 tests green
**Source:** Adopted verbatim from `refactored_workstreams.md.resolved` §B (Apr 28)

**Summary.** Apr 28 audit produced: stale-test reconciliation (52 → 56 tests passing, parametric lexicon suite added), 10 Rob blocker-forms, 10 vendor-agnostic AI-session workstreams, 5-cluster sequencing (A→B‖C→D→E), 10 personas (P1–P10), 13-form offline pre-work package (A–M), parallel `domus-semper-palingenesis` lawsuit substrate audit (5 gaps, 4 fixed in-session).

**Canonical locations:**
- Audit + 10 Rob forms: `hokage-chess/docs/business/forms/`
- Workstream catalog: `hokage-chess/docs/business/workstreams/README.md`
- Cluster sequencing: `hokage-chess/docs/business/workstreams/sequencing.md`
- Persona taxonomy: `~/.claude/plans/2026-04-28-domain-persona-workstreams-taxonomy.md`
- 13-form offline package: `~/.claude/plans/audit-session-audit-encompassing-parsed-orbit.md`
- Chezmoi mirror: `domus-semper-palingenesis/private_dot_claude/plans/2026-04-28-audit-reverify-and-external-forms-package.md` ✓ (P1 closed Apr 29)

**Orphan reconciliation (from gap_tracker §2a — three HIGH-priority docs not yet linked):**
- `hokage-chess/docs/business/2026-04-25-business-plan-v2.md` (54KB) — link as W2 primary reference
- `hokage-chess/docs/business/2026-04-25-strategy-v6-master.md` (50KB) — supersedes v4/v5
- `hokage-chess/docs/business/2026-04-27-rob-evidence-of-existence-system-audit.md` (20KB) — cite in B.3

**Governance:**
- A before D always (substrate before production); skipping E (Quality) ships unaudited output
- One persona per session — mixing corrupts both
- Persona dispatch by measured strengths, not familiarity
- Forms 02 → 05 → 07 = ~12 min path clearing 3 of 8 Rob-blockers

**Checklist:**
- [ ] Execute Form 02 → 05 → 07 (12 min, 3 blockers)
- [ ] Execute Form A (Beddome LinkedIn DM, highest leverage)
- [ ] Resolve duplicate transcript pair `2026-04-25-rob-anthony-funnel-audit-transcript.md` ≡ `rob-call-transcript-source.md` (32,176 bytes byte-identical) — keep one, archive other
- [ ] Link 3 HIGH-priority orphans into `workstreams/README.md`
- [ ] Activate Cluster A — Vocabulary Cartographer drafts FITNESS_LEXICON

**Cascades into:** W6 (persona taxonomy → vendor-agnostic library), W3 (audit transcripts → wiki ingestion after triage)

---

### W3 — my-knowledge-base Wiki Consolidation
**Status:** SUBSTRATE · BLOCKS DOWNSTREAM INGESTION · 187/235 tasks (80%)
**Source:** NEW — discovered by `gap_tracker.md.resolved` (Apr 29); missing from previous refactor

**Summary.** TypeScript knowledge atomizer (`wiki-compiler.ts`) with SQLite + ChromaDB + Anthropic SDK. 118 brain artifacts swept (Apr 28 ✓). 39 byte-identical drafts dedup'd (Apr 29 ✓). **35 more duplicate pairs remain** in `intake/drafts/`. **Two oversized files flagged HIGH risk for wiki corruption:** `re-ini-plan-Claude.md` (427KB) and `ark-universal.md` (1.2MB) — both likely full session dumps that will overwhelm atomization. Volume `/Volumes/4444-livii` not mounted (blocks DIRECTORY_KEY recovery).

**Canonical locations:**
- Hub: `my-knowledge-base/TOTAL_RECORD.md` (needs U1–U5 link additions)
- Plan v2: `my-knowledge-base/.gemini/plans/2026-04-28-master-file-map-v2.md` ✓ CURRENT
- Companion plan: `my-knowledge-base/.gemini/plans/2026-04-28-total-record-consolidation.md`
- Gap audit: `my-knowledge-base/docs/audits/gap_tracker.md` *(TO PROMOTE from `brain/5efe471b/`)*
- Sources config: `my-knowledge-base/config/sources.yaml`
- Pipeline: `my-knowledge-base/src/wiki-compiler.ts`, `db/knowledge.db`

**Supersession decisions (record explicitly):**
| Keep | Archive |
|------|---------|
| `master-file-map-v2.md` | `master-file-mapping-and-assembly.md` (v1) → `.gemini/plans/archive/2026-04/` |
| `gap_tracker.md` (more comprehensive) | `master_file_map.md.resolved` (in `brain/2bdd447b`) → `docs/archive/gemini-meta/` |
| `refactored_workstreams.md.resolved` (extended into `CASCADING_WORKSTREAMS.md`) | `walkthrough.md.resolved` → `docs/archive/gemini-meta/` |
| (none — delete) | `Untitled-1` (331-byte bootstrap) |

**Critical pre-ingestion gates (HIGH-priority blockers from gap_tracker):**
1. Triage `re-ini-plan-Claude.md` (427KB) — atomize manually or quarantine
2. Triage `ark-universal.md` (1.2MB) — same
3. Dedup remaining 35 `-Claude` twin pairs in `intake/drafts/` (script: keep `-Claude.md`, delete twins)
4. Diff `intake/audits/antigravity-files.pdf` vs `antigravity-files-v2.pdf` (both 7.0MB — possibly identical)
5. Resolve empty `~/Workspace/.gemini/plans/2026-04-28-workspace-assembly-and-mapping.md` (0 bytes) — populate or delete

**Governance:**
- **NEVER overwrite `db/knowledge.db` wholesale** (per `Workspace/CLAUDE.md` data integrity rule)
- **Read-before-write** on `TOTAL_RECORD.md` (hub file)
- **Plan supersession protocol:** when v2 supersedes v1, MOVE v1 to `archive/`, don't leave as sibling
- **Pre-ingestion gate:** any file >100KB in `intake/drafts/` must be triaged before atomization runs

**Checklist:**
- [ ] Dedup `intake/drafts/` 35 pairs
- [ ] Triage `re-ini-plan-Claude.md` (427KB)
- [ ] Triage `ark-universal.md` (1.2MB)
- [ ] Diff antigravity PDFs; archive duplicate
- [ ] Promote `gap_tracker.md.resolved` → `docs/audits/`
- [ ] Archive `master_file_map.md.resolved` (duplicate of gap_tracker)
- [ ] Archive `walkthrough.md.resolved`
- [ ] Delete `.gemini/plans/Untitled-1`
- [ ] Archive v1 master-file-mapping plan → `.gemini/plans/archive/2026-04/`
- [ ] Resolve empty `~/Workspace/.gemini/plans/2026-04-28-workspace-assembly-and-mapping.md`
- [ ] Add U1–U5 links to `TOTAL_RECORD.md` (refactored workstreams · Rob workstream catalog · persona taxonomy · 13-form package · brain sweep results summary)
- [ ] Mount `/Volumes/4444-livii` → recover DIRECTORY_KEY
- [ ] Run `npm run prepare-db` then `wiki-compiler.ts` after triage gates clear

**Cascades into:** ALL — once W3 substrate is clean, W1/W2/W6 artifacts ingest without corrupting search

---

### W4 — Voice Synthesis (sign-signal--voice-synth + Whisper)
**Status:** FORGOTTEN · recovery search required
**Source:** NEW — surfaced from session titles only; no artifacts found in current exploration

**Summary.** Two session titles reference voice work (`Installing Whisper Speech Recognition`, `Implementing macOS Voice Bridge sign-signal--voice-synth`). No corresponding files in any explored directory. No artifacts in `brain/`, `~/.claude/plans/`, or any repo cited in the dump. Likely a separate experimental branch or earlier session that didn't get linked to TOTAL_RECORD or the conductor ecosystem.

**Recovery checklist (verifiable steps):**
- [ ] `find ~/Workspace -type d -name 'sign-signal*' 2>/dev/null` — does the repo exist locally?
- [ ] If yes: `git -C <path> log --all --oneline | head -50`
- [ ] `find ~/.claude/projects -name '*.jsonl' | xargs grep -l -i 'whisper\|voice bridge'`
- [ ] `find ~/.claude/plans -iname '*voice*' -o -iname '*whisper*' -o -iname '*sign-signal*'`
- [ ] If artifacts surface: open W4 with proper repo + plan
- [ ] If not: close as session-only exploration, log IRF entry "ATTEMPTED 2026-04-XX, not productionized"

**Governance:**
- Pure recovery; do not advance W1/W2/W3 actions for it until artifacts surface
- If revived, W4 lives in `sign-signal--voice-synth` as a standalone organ

---

### W5 — Workspace System Hygiene (META)
**Status:** OBSERVATIONAL · ongoing · blocks no project stream
**Source:** NEW — synthesized from 7 session titles previously unrouted

**Summary.** A cluster of audit-style sessions: workspace timezone, terminal session history, repository hygiene, workspace activity logs, editor file history, modular architecture, recursive abstractions. These are signals about *the meta-system itself* — not project work. Previous refactor missed them.

**Canonical destination:** `meta-organvm/audits/` + cross-cutting `Workspace/CLAUDE.md` updates

**Governance:**
- W5 outputs are MEMOS, not features — single short markdown per audit, indexed in `meta-organvm/audits/INDEX.md`
- W5 never blocks W1/W2/W3 — observation, not action
- If a W5 audit surfaces a structural problem, spawn an IRF item; don't grow W5 into project work

**Checklist:**
- [ ] Create `meta-organvm/audits/2026-04-29-INDEX.md` listing the 7 hygiene audits
- [ ] One-line memo per audit, citing originating session
- [ ] Route any specific repo findings (e.g. inactive-repository hygiene) → repo-onboarding queue
- [ ] Move `~/.gemini/plans/2026-02-18-fix-claude-hang.md` → `~/.gemini/plans/archive/2026-02/`

---

### W6 — Macro Pattern Extraction (CROSS-CUTTING)
**Status:** RETROSPECTIVE · consumes W1+W2 outputs
**Source:** NEW — synthesized from `2026-04-04-reusable-processes.md` + Downloads + persona taxonomy

**Summary.** "Distilling Person-Project Macro Patterns" + "Formalizing Person-Tied Project Architectures" + `2026-04-04-reusable-processes.md` are pattern-extraction efforts. The persona taxonomy (P1–P10) and 10 vendor-agnostic AI-session workstreams from W2 are also W6 outputs. Goal: turn client-specific work into studio IP.

**Canonical locations:**
- Maddie process IP: `sovereign-systems--elevate-align/docs/process-extraction/2026-04-04-reusable-processes.md` ✓
- Macro patterns: `my-knowledge-base/docs/patterns/Distilling Person-Project Macro Patterns.md` *(TO MOVE from `~/Downloads/`)*
- Routing potentials: `my-knowledge-base/docs/routing/Potentials Cataloging and Routing.md` ✓
- Persona taxonomy: `~/.claude/plans/2026-04-28-domain-persona-workstreams-taxonomy.md` ✓
- AI-session workstreams library: `hokage-chess/docs/business/workstreams/README.md` ✓

**Governance:**
- W6 is **always retrospective** — never runs ahead of W1/W2 (you can't extract patterns from work not yet done)
- W6 outputs go to `meta-organvm/praxis-perpetua/library/` when stable
- Person-name leakage = corruption: Maddie/Rob references must be abstracted before SOP promotion

**Checklist:**
- [ ] Move `~/Downloads/Distilling Person-Project Macro Patterns.md` → `my-knowledge-base/docs/patterns/`
- [ ] Strike all references to phantom `~/Downloads/Streamlining Rob-Maddie Project Artifacts.md`
- [ ] Audit existing W6 docs for personal-name leakage; abstract before promotion
- [ ] Cross-link persona taxonomy ↔ AI-session workstreams library

---

## Noise / Contamination Index

To strip from any future paste:

| Noise Class | Examples | Remediation |
|------------|----------|-------------|
| Gemini editor file-tab bleed | `settingseditor`, repeated path blocks ×10 | Don't copy from open-tab panel; use `git ls-files` or `find` |
| `.resolved` artifact persistence | `walkthrough.md.resolved`, duplicate `master_file_map.md.resolved` | After promoting an artifact, archive the brain dir |
| Glitched filenames | `⏺ I'll audit every claimed artifact on d.ini` | Filename validation hook on save |
| Empty buffers committed | `Untitled-1`, `2026-04-28-workspace-assembly-and-mapping.md` (0 bytes) | Pre-commit hook: reject 0-byte `.md` |
| Phantom paths | `~/Downloads/Streamlining Rob-Maddie Project Artifacts.md` | Verify-on-cite for any path mentioned in plans |
| Session log JSONs | `~/.gemini/tmp/4jp/chats/session-*.json` (1.4MB) | Confirm gitignored in all repos |

---

## Locations Map (Canonical)

| Artifact | Repo | Path | State |
|----------|------|------|-------|
| **Master cascading workstreams doc** | my-knowledge-base | `CASCADING_WORKSTREAMS.md` | **TO CREATE** (extend `refactored_workstreams.md` with W3–W6) |
| W1 catalog | sovereign-systems--elevate-align | `docs/intake/maddie_spiral_wishes.md` | TO PROMOTE |
| W1 audit+forms | sovereign-systems--elevate-align | `docs/audits/spiral_audit_and_forms.md` | TO PROMOTE |
| W1 plan | sovereign-systems--elevate-align | `.gemini/plans/2026-04-28-spiral-catalog-audit-and-brainstorming-forms.md` | ✓ |
| W1 code | sovereign-systems--elevate-align | `src/data/hub.config.ts` | ✓ (drift to fix) |
| W2 forms | hokage-chess | `docs/business/forms/` | ✓ |
| W2 workstreams | hokage-chess | `docs/business/workstreams/README.md` | ✓ |
| W2 personas | ~/.claude/plans | `2026-04-28-domain-persona-workstreams-taxonomy.md` | ✓ |
| W2 offline forms | ~/.claude/plans | `audit-session-audit-encompassing-parsed-orbit.md` | ✓ |
| W2 chezmoi mirror | domus-semper-palingenesis | `private_dot_claude/plans/2026-04-28-audit-reverify-and-external-forms-package.md` | ✓ |
| W3 hub | my-knowledge-base | `TOTAL_RECORD.md` | ✓ (needs U1–U5) |
| W3 plan v2 | my-knowledge-base | `.gemini/plans/2026-04-28-master-file-map-v2.md` | ✓ CURRENT |
| W3 companion plan | my-knowledge-base | `.gemini/plans/2026-04-28-total-record-consolidation.md` | ✓ |
| W3 gap audit | my-knowledge-base | `docs/audits/gap_tracker.md` | TO PROMOTE |
| W3 sources | my-knowledge-base | `config/sources.yaml` | ✓ |
| W3 pipeline | my-knowledge-base | `src/wiki-compiler.ts` | ✓ |
| W4 (recovery) | sign-signal--voice-synth | TBD | TO INVESTIGATE |
| W5 audit index | meta-organvm | `audits/2026-04-29-INDEX.md` | TO CREATE |
| W6 macro patterns | my-knowledge-base | `docs/patterns/Distilling Person-Project Macro Patterns.md` | TO MOVE from Downloads |
| W6 reusable processes | sovereign-systems--elevate-align | `docs/process-extraction/2026-04-04-reusable-processes.md` | ✓ |

---

## Verification

After execution, the refactor is complete when:

1. **`my-knowledge-base/CASCADING_WORKSTREAMS.md` exists** and contains all 6 workstreams with summaries, governance, checklists, locations.
2. **`TOTAL_RECORD.md` references CASCADING_WORKSTREAMS.md** as §0 (master index) and includes U1–U5 from gap_tracker §5.
3. **Brain GC verified:** every `.resolved` file referenced in this plan has been promoted to a repo path; brain UUIDs of consumed sessions can be moved to `~/.gemini/antigravity/brain/archive/`.
4. **W1:** `git -C sovereign-systems--elevate-align grep -l 'maddie_spiral_wishes' docs/` returns the canonical path; `hub.config.ts` emoji + Node 11 phase match catalog.
5. **W2:** `git -C hokage-chess log --oneline -5` shows Apr 28 commits (`53bcd32`, `1bb4e79`, `0a31116`, `9b6dd49`, `83483bd`); `npm test` reports 56/56.
6. **W3:** `find intake/drafts -name '*.md' | wc -l` drops by ≥35; no file >100KB in `intake/drafts/`; `wiki-compiler.ts` runs to completion.
7. **W4:** Either an artifact path exists in a real repo OR an IRF entry records the recovery attempt + outcome.
8. **W5:** `meta-organvm/audits/2026-04-29-INDEX.md` exists with ≥7 entries.
9. **W6:** `find ~/Downloads -name 'Distilling*' -mmin -10080` returns nothing (moved); `my-knowledge-base/docs/patterns/Distilling Person-Project Macro Patterns.md` exists.
10. **Plan discipline:** This file copied from `~/.claude/plans/the-following-files-are-bright-sky.md` to `~/Workspace/organvm/my-knowledge-base/.gemini/plans/2026-04-29-cascading-workstreams-refactor.md`, committed, pushed.

---

## Plan File Discipline (post-approval)

Per `~/CLAUDE.md` and `~/Workspace/CLAUDE.md`:
- After approval, copy this plan to **project-scoped, dated location**:
  - Primary: `~/Workspace/organvm/my-knowledge-base/.gemini/plans/2026-04-29-cascading-workstreams-refactor.md`
  - Cross-link from W1 and W2 plans indexes
- Never overwrite — revisions get `-v2.md`, `-v3.md`
- Commit + push (per "Plans are artifacts" rule — local-only plans are invisible to the system)

---

## Critical Files (read on execution)

- `/Users/4jp/Workspace/organvm/my-knowledge-base/TOTAL_RECORD.md` — hub to update
- `/Users/4jp/.gemini/antigravity/brain/5efe471b-36e1-4565-bd21-785466e74a77/artifacts/refactored_workstreams.md.resolved` — base for W1+W2
- `/Users/4jp/.gemini/antigravity/brain/5efe471b-36e1-4565-bd21-785466e74a77/artifacts/gap_tracker.md.resolved` — W3 actionables
- `/Users/4jp/.gemini/antigravity/brain/f0c19e07-9a3e-4209-b7d7-a6b845486c1f/artifacts/maddie_spiral_wishes.md.resolved` — W1 catalog source
- `/Users/4jp/.gemini/antigravity/brain/4feea892-69a5-4253-a6ac-af10871df164/artifacts/spiral_audit_and_forms.md.resolved` — W1 audit source
- `/Users/4jp/Workspace/organvm/my-knowledge-base/.gemini/plans/2026-04-28-master-file-map-v2.md` — W3 current plan
- `/Users/4jp/Workspace/organvm/my-knowledge-base/.gemini/plans/2026-04-28-master-file-mapping-and-assembly.md` — W3 v1 (to archive)
- `/Users/4jp/Workspace/organvm/my-knowledge-base/.gemini/plans/2026-04-28-total-record-consolidation.md` — W3 companion
- `/Users/4jp/Workspace/organvm/my-knowledge-base/config/sources.yaml` — W3 sources
- `/Users/4jp/Workspace/organvm/sovereign-systems--elevate-align/.gemini/plans/2026-04-28-spiral-catalog-audit-and-brainstorming-forms.md` — W1 plan
- `/Users/4jp/Workspace/organvm/sovereign-systems--elevate-align/docs/process-extraction/2026-04-04-reusable-processes.md` — W6 source
- `/Users/4jp/Downloads/Distilling Person-Project Macro Patterns.md` — W6 (move to repo)

## Existing functions/utilities to reuse

- **`my-knowledge-base/src/wiki-compiler.ts`** — handles atomization (don't reinvent)
- **`my-knowledge-base/npm run prepare-db`** — runs migrate + seed automatically
- **`my-knowledge-base/npm run search`** / `search:semantic` / `search:hybrid` — verify post-ingestion quality
- **`Workspace/CLAUDE.md` data integrity rules** — `save_registry()` pattern (read-before-write, refuse <50 records) — same discipline applies to `TOTAL_RECORD.md`
- **`Workspace/CLAUDE.md` Session Start Protocol** — call `conductor_session_start` before BUILD work; FRAME→SHAPE→BUILD→PROVE→DONE phase gates
- **Brain GC pattern from gap_tracker** — `~/.gemini/antigravity/brain/<UUID>/` after artifact promotion: archive don't delete (audit trail)
