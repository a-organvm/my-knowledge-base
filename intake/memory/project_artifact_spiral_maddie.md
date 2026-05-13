---
name: Spiral renderer + substrate stack - Maddie's Elevate Align site
description: Current spiral state in sovereign-systems--elevate-align: V5.10 materia physics still underpins the renderer, but the late-2026-04-25 V6/A14 chain added shared IconWorld data, EnvVar substrate, NAMING_CHAINS, /lineage/[envvar], and world-driven cohesion vs chaos physics
type: project
originSessionId: 5d02da2f-6b50-4f5e-a178-873b06208e5e
---
**What:** Three.js helix renderer plus the data substrate beneath it. `?variant=symbols` and `?variant=stars` now share the same 13 node worlds, but diverge in physics regime: symbols cohere, stars repel/burst. Each node also carries an immutable `envVar` used by `NAMING_CHAINS` and `/lineage/[envvar]`.

**Where:**
- Renderer: `~/Workspace/organvm/sovereign-systems--elevate-align/src/components/spiral/spiral.ts`
- World data: `~/Workspace/organvm/sovereign-systems--elevate-align/src/data/icon-worlds.ts`
- Node substrate: `~/Workspace/organvm/sovereign-systems--elevate-align/src/data/hub.config.ts`
- Multi-lens lineage: `~/Workspace/organvm/sovereign-systems--elevate-align/src/data/naming-chains.ts`
- Lineage route: `~/Workspace/organvm/sovereign-systems--elevate-align/src/pages/lineage/[envvar].astro`
- Node-page lineage link: `~/Workspace/organvm/sovereign-systems--elevate-align/src/pages/nodes/[id].astro`
- Plan: `~/Workspace/organvm/sovereign-systems--elevate-align/.claude/plans/2026-04-25-complete-spiral-maddie-icon-worlds-envvar-lineage.md`
- Physics design note: `~/.claude/plans/jolly-fluttering-hare.md`

**Project:** `sovereign-systems--elevate-align` (ORGAN-III, organvm-iii-ergon)

**For whom:** Maddie (client) and Anthony (operator / reviewer)

**State:** **V6 / A14 substrate + physics chain shipped to `main` late 2026-04-25 America/New_York.**
- V5 -> V5.10 remains the base visual system: materia-particle renderer, bouncing substrate, labels, and variant plumbing (`d8b34b6` -> `e12b742`).
- `447ab84` - shared `IconWorld` table and share-tunnel host prep.
- `fe96652` - immutable `EnvVar` substrate bound to all 13 nodes.
- `19e67bc` - `NAMING_CHAINS` committed for all 13 substrates.
- `d900c83` - `/lineage/[envvar]` route + node-page lineage link shipped.
- `90bc2b4` - live particle physics now reads `icon-worlds.ts`; symbols/stars divergence is meaningful again.
- All 5 commits above are pushed to `organvm-iii-ergon/sovereign-systems--elevate-align#main`.
- No IRF DONE atom yet exists for this V6/A14 chain.

**User-facing behavior now:**
- `?variant=symbols` = cohesion regime. Particles cluster around sampled neighbors and phase centroids, then layer world-specific behavior (`lattice`, `tidal`, `spiraling`, `rising`, `dual-gyre`, etc.).
- `?variant=stars` = chaos regime. Particles repel, burst, and respawn when they escape the vessel; same node identity, opposite force law.
- Particle palettes, thermal motion, gravity, size bias, and phase mix now route through `src/data/icon-worlds.ts`.
- Every node detail page exposes its immutable substrate and links to `/lineage/<envvar>`.
- `/lineage/[envvar]` statically renders a cross-tradition lineage surface for each of the 13 substrates.

**Verification (2026-04-25 America/New_York):**
- `npm run build` clean after commit `90bc2b4`.
- Rendered checks captured locally:
  - `output/playwright/spiral-symbols.png`
  - `output/playwright/spiral-stars.png`
  - `output/playwright/lineage-pyr.png`
  - `output/playwright/node-1.png`
- Public share tunnel verified:
  - `https://symbolistical-amiya-mitigable.ngrok-free.dev/` -> `200`
  - `https://symbolistical-amiya-mitigable.ngrok-free.dev/lineage/pyr/` -> `200`

**Deployment caveat:**
- GitHub `main` is current.
- Cloudflare Pages auto-deploy is still blocked by GH#52, so `https://sovereign-systems-spiral.pages.dev/` may lag the pushed V6 chain until a manual wrangler deploy or CI repair happens.
- The ngrok share link above is the verified current review surface for Maddie.

**Pending feedback / open threads:**
- Maddie still needs to react to the V6/A14 state, especially whether the current symbols-vs-stars divergence is the right "same God, opposite physics" balance.
- GH#52 still blocks automatic Pages deploys.
- No spiral-hover lineage CTA yet; lineage is currently reached from node detail pages and direct `/lineage/*` routes.
- A future whole-spiral multi-lens viewer can reuse `NAMING_CHAINS` / `viewThroughLens()` without schema change.

**Companion artifact:** `project_artifact_naming_chains.md` tracks the data substrate itself. This file tracks the renderer + end-user surface.
