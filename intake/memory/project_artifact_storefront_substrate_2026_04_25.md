---
name: project_artifact_storefront_substrate_2026_04_25
description: Personalized Client Storefront Substrate v1 (slice 1 scaffolded); skill + schema + Rob lexicon + hokage-chess opt-in + canonical frontmatter on bridge-content-pillar; 4 trinity agents returned (repo verification + corpus persona-extract spec + application-pipeline slice + 3-phase upstream refactor); slice 1 deploy step DEFERRED (Next.js AGENTS.md warning)
type: project
originSessionId: a3aadd8d-8100-4616-b6c8-5f16f92d1b2d
---
# Personalized Client Storefront Substrate (slice 1 scaffolded 2026-04-25)

## What it is
Substrate that translates internal markdown artifacts (pitch decks, business plans, research, schemas) into per-persona client-facing storefront surfaces in the client's domain language with ELI5/TLDR layers. Sits ABOVE Product Domain Engine (invokes PDE Phase 4) and 8-Strata Domain-Ideal-Whole (uses internal-magnet stratum + gap-map). Calls voice-enforcement against per-persona voice_constitution.

## Files shipped (4 git commits, all pushed 2026-04-25)
- `~/Workspace/a-i--skills/skills/project-management/personalized-storefront-render/SKILL.md` — conductor protocol (commit b203d86)
- `~/Workspace/organvm/schema-definitions/schemas/storefront-v1.schema.json` — frontmatter contract (commit 5e36754)
- `~/Workspace/organvm/schema-definitions/examples/storefront-frontmatter-rob.yaml` — canonical example
- `~/Workspace/4444J99/hokage-chess/storefront.config.yaml` — first per-repo opt-in (commit 5e5d5fb)
- `~/Workspace/4444J99/hokage-chess/docs/content/2026-04-25-bridge-content-pillar.md` — first tagged source artifact
- `~/Documents/personas/rob-bonavoglia.lexicon.yaml` — first persona lexicon (NOT git-tracked — vacuum)
- `~/.claude/plans/2026-04-25-personalized-client-storefront-substrate.md` — plan (commit ff4d9ed in dotfiles)
- `~/.claude/plans/2026-04-25-storefront-session-research-prima-materia-and-all-roads.md` — research artifact for next session

## Status
- **Slice 1 substrate scaffold**: DONE
- **Slice 1 deploy** (Next.js `/storefront/[...slug]` route): DEFERRED — hokage-chess AGENTS.md warns "Next.js APIs differ from training data; read node_modules/next/dist/docs/ first"
- **Slice 2 (Maddie/Spiral)**: PENDING
- **Slice 3 (full substrate: auto-draft, IRF wiring, mailto backfeed)**: PENDING

## 4 trinity agents returned 2026-04-25 (parallel dispatch)
1. **Repo verification** (Explore): 4 of 8 P1 CONFIRMED (linguistic-atomization-framework, conversation-corpus-engine, vox--architectura-gubernatio, application-pipeline); 1 PARTIAL (narratological-algorithmic-lenses); 4 LOCAL-MISSING (mirror-mirror, specvla-ergon--avditor-mvndi, a-i-council--coliseum, gamified-coach-interface). 5 of 11 P2 confirmed.
2. **`cce corpus persona-extract` spec** (Plan): implementation-ready, ~1,560 LOC, stdlib-only, 3 verification gates. Self-applicable extension: Claude session JSONLs at `~/.claude/projects/-Users-4jp/` → `claude.lexicon.yaml`. Spec at end of agent return; not yet written to plans dir.
3. **Application-pipeline slice** (Plan): 5 recruiter-class personas (faang-eng/ai-startup/design-agency/consultancy/grant-panel); schema extensions (`forbidden_for_class_only`, `position_translation`, `lexicon.substitutions[]`); position-to-persona overlay enables near-zero-touch ingestion. 5 hand-curated translations as DoD.
4. **Upstream refactor** (Plan): 3 phases (R1 register taxonomy → NAL+VAG split, R2 lexicon authoring → LAF, R3 voice constitution → VAG rule-pack registry). Each reversible. Gated on slice 3 shipping or 2+ new clients exercising substrate. Migration data: 1 file today (Rob's lexicon).

## Critical conflict surfaced by parallel agents
VAG already has `constitution/REGISTER_TRANSFORMATION_MATRIX.yaml`. Register taxonomy is partially squatted there. Resolution: NAL owns enum + semantic guidance ("what each register IS"); VAG owns transformation matrix ("how to move between them"). Different abstraction tiers.

## Open vacuums (radiation per Rule #47)
1. **Personas not git-tracked** (~/Documents/personas/ has no .git) — Rob's lexicon could be lost on disk failure. Options: chezmoi `private_Documents/`, own repo, dotfiles sync. PENDING DECISION.
2. **Slice 1 deploy** — Next.js route wire deferred to next session.
3. **Resolver-audit not run** — SessionStart hook flagged 20 hardcoded paths; my new files likely add more.
4. **Voice-scorer not run** — ~600 lines of prose unaudited.
5. **Conductor MCP not invoked** — workspace SOP for session_start unused.
6. **4 of 8 "walk first" repos LOCAL-MISSING** — clone or accept gap.
7. **Domain ownership unverified** — hokagechess.com / spiralhealing.com fallback to 4jp.io/{persona}/.

## Pending feedback
- User signoff on substrate v1 architecture (implicit via ExitPlanMode approval)
- User decision on personas-tracking solution
- User decision on which trinity agent's spec to implement first (Maddie worker recommends Move 3 / corpus persona-extract as keystone)

## Next session priorities
1. Implement `cce corpus persona-extract` per the spec (or hand to parallel session in that lane)
2. Slice 1 deploy step (read Next.js docs, wire /storefront route)
3. Persona-tracking decision + execution
4. Walk the 4 LOCAL-MISSING P1 repos if they're cloneable
5. Slice 2 scaffold (Maddie/Spiral lexicon + Astro adapter)

## Last interaction: 2026-04-25
