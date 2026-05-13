# Rob-Gemini Warm-Clock: Phase A Implementation Plan

This plan details the execution of Phase A of the `rob-gemini-warm-clock` spec, picking up from the hanging actions identified in the Claude session export.

## Proposed Changes

We will execute the three HIGH priority hanging actions.

### 1. Mirror Volatile Downloads
The following unmirrored volatile assets will be copied into `docs/superpowers/intakes/` to ensure they are git-backed:
- `~/Downloads/project daisy apple music selection rob sheridan - Google Search (3_27_2026 9:10:04 AM).html`
- `~/Desktop/hokage-chess--youtube-thumbnails-review.pdf`
- `~/Downloads/drive-download-20260425T174235Z-3-001/the-legion-of-fitness_-battle-plan-interrogation.docx`
- `~/Downloads/drive-download-20260425T174235Z-3-001/blueprint-for-a-niche-fitness-coaching-enterprise_-a-deep-dive-into-the-gamified-life-model.docx`
- `~/Downloads/drive-download-20260425T174235Z-3-001/the-legion-of-fitness_-battle-plan-interrogation-(1).docx`
- `~/Downloads/drive-download-20260425T174235Z-3-001/strategic-framework-for-a-niche-fitness-coaching-enterprise.docx`

### 2. Execute `drift` Pass
I will generate `docs/business/2026-04-27-rob-drift-ledger.md`. This will identify contradictions between the maintained documentation (the audit, persona file, and `seed.yaml`) and the true repository `HEAD`.
- **Numerical drift:** Verifying commit count, file counts, and page counts.
- **State drift:** Validating "formalized" vs. "in-principle" agreements across docs.
- **Claim drift:** Identifying unfulfilled `produces` edges in `seed.yaml`.

### 3. Execute `redteam` Pass
I will generate `docs/business/2026-04-27-rob-redteam.md` using only raw intake artifacts (transcripts, mirrored PDFs/DOCXs) and deliberately ignoring all existing synthesis/summary documents.
- The output will include a contradiction/drift ledger, identify "what everyone is overconfident about", propose a revised ontology, and surface at least one structural recommendation that materially changes the project direction rather than just the wording.

## User Review Required

> [!IMPORTANT]
> The `drift` and `redteam` passes will be executed by me (Gemini). The outputs will be placed in `docs/business/` and then diffed. Please confirm if you would like me to automatically execute the Codex reconciliation pass (i.e. commit and push the generated files) at the end, or pause for your review of the Markdown files before committing.

## Verification Plan

### Automated Tests
- I will run `git rev-list --count HEAD` and compare against the numbers in the existing evidence audit.

### Manual Verification
- You can review the newly generated `2026-04-27-rob-drift-ledger.md` and `2026-04-27-rob-redteam.md` to ensure they provide orthogonal value (different findings/framings) and do not just restate existing synthesis.
