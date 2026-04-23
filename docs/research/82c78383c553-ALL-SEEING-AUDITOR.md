# Design Doc: ALL-SEEING-AUDITOR (Vigiles Aeternae — Theatrum Mundi)

**ID:** 82c78383c553
**Status:** DRAFT
**Priority:** P2
**Domain:** Strategic / Auditor Architecture

## 1. Executive Summary
The **ALL-SEEING-AUDITOR** is a strategic architectural component designed to provide continuous, high-fidelity oversight of the Knowledge Base. It operates as an autonomous "watcher" (Vigiles Aeternae) that ensures the internal representation of knowledge (Theatrum Mundi) remains consistent, truthful, and structurally sound.

## 2. Problem Statement
As the PKB grows to tens of thousands of "atoms," manual verification becomes impossible. "Context rot," redundant extraction, and semantic drift threaten the utility of the system. We need a way to audit the database without human intervention at every step.

## 3. Proposed Architecture: The Triadic Oversight Loop

### A. Structural Audit (The Grammar)
- **Invariant Checking:** Ensure all `AtomicUnits` follow the required schema.
- **Link Integrity:** Verify that `relatedUnits` actually exist and form valid directed graphs.
- **Orphan Detection:** Identify units with no incoming or outgoing connections.

### B. Semantic Audit (The Logic)
- **Consistency Probes:** Detect contradictory "insights" extracted from different conversations.
- **Redundancy Compression:** Identify semantically identical atoms that should be merged (Deduplication).
- **Quality Scoring:** Rate atoms based on their density, clarity, and utility.

### C. Evolutionary Audit (The Rhetoric)
- **Trend Analysis:** Monitor how the "Theater of the World" evolves over time.
- **Gap Detection:** Identify areas where the Knowledge Base has high uncertainty or missing "connective tissue."
- **Directive Tracking:** Ensure that "Canonical Directives" are being honored by the system's own analyzers.

## 4. Implementation Strategy (Phase 6 Integration)

1.  **Auditor Registry:** A new table `audit_runs` to track the history of every integrity check.
2.  **Verification Probes:** Modular scripts in `src/auditors/` that target specific invariants.
3.  **Automated Remediation:** The Auditor shouldn't just report; it should propose "Remediation Plans" (Praxis) for fixing issues.

## 5. Dialect & Aesthetics
The Auditor's output must follow the **FORMAL_LOGIC** dialect, presenting findings as a series of propositions and proofs. The "Theater of the World" (Theatrum Mundi) should be viewable as a dynamic graph where the Auditor highlights "tensions" or "cracks" in the structure.

---

*“Who watches the watchers? The logic itself.”*
