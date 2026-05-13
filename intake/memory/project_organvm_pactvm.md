---
name: ORGANVM system state
description: Current state of the eight-organ creative-institutional system — 10 organs, 145 repos, omega 9/20, ~896 IRF items, launched 2026-02-11
type: project
originSessionId: 80581eb0-933d-4de3-a31f-f0c420955109
---
Eight-organ creative-institutional system with PERSONAL + META umbrella. Planning corpus at `~/Workspace/meta-organvm/organvm-corpvs-testamentvm/`.

**Why:** Central portfolio architecture. Single-operator system running at institutional scale.

**How to apply:** When working on any organvm repo, check the IRF for P0/P1 items in the relevant domain. Use `organvm` CLI for registry, governance, omega queries.

---

## Current State (as of 2026-04-21)

- **Omega:** 9/20 MET, 0 IN PROGRESS, 11 NOT MET
- **Registry:** 145 repos across 10 organ sections (ORGAN-I through VII, ORGAN-PSG, PERSONAL, META-ORGANVM)
- **Testament chain:** 5953+ events, verified from genesis to seq 5952
- **Memory parity:** 460/460 files chezmoi-tracked
- **IRF:** ~900+ items. New: IRF-SEC-005 through IRF-SEC-009, IRF-ATN-010, IRF-OSS-054 through IRF-OSS-057, IRF-INST-029, IRF-DOM-045, IRF-SYS-125. DONE counter at ~405 (4th collision incident corrected, DONE-392..395 voided).
- **DONE-ID:** Counter needs pre-commit hook enforcement — 4 collision incidents to date
- **Conductor MCP:** live (mcp 1.27.0)
- **Voice-scorer MCP:** connected

## Organ Counts (2026-04-14)

I=26, II=32, III=32, IV=22, V=6, VI=6, VII=6, PSG=0, PERSONAL=2, META=13

## Key Paths

- Registry: `meta-organvm/organvm-corpvs-testamentvm/registry-v2.json`
- IRF: `meta-organvm/organvm-corpvs-testamentvm/INST-INDEX-RERUM-FACIENDARUM.md`
- Evidence map: `meta-organvm/organvm-corpvs-testamentvm/docs/evaluation/omega-evidence-map.md`
- Engine: `meta-organvm/organvm-engine/` (23 domain modules, unified `organvm` CLI)
- Concordance: `meta-organvm/organvm-corpvs-testamentvm/docs/operations/concordance.md`
- Testament chain: `~/.organvm/testament/chain.jsonl`

## Build Timeline (abbreviated)

| Date | Milestone |
|------|-----------|
| 2026-02-11 | SYSTEM LAUNCHED — 9/9 criteria, all 8 organs OPERATIONAL |
| 2026-02-28 | Omega 4/17 — 12 products deployed, LobeHub organic link |
| 2026-03-18 | Omega 7/17 — soak test passed (32/30 days, 0 incidents) |
| 2026-04-13 | Domus registered — PERSONAL section created, 5 vacuums closed |
| 2026-04-14 | Reconciliation Sprint — omega 9/20, registry 145, 13 IRF items closed |
| 2026-04-15 | Inbox review (Apr 9-15), session archival system built, networking outreach signals (APP-081–086) |

## Known Gotchas

- `status` is a read-only variable in zsh — never use in shell scripts
- ORGAN-I billing lock inflates CI failure counts (soak test noise)
- GitHub MCP content filter blocks security terms — use local reads
- `modify_dot_claude.json.tmpl` uses chezmoi modify mode — merges, doesn't overwrite
- ORGAN-III private repos: rulesets API returns 403 on free plan (false positive)
- Scorecard has 20 criteria (was 17, then 19, now 20 — #20 is sigma-E formal validation)
