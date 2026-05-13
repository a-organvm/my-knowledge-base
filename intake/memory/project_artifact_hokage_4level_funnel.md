---
name: Hokage 4-level funnel architecture (PRT-044)
description: Architecture doc importing BODI's L1-L4 funnel mechanism wholesale and re-skinning to chess + Naruto stack (Genin $9 / Chunin $29 / Jonin $99 + ambassador rev-share). Blocked on Kit API key for L2 deploy.
type: project
originSessionId: 1c644505-be6a-4821-89ab-c1f1cafa38e8
---
**What:** v1 architecture installing BODI's working funnel discipline into Hokage Chess. L1 chess-content discovery (YouTube algorithm + Twitter chess corner + r/chess + NYC park outreach) → L2 lead magnet ("Get to 1400" repertoire PDF) + Kit email capture → L3 Genin Squad ($9/mo) + within-tier Chunin Dojo ($29/mo) → L4 Jonin Mentorship ($99/mo) + ambassador rev-share Genin facilitators (30%).

**Where:** `~/Workspace/4444J99/hokage-chess/docs/business/2026-04-25-hokage-4-level-funnel-architecture.md`

**Project:** `4444J99/hokage-chess`

**For whom:** Rob Bonavoglia

**State:** shipped (commit `c404b5a` 2026-04-25); BLOCKED on Kit API key for L2 deploy

**Pending feedback:**
- Rob: repertoire content for Lead Magnet PDF (lines in his head, needs to record/type)
- Rob: pick top-5 YouTube videos for welcome content pack
- User: provision Kit API key (PRT-030, 60s action — kit.com signup → API Keys → drop into `.env.local` as `KIT_API_KEY`)
- User/Rob: CRM unification decision — Kit standalone vs Teamzy unified across BODI + Hokage

**Next action:** P0 lead magnet authoring (week 1) + user Kit setup. Once Kit key lands, P1 ships `/free-plan` route in Next.js app + Kit form integration. Earliest revenue impact: Week 4 Genin Squad launch.

**IRF:** PRT-044 (depends on PRT-030 Kit API key, PRT-038 LCC schema port, PRT-039 Character Sheet onboarding, PRT-040 Bridge Content, PRT-041 Discord rituals).

**Lineage:** mirror of `project_artifact_bodi_funnel_premium_content.md` (PRT-043); synthesized in `project_artifact_cross_pollination_master_diagnosis.md` (PRT-045). Aligns with v6 strategy (`docs/business/2026-04-25-strategy-v6-master.md`).
