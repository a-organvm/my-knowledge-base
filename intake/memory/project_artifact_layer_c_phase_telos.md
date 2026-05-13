---
name: Layer C — Phase coherence + Telos
description: Spec for 4-quadrant phase model + telos abstraction + cross-domain scanner; emergent state from (abstract_exists × concrete_exists × coherence); SPEC-ONLY.
type: project
originSessionId: f3beab49-8440-4336-b4db-299e2933f5a1
---
**What**: Each atom carries a `phase` block computed from three predicates and one scalar:
- `abstract_exists` — atom is/has parent prompt-atom
- `concrete_exists` — referenced artifacts exist on disk/git
- `coherence` — semantic similarity of prompt vs artifact text
- `state` — derived: in_phase / out_of_phase / just_a_dream / non_existent

Plus `telos` block (ideal_form_ref + distance_from_ideal + yearning_vector + convergence_rank) and `siblings` block (cross-organ scanner output across the 600 cross-organ links).

The 4-quadrant model maps `(abstract_exists, concrete_exists)` × coherence threshold (default 0.7); states emerge from the substrate, not stipulated by hand. Connective tissue rendered as line viz: abstract pole → concrete pole, length = distance_from_ideal.

**Where**:
- Plan: `2026-04-27-phase-coherence-telos-substrate.md` (chezmoi 1e7e9d4)
- Target: extends Layer B's `classify.py` with Pass 1 (phase), Pass 2 (telos), Pass 3 (siblings). New file: `~/Workspace/organvm/.../data/atoms/scope-graph.yaml` (bootstrapped from seed.yaml across organs).

**Project**: `organvm-corpvs-testamentvm` + `meta-organvm`

**For whom**: User — answers "how far is each thing from its perfect form?"

**State**: SPEC. Slice 1 (term-overlap coherence, no embeddings) unbuilt.

**Pending feedback**:
- Coherence threshold per-scope vs global (default 0.7 globally)
- Yearning vector: rule-driven only (default) vs LLM-augmented later
- Phase computation on AI responses (not just prompts)
- Macro phase as automatic vs opt-in lens

**Next action**: Slice C1 — Pass 1 (term-overlap coherence). Slice C3 (semantic coherence) waits for Slice A2 (embeddings) to land.
