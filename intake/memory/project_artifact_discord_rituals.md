---
name: Hokage Discord rituals — Welcome Wed / Loot Drop Fri / Quest Log Sun (PRT-041)
description: Three weekly recurring Discord rituals scaffolding L2 retention + L3 conversion. ~80min/week Rob commitment. Channel structure with Genin/Chunin/Jonin role gating. Tier-gated rituals (Sunday Puzzle / Tuesday Live / Bi-weekly 1:1) support paid-tier retention.
type: project
originSessionId: 1c644505-be6a-4821-89ab-c1f1cafa38e8
---
**What:** Discord ritual specification for Hokage Chess community server. Three public rituals: **Welcome Wednesday** (7pm ET, 30min, onboarding new joiners), **Loot Drop Friday** (4pm ET, 15-20min, free-resource drop paired with that week's Jutsu), **Quest Log Sunday** (8pm ET, 20-30min, public next-week-goal posting). Plus tier-gated rituals: **Sunday Group Puzzle** (Genin), **Tuesday Live Session** (Chunin), **Bi-weekly 1:1** (Jonin), **Monthly Facilitator Sync** (Ambassador). Channel structure + role bot config + Stripe→Kit→Discord webhook chain specified.

**Where:** `~/Workspace/4444J99/hokage-chess/docs/content/2026-04-25-discord-rituals.md`

**Project:** `4444J99/hokage-chess`

**For whom:** Rob Bonavoglia (host) + future Hokage community

**State:** shipped (commit `050dcc8` 2026-04-25); ready to deploy on Discord setup

**Pending feedback:**
- Rob: confirm 7pm/4pm/8pm ET ritual times match his weekly availability (~80min total)
- Discord server provisioning + channel structure setup (per §2 of doc)
- Bot tooling decision: Carl-bot vs MEE6 for welcome bot; Zapier vs n8n for Kit-Discord glue

**Next action:** provision Discord server with §2 channel structure; configure welcome bot + role bot; run Week 1 of all three rituals live; review KPIs after first 4 weeks.

**IRF:** PRT-041 (DONE on commit). Feeds PRT-044 Hokage funnel L2/L3 retention.

**Lineage:** parallel to BODI's Teamzy warmth-cadence (`project_artifact_bodi_funnel_premium_content.md`). Interlocks with `project_artifact_bridge_content_pillar.md` (PRT-040) — Tuesday Jutsu drop feeds Wed Welcome; Friday Boss Battle (monthly) intersects Loot Drop. Tier-gating depends on PRT-044 funnel L3-L4 mechanism.
