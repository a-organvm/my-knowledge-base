---
name: Landing-engine (Persona × Narrative × Section) — slices 1+3 SHIPPED
description: Unified landing-engine primitive shared between spiral (Maddie) and hokage (Rob); slice 1 + slice 3 shipped 2026-04-25; slice 2 (Keystatic) deferred
type: project
originSessionId: 5a485c0a-8c2d-4af3-a88c-63d09aca2467
---
**What:** A `src/lib/landing-engine/` primitive — Persona × Narrative × Section composition that generates audience-targeted landing pages from declarative data. Same schema, two framework adapters (Astro for spiral, React/Next for hokage). Adding a persona to either repo's `personas.ts` spawns a new `/for/<id>` page automatically.

**Plan source:** `~/Workspace/organvm/sovereign-systems--elevate-align/.claude/plans/2026-04-25-landing-engine-persona-narrative-section-v1.md` (commit 11533e7)

**Project:** spiral repo (slices 1–2) + hokage-chess (slice 3)

**For whom:** Maddie (spiral), Rob (hokage); architectural instantiation of the Product Domain Engine skill (DONE-446).

**State:**
- Slice 1 (spiral, hardcoded) — **SHIPPED** commit `3d8cabd` (organvm-iii-ergon/sovereign-systems--elevate-align#main 2026-04-25)
- Slice 2 (spiral, Keystatic-driven) — deferred
- Slice 3 (hokage port) — **SHIPPED** commit `a2ef26f` (4444J99/hokage-chess#main 2026-04-25)

**Spiral live pages** (build-verified, 3 prerendered):
- `/for/toxic-environment-seeker` — water pillar
- `/for/burnt-out-high-achiever` — inner pillar
- `/for/cycle-syncing-practitioner` — identity pillar

**Hokage live pages** (Next.js SSG via generateStaticParams, 3 prerendered with per-persona OG metadata):
- `/for/stuck-beginner` — 1000-1400 ELO, tactics
- `/for/climbing-intermediate` — 1400-1800 ELO, strategy
- `/for/returning-adult-improver` — variable ELO, tilt-resistance

**Schema layers (identical in both repos):**
- `personas.ts` — typed Persona records with id/label/pain/desire/heroHook/ctaCommit + domain-specific PillarId
- `sections.ts` — 4 typed section props + builders that derive props from a Persona
- `narratives.ts` — ordered SectionBuilderKey sequences (ki-sho-ten-ketsu only for slice 1)
- `compose.ts` — pure `(personaId) → ComposedLanding` function

**Renderers (framework-specific):**
- Spiral: `src/components/landing/{Hero,Problem,ThreePaths,Cta}Section.astro` + dynamic route `src/pages/for/[persona].astro`
- Hokage: `src/components/landing/{Hero,Problem,ThreePaths,Cta}Section.tsx` (RSC) + Next App Router `src/app/for/[persona]/page.tsx` with `generateStaticParams` + per-persona `generateMetadata`

**Open follow-ups:**
- Slice 2 (spiral Keystatic CMS port for personas) — when Maddie wants non-developer persona authoring
- Hokage adjacency map for ThreePaths is currently 2-deep adjacency from primary pillar; could be tuned per-persona
- Multi-variant showcase pattern (per `feedback_multi_variant_showcase.md`) — add `/showcase` page in each repo that grids all 3+ personas side-by-side for client review
- Add more narratives (problem-agitate-solve, before-after-bridge, hero-journey) once a second template is genuinely needed

**Why:** Both products needed persona variants for ad funnels / multi-pillar surface. Building the primitive once vs. twice saved ~4-6h AND keeps both products on the same composition law. The shared schema means design decisions (adding a section type, refining a narrative template) propagate by replay, not by reimplementation. Framework adapter cost was the only fork.
