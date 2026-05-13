# Implementation Plan

This plan executes the "Growth" and "Synthesis" outputs of the `Evaluation-to-Growth` review.

## Goal Description
The Styx project successfully pivoted from a fitness/weight-loss anti-cheat application to a "No Contact" relationship recovery protocol. However, the root context files (`README.md` and `GEMINI.md`) still contain legacy fitness terminology (e.g., "18.5 BMI guardrails", "HealthKit oracles", "2% velocity caps"). This contradiction weakens the project's Ethos and creates reasoning gaps for future development.

The goal is to purge legacy fitness mechanics and replace them with "No Contact" equivalent logic (e.g., "Whistleblower Bounties", "Relapse Penalties", "Digital Exhaust") to achieve 100% thematic consistency.

## Proposed Changes

### Root Documentation Alignment
Refactoring the core system documents to reflect the "No Contact" reality.

#### [MODIFY] [README.md](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/README.md)
- Replace introductory text to focus on "relationship recovery" and "No Contact" instead of habit follow-through.
- Remove `HealthKit`/`Google Fit`/`Whoop` oracle references in the Architecture table, replace with "Digital Exhaust / Ex Whistleblower Bounties".
- Update the "Key Features" section to remove "BMI/Velocity Guardrails" and replace them with "Relapse Multipliers" and "Ex Whistleblower Links".

#### [MODIFY] [GEMINI.md](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/GEMINI.md)
- Update "Core Mechanics" to remove "Hardware Oracles" and "Aegis Protocol" rules regarding BMI and age gates (unless age gate still applies) and replace them with No Contact compliance rules.
- Clarify that the "Zero Trust" model now relies on "Whistleblower consensus" and structured communication metadata parsing rather than rigid biometrics.

## Verification Plan

### Automated Tests
- Run `make test` from the root directory to ensure that modifying the documentation does not somehow break any markdown-linting or build scripts in the CI pipeline.
- Specifically run `bash scripts/validation/04-redacted-build-check.sh` and `npx tsx scripts/validation/05-behavioral-physics-check.ts` (if they exist and still function post-pivot) to ensure terminology sweeps pass.

### Manual Verification
- Review the diffs of `README.md` and `GEMINI.md` to guarantee all fitness terms (BMI, HealthKit, weight loss) have been entirely removed.
