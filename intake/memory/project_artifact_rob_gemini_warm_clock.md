---
name: Rob × Gemini Warm Clock plan
description: Spec for cache-aware, mode-disciplined Gemini integration on the Rob (Hokage Chess + BODI) lane; Phase A manual, B semi-auto, C scheduled
type: project
originSessionId: 81498485-45e0-487a-8140-0c4e281fd377
---
**What:** Plan spec for a three-cadence Gemini integration on the Rob lane. Forces orthogonal modes (`drift`, `redteam`, `latent-map`, `failure-sim`); forbids `synthesis` (already covered by Codex audit). Codex validates every Gemini output against repo HEAD before it counts as shipped.

**Where:**
- Spec: `~/.claude/plans/archive/rob-gemini-warm-clock.md` (full plan, 10 sections, ~290 lines)
- Stub redirect: `~/.claude/plans/2026-04-27-rob-gemini.md`
- Full session export + 204-item inventory: `~/.claude/plans/2026-04-27-rob-gemini-warm-clock-full-session-export.md`

**Project:** Dotfiles `~/.claude/plans/` — but the *target* is `4444J99/hokage-chess` (where Phase A drift + redteam outputs land under `docs/business/`).

**For whom:** Rob Bonavoglia (Hokage Chess client; BODI fitness MLM as parallel venture).

**State:** spec approved 2026-04-27; Phase A (manual `gemini` runs) NOT yet executed. No artifacts produced yet beyond the plan itself.

**Why this exists:** Cross-agent reconciliation on 2026-04-27 (Gemini, Codex, Claude) showed Gemini retrieves fast but smooths source material into rhetoric, propagates stale numbers (28 vs 29 pages, 161 vs 202 commits), and cite-hallucinates files that don't exist locally. The warm clock divides labor: Gemini = orthogonal pressure (red-team / drift / latent-link); Codex = reconciliation; Claude = composition.

**Cache logic:** 5-minute prompt-cache TTL is the binding constraint. Active sessions tick at 270s via `ScheduleWakeup`; idle drops to 1800s; daily cron eats one cold-start per day.

**Hard rules:**
- No LaunchAgents (Universal Rule + `feedback_no_launchagents.md`). Cron runs via GitHub Actions or remote Claude trigger only.
- No bypass of reconciliation — unvalidated Gemini outputs are drafts, not shipped artifacts.
- No re-running synthesis modes — link to `docs/business/2026-04-27-rob-evidence-of-existence-system-audit.md` (commit `e43e972`) instead.

**Critical input files (Gemini must read before producing):**
- `~/Documents/personas/rob-bonavoglia.md` + `.lexicon.yaml`
- `~/Workspace/4444J99/hokage-chess/docs/business/2026-04-27-rob-evidence-of-existence-system-audit.md`
- `~/Workspace/4444J99/hokage-chess/.codex/plans/2026-04-25-bodi-gap-closure-full-implementation-plan.md`
- `~/Workspace/4444J99/hokage-chess/seed.yaml`
- `~/.claude/plans/2026-04-25-relay-rob-hokage-fitness.md`

**Drive-side artifacts** (latent-map mode only): `Fitness_Business_Rob` folder + 4 child docs in My Drive; 5 adjacent Rob docs in My Drive root (Codex Drive scan output, 2026-04-27).

**Pending feedback:** none yet — user hasn't reviewed Phase A outputs because Phase A hasn't run.

**Next action:** Phase A manual run. User invokes `gemini` CLI with `mode: drift` against the file list in §4 of the plan. Output to `hokage-chess/docs/business/2026-04-27-rob-drift-ledger.md`. Codex validates. Then repeat for `mode: redteam`. Compare both against the existing audit; outputs that duplicate the audit's findings indicate mode failure (re-prompt with stricter forbidden-input list).

**Open questions (parked, see §9 of plan):**
- Q1: cron substrate — GitHub Actions vs remote Claude trigger (lean GH Actions).
- Q2: BODI included alongside Hokage in mode prompts (yes — one founder, two ventures).
- Q3: parallel `maddie-gemini-warm-clock.md` — defer until Phase A proves value here.
- Q4: log active-warm ticks to `~/.claude/state/`? — defer.

**204-item inventory:** Exported 2026-04-27. Covers 15 categories (persona, repo, plans, memory, domus mirrors, archive, knowledge-base, application-pipeline, downloads, iCloud, Gemini session paths, Drive IDs, git commits, IRF IDs, domains/legal, Rob's homework). 6 volatile Downloads items (#140-145) need mirroring. Full list in the session export file.

**Sister artifact:** Maddie evidence audit shipped same day as commit `8f68b2d` in `organvm/sovereign-systems--elevate-align`. The Maddie warm-clock spec is deferred but follows the same shape.
