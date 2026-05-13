---
name: Hokage Chess v6 strategy refresh
description: Strategy v6 master + pitch deck v3 + business plan v2 — lineage-integrated refresh after Apex Predator parent architecture discovery
type: project
originSessionId: 7d677466-0034-49db-982b-a1cd2afe115c
---
**What:** Refreshed Hokage Chess document family integrating Apex Predator parent architecture (Dec 2025, 13 source files) + Legion Command Center sister codebase (`a-organvm/gamified-coach-interface`) discovery. Three documents:

- **Strategy v6 master** (833 lines) — supersedes v5 + apex-predator-lineage-appendix
- **Pitch deck v3** (470 lines, 16 slides) — adds Slide 5 "Architectural Lineage" + de-loaded risks
- **Business plan v2** (909 lines) — adds § 2.7 Architectural Lineage credibility section + § 5.6/5.7/5.8 (Character Sheet + Chess XP + Bridge Content) + Appendix E/F (parent inventory + sister codebase)

**Where:**
- `~/Workspace/4444J99/hokage-chess/docs/business/2026-04-25-strategy-v6-master.md`
- `~/Workspace/4444J99/hokage-chess/docs/business/2026-04-25-pitch-deck-v3.md`
- `~/Workspace/4444J99/hokage-chess/docs/business/2026-04-25-business-plan-v2.md`

**Project:** `4444J99/hokage-chess` (private)

**For whom:** Rob Bonavoglia (founder, @HokageChess) — pitch deck for sponsors/partners/creator-economy capital · business plan for SBA/lender-grade reference · strategy v6 as internal master

**State:** draft / committed-and-staged

**Key changes from v5/v2/v1:**
- Architecture is no longer "speculative" — Hokage Chess is the **second instantiation** of an Apex Predator parent pattern
- 4 risks de-loaded: architecture validation, pricing tiers, phase timeline, architect capacity
- New product layer: Character Sheet onboarding (6 chess stats + Main Quest/Side Quests/Debuffs), Chess XP system (rated game/puzzle/Boss Battle XP grants → level rewards), Discord rituals (Welcome Wed / Loot Drop Fri / Quest Log Sun), Bridge Content pillar (gaming/anime → chess crossover hooks)
- Phase 2 engine inheritance: port `xp-ledger.ts` + `quests.ts` + `achievements.ts` from Legion Command Center
- Vacuum register expanded V15-V18 (LCC port pending, Character Sheet build pending, Bridge Content not started, Discord rituals not codified)

**Pending feedback:** None yet — Rob has not seen v6/v3/v2 versions. Previous v5/v2 pitch + v1 business plan committed in `961d05a`.

**Next action:**
1. Decide whether to push v6 + v3 + v2 to `4444J99/hokage-chess` private remote
2. Share pitch deck v3 + business plan v2 with Rob (next call)
3. Address V15-V18 vacuums in execution sequence:
   - V15 (LCC port) — Phase 2 trigger
   - V16 (Character Sheet) — Phase 1 (Week 1-2 build)
   - V17 (Bridge Content) — Phase 1 (Week 3-4 first video)
   - V18 (Discord rituals) — Phase 1 (Week 1-2 codify in bot)
