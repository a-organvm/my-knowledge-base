---
name: Layer E — Filter substrate (alchemical distillation operator)
description: Spec for the operator that distills incoming data to generative form; bidirectional (inbound = surface→generative, outbound = generative→surface re-projection); SPEC-ONLY but immediately demonstrable via statusline first-light fix.
type: project
originSessionId: f3beab49-8440-4336-b4db-299e2933f5a1
---
**What**: Three-operator pipeline that produces canonical atoms:
1. `decompose` — split incoming raw into structured fragments
2. `purify` — purge contamination (persona-coloration, movie-set abstraction, old DNA, old bacteria, redundant transcription, temporally-local, surface-decoration, unfounded-claim)
3. `distill` — compile to generative-code form (the rule that produces the surface, not the surface)

Bidirectional: inbound stores generative form; outbound `re_project()` regenerates correct surface on demand. This is what makes the statusline bug auto-catchable: if statusline atom were stored as `{label, value, color}` instead of literal `\033[...]`, render would always be correct.

Schema additions: `surface_form`, `generative_form` (with `schema_id` + `rule_spec` + `ladder_refs`), `purification_residue`. Distillation ladder: instance → pattern → rule → principle → universal (5 levels).

**Where**:
- Plan: `2026-04-27-filter-substrate-alchemical-distillation.md` (chezmoi 1e7e9d4)
- Target build: `~/Workspace/organvm/my-knowledge-base/filter/{filter.py, ladder.py, re_project.py}` + `filter/predicates/{persona_coloration,movie_set_abstraction,old_dna,old_bacteria,redundant_transcription,temporally_local,surface_decoration,unfounded_claim}.py` + `filter/schemas/*.yaml`

**Project**: `organvm/my-knowledge-base`

**For whom**: User — operationalizes `feedback_intake_alchemical_decomposition.md` rule

**State**: SPEC. Slice E1 (operator core + statusline first-light) unbuilt.

**First-light demo (separate from full build)**: statusline ANSI bug currently ships literal `\033[38;5;146m...` to terminal. Layer E version: store `{label:"ctx", value:0.55, color:"indigo"}`, render via `re_project()` that produces ANSI bytes fresh. ~5min isolated fix; full Slice E1 ~2 days.

**Pending feedback**:
- Persona-coloration policy (preserve voice-signature/intimate-affection vs strip mood-bleed/era-slang)
- Movie-set abstraction unblock (placeholder vs leave null vs auto-generate)
- Generative-form schema authority (filesystem-as-truth in `filter/schemas/` vs registry repo vs seed.yaml)
- Filter version migration (idempotent vs always re-run)

**Next action**: Slice E1 — operator core (`filter.py` 3-stage pipeline) + `surface_decoration` predicate + statusline schema YAML + statusline first-light fix.
