---
name: system-system--system atom registry
description: Formal system with 238 atoms across 28 documents, 56.7% FORMAL; GH-#8 closable; Theorems 7/8/10/11 formalized; 55-atom gap to 80% target
type: project
originSessionId: 80581eb0-933d-4de3-a31f-f0c420955109
---
Formal theoretical system at `~/Workspace/organvm/system-system--system/`.

**State (2026-04-20):** 238 atoms across 28 documents. 135 FORMAL (56.7%), 89 SKETCHED, 13 INTUITIVE. Up from 203 atoms / 49.3% FORMAL.

**Why:** Core theoretical substrate for ORGANVM — axioms, derivations, proofs. Each atom is a trackable unit of formalization (INTUITIVE → SKETCHED → FORMAL).

**How to apply:**
- GH-#8 (document decomposition) is closable — all documents have ATM markers
- GH-#5 target: 80% FORMAL = 190 atoms. Gap: 55 atoms to upgrade
- Next high-value targets: Theorems 9, 12, 13 (Gödelian/Knaster-Tarski formalizations)
- Atom registry: `atom-registry.yaml`. Validate with grep counts.
