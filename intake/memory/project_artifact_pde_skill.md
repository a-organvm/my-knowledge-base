---
name: Product Domain Engine skill
description: Conductor skill that formalizes any domain-tied product through 5-phase protocol expressed via 4 rhetorical modes (logos, ethos, pathos, kairos); orchestrates 7 existing skills; built 2026-04-25 in a-i--skills repo (commit cf92479)
type: project
originSessionId: 5e6b1b1c-2e50-41f2-8b4a-8ee02cebdc19
---
**What:** The meta-system. A conductor skill that names the pattern recurring across 4 products (public-record-data-scrapper, styx, sovereign-systems--elevate-align, hokage-chess) and converts re-derivation into composition. Adds the rhetorical-mode framework (logos/ethos/pathos/kairos), the 5-phase formalization protocol (identify→map→encode→express→deploy), the composition matrix, the autopoietic feedback loop, and the organ-chain traversal scoring that none of the 7 orchestrated skills carry.

**Where:** `~/Workspace/a-i--skills/skills/project-management/product-domain-engine/`

**Files (all committed cf92479, pushed):**
- `SKILL.md` (306 lines) — conductor frontmatter + 5-phase protocol + 4 modes + composition matrix + invocation pattern
- `scripts/domain-audit.sh` (291 lines, +x) — bash CLI; scans repo for structural mode signals; outputs scored audit; tested against hokage-chess (logos-dominant in structure) and elevate-align (balanced)
- `references/rhetorical-modes.md` (156 lines) — full treatment of logos / ethos / pathos / kairos with internal/external function distinction
- `references/composition-matrix.md` (120 lines) — output × mode blend table with mode-pattern → output recommendations
- `references/prompt-sequence.md` (194 lines) — universal $MODE/$DEPTH/$RESEARCH_ATLAS commands ordered by tier; tier-order-by-stage selection logic; 4 worked examples (hokage / styx / public-record / elevate-align)
- `references/proof-instances.md` (187 lines) — full case data for the 4 instances; cross-instance pattern table; verification approach
- `assets/domain-template/seed.yaml` — ORGANVM contract template for new domain repos

**Project:** `a-i--skills` (a-organvm/a-i--skills on GitHub)

**For whom:** Anthony's whole agent fleet. Becomes available at `~/.claude/skills/` after next chezmoi apply (run_onchange_after_link-skills.sh hook).

**State:** Built, tested, committed, pushed. Audit script confirmed working. Skill not yet linked into runtime (pending chezmoi apply).

**Audit calibration note:** the bash script reads structure (presence of `src/`, `brand/`, `ROADMAP.md`, etc.), not voice. Hokage-chess scores logos-dominant in the script even though it's pathos-dominant in lived practice — its narrative is embedded in code/copy, not in `brand/voice.md`. Treat audit output as a coverage check, not quality assessment.

**The framework's load-bearing additions** (what the skill carries that the 7 orchestrated skills don't):
1. The four rhetorical modes as a coordinate system (logos/ethos/pathos/**kairos** — kairos was missing from earlier drafts)
2. Internal-mass vs external-function distinction (a test suite is logos-mass internally but ethos-functional externally)
3. The 5-phase formalization protocol (identify → map → encode → express → deploy)
4. Tier-order-by-stage (new / theory-heavy / deployed / client-driven each get different sequences)
5. Autopoietic loop (deployment metrics feed back into formalization; analytics modules are observation instruments)
6. Materia-collider graduation criteria (when a domain transitions from incubation to organ-residence)
7. Cross-fertilization registry (patterns proven once propagate to all)

**Pending follow-up:**
- Run audit against styx and public-record-data-scrapper to validate the cross-instance pattern table
- Eventual `references/cross-fertilization.md` — pattern registry living alongside SKILL.md, populated as patterns prove out
- Possible TS port of `domain-audit.sh` for richer scoring (semantic, not just structural)

**Plan source:** `~/.claude/plans/mutable-weaving-raccoon.md` (the 8-part PDE plan with gap-fills) — written 2026-04-25 same-day as the build
