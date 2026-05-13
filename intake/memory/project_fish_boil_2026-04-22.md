---
name: Fish boil atoms 2026-04-22
description: 4 new atoms from user input — Karpathy wiki architecture, 8! permutations, USPIS report, markdown linting standards
type: project
originSessionId: 98e6abc9-e524-43f7-90b0-0b9a84a4b6d7
---
## Atoms captured 2026-04-22

### ATOM-FB-001: KARPATHY-WIKI-ARCHITECTURE
**Domain:** Architecture / Knowledge
**Content:** Andrej Karpathy's LLM wiki architecture bypasses RAG by shifting complexity from query-time to compile-time. LLM acts as a compiler: raw documents → structured Markdown wiki with index.md navigation, encyclopedia articles, backlinks. Self-healing via periodic linting. Local-first plain-text. Eliminates embedding pipelines, vector databases, retrieval tuning for mid-sized corpora (~400K words fits in 200K context window).
**Why it matters to ORGANVM:** This IS the ORGANVM documentation architecture — 810K+ words of markdown, registry-based navigation, no vector DB. Karpathy independently arrived at the same pattern. This validates the approach and provides academic/industry citation for the thesis.
**Route:** `carrier-wave--zeitgeist-thesis` (research citation) AND `system-system--system` (architectural validation)
**Priority:** P1 — thesis ammunition
**Sources:** VentureBeat, MindStudio, Atlan, Mejba.me, LinkedIn (Taboriskiy), TechBuddies, DAIR Academy (13 citations provided)

### ATOM-FB-002: EIGHT-FACTORIAL-PERMUTATIONS
**Domain:** Architecture / Theory
**Content:** 8 organs × sequence-dependent ordering = 8! = 40,320 unique instances. Permutations (order matters) not combinations (order doesn't). Each unique ordering of the 8 organs produces a different system instance.
**Why it matters:** This is the mathematical foundation for why ORGANVM's 8-organ model has such generative potential. 40,320 unique traversal paths through the system. Connects to routing-law design, Styx pipeline traversal SOP, and the combinatorial explosion argument in the thesis.
**Route:** `system-system--system` (formal atom — mathematical proof of generative capacity)
**Priority:** P2 — theoretical framing

### ATOM-FB-003: USPIS-FRAUD-REPORT
**Domain:** Legal / Security
**Content:** URL: https://www.uspis.gov/report — US Postal Inspection Service fraud reporting portal.
**Why it matters:** User may need to file a report (context unclear — possibly related to housing/family situation or mail fraud).
**Route:** `custodia-securitatis` (security/legal) or personal action item
**Priority:** P1 — if actionable, time-sensitive

### ATOM-FB-004: MARKDOWN-LINTING-STANDARDS
**Domain:** Governance / Standards
**Content:** File exists at `~/Workspace/organvm/system-system--system/Automating Markdown Linting Standards.md`. Needs review and integration into the system's governance pipeline.
**Why it matters:** Connects to Karpathy wiki architecture (ATOM-FB-001) — linting/self-healing is a key feature. Also connects to the hook enforcement work (S6) and the markdown-first documentation approach.
**Route:** `system-system--system` (already there — needs review and upgrade to FORMAL status)
**Priority:** P2 — governance infrastructure
