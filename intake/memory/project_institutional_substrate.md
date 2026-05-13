---
name: Institutional substrate architecture
description: ORGANVM extension from production engine to full institutional singularity — 19 primitives, 4 composition operators, 4 pressure-crystallized formations (AEGIS, OIKONOMIA, PRAXIS, TESSERA)
type: project
originSessionId: e667bfc4-92bc-4867-836d-1c3cd55b4074
---
Initiated 2026-04-20. Major architectural extension to ORGANVM: the system lacked institutional backing (legal, financial, political, advisory, representational, protective). Now specified via SPEC-025 + INST-COMPOSITION + four named formations.

**Why:** ORGANVM gave the single person a studio, lab, shop, control room, podium, salon, megaphone, and constitution. It did NOT give them a lawyer, accountant, strategist, agent, or bodyguard. Every successful person has institutional backing; ORGANVM must provide it to achieve the singularity property.

**How to apply:**
- 19 institutional primitives (PRIM-INST-001 through 020) defined in SPEC-025 at `/Users/4jp/Workspace/meta-organvm/organvm-corpvs-testamentvm/specs/SPEC-025.md`
- Composition grammar (4 operators: CHAIN, PARALLEL, ENVELOPE, FEEDBACK) in INST-COMPOSITION at `specs/INST-COMPOSITION.md`
- Four pressure-crystallized formations: AEGIS (defense), OIKONOMIA (economics), PRAXIS (income), TESSERA (identity) at `specs/formations/`
- Primitives share a FLAT POOL with production primitives — no layers, no fixed topology
- Implementation phased: Phase 0 (assessor, guardian, ledger, counselor, mandator, archivist) is immediate
- The numbered organs are now understood as "the first formations to crystallize" — conventional, not architectural
- Ideal form logic takes precedence over implementation convenience

**Key principle:** The singularity property emerges at compositional coverage, not capability depth. 60% capability across all primitives with free composition > 95% in five primitives that don't compose.

**Status:** Phase 0 IMPLEMENTED (2026-04-21). 6 primitives (assessor, guardian, ledger, counselor, archivist, mandator) + composition engine (4 operators) + AEGIS formation live in `organvm-engine/src/organvm_engine/primitives/`, `composition/`, `formations/`. CLI wired (`organvm primitive *`, `organvm formation *`). 56 tests passing, lint clean. Next: Phase 1 (LLM-powered logic, remaining 13 primitives, OIKONOMIA/PRAXIS/TESSERA formations).
