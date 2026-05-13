---
name: Naming-chains substrate - 13 envVars x 7 lenses
description: Shared lineage data for the Maddie spiral; immutable EnvVar layer, 91 SurfaceBinding records, /lineage/[envvar] consumer, and future multi-lens viewer API
type: project
originSessionId: 5d02da2f-6b50-4f5e-a178-873b06208e5e
---
**What:** Immutable substrate beneath the spiral's mutable copy. Each node gets an `envVar` true name, then `NAMING_CHAINS` maps that substrate across Egyptian, Sanskrit/Vedic, Greek-classical, Christian-mystical, Jungian, physics-elemental, and modern-wellness lenses.

**Where:**
- `~/Workspace/organvm/sovereign-systems--elevate-align/src/data/hub.config.ts` - `EnvVar` union + `envVar` on every `SpiralNode`
- `~/Workspace/organvm/sovereign-systems--elevate-align/src/data/naming-chains.ts` - `Lens`, `SurfaceBinding`, `NAMING_CHAINS`, `chainsFor`, `viewThroughLens`
- `~/Workspace/organvm/sovereign-systems--elevate-align/src/pages/lineage/[envvar].astro` - current consumer surface
- `~/Workspace/organvm/sovereign-systems--elevate-align/src/pages/nodes/[id].astro` - node-page link to lineage
- Plan: `~/Workspace/organvm/sovereign-systems--elevate-align/.claude/plans/2026-04-25-complete-spiral-maddie-icon-worlds-envvar-lineage.md`

**Project:** `sovereign-systems--elevate-align`

**State:** shipped to `organvm-iii-ergon/sovereign-systems--elevate-align#main` late 2026-04-25 America/New_York.
- `fe96652` - `EnvVar` substrate bound to all 13 nodes
- `19e67bc` - `NAMING_CHAINS` table committed
- `d900c83` - `/lineage/[envvar]` consumer + node-page lineage link
- Build verified locally on 2026-04-25
- Public ngrok route `https://symbolistical-amiya-mitigable.ngrok-free.dev/lineage/pyr/` verified `200`
- Not yet IRF-atomized

**Coverage:**
- 13 envVars: `PYR`, `OCULUS`, `DYAD`, `PYRAMIS`, `HYDOR`, `MANDORLA`, `KENOSIS`, `SHATKONA`, `PADMA`, `BODHI`, `TETRAD`, `OKTAEDRON`, `ANKH`
- 7 lenses: Egyptian, Sanskrit/Vedic, Greek-classical, Christian-mystical, Jungian, physics-elemental, modern-wellness
- 91 `SurfaceBinding` entries currently on disk (13 x 7)

**Helper API:**
- `chainsFor(envVar)` -> chronology for one substrate
- `viewThroughLens(lens)` -> the full spiral named through one tradition

**Why it matters:** This decouples Maddie's present-day wellness copy from the deeper symbolic identity of the node. Surface names can change; the substrate does not. The same file also seeds a future whole-spiral lens toggle without changing schema.

**Open threads:**
- No whole-spiral multi-lens viewer surface yet; only per-substrate lineage pages exist.
- Source attributions are indicative and can be expanded.
- If the spiral hover itself needs direct lineage access, add a hover CTA in the renderer or island wrapper rather than duplicating the data model.
