---
name: Layer A — Density (time projection)
description: Spec for prompts-as-measurements density substrate; D(t,F) signal over prompt-atoms, tunable via 4-component weight vector + JSON filter DSL; SPEC-ONLY, slice 1 unbuilt.
type: project
originSessionId: f3beab49-8440-4336-b4db-299e2933f5a1
---
**What**: Density signal `D(t, F; α,β,γ,δ, q) = α·z(D_term) + β·z(D_pred) + γ·z(D_time) + δ·z(D_sem)` over `prompt-atoms.jsonl`, with additive 4-field `measurement` block on each atom. Filter DSL is JSON over existing fields. Slice 1 ships in a day without embeddings; Slice 2 adds semantic axis via mesh `LocalEmbedder` + sidecar `.npy` vectors.

**Where**:
- Plan canonical: `~/Workspace/4444J99/domus-semper-palingenesis/private_dot_claude/plans/2026-04-27-prompts-as-measurements-density-substrate.md` (committed at chezmoi 1e7e9d4)
- Live mirror: `~/.claude/plans/2026-04-27-prompts-as-measurements-density-substrate.md` + sculpture `i-don-t-know-how-lucky-biscuit.md`
- Target build: `~/Workspace/organvm/my-knowledge-base/scripts/density.py` (NEW), `scripts/backfill_measurement.py` (NEW), `config/density-tuning.yaml` (NEW), `scripts/embed_prompt_atoms.py` (Slice 2)
- Substrate read targets: `~/Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl` (11,547 records), `…/data/corpus/april-2026/verdicts.jsonl` (2,583 verdicts, committed at corpvs b431063)

**Project**: `organvm/my-knowledge-base` (target) + `organvm-corpvs-testamentvm` (substrate)

**For whom**: User (Anthony) — for own substrate operating

**State**: SPEC — approved via ExitPlanMode 2026-04-27. Slice 1 unbuilt. No code shipped.

**Pending feedback**: Three open questions in plan §Open Questions:
- Q1: Canonical store scope (measure prompt-atoms.jsonl as-is vs refresh first vs side-by-side)
- Q2: Embedder choice for Slice 2 (LocalEmbedder default, OpenAIEmbedder optional)
- Q3: Output format (JSON-only vs JSON + CLI text summary)

**Next action**: Slice 1 — write `density.py` (~150 lines, imports `trajectory_engine.py` for n-grams) + `backfill_measurement.py` (~80 lines, streaming rewrite). Day-1 deliverable: real JSON report from 11,547-prompt corpus.
