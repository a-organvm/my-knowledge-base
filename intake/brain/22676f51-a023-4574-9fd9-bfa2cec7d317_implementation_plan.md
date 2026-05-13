# Escrow Protocol Implementation Plan

The Escrow Protocol functions as a "satellite" returning from orbit to adjudicate operational abstractions against the formal laws of `system-system--system`. It bridges the gap between the formal axioms and the biological/engine mechanisms of the Triptych (`a-organvm`, `meta-organvm`, `organvm-iv-taxis`).

## User Review Required

> [!IMPORTANT]
> The protocol requires a shared workspace context or a defined set of environment variables to point to the Triptych directories. We need to ensure that the `piece` tool can effectively "see" into these external repositories.

> [!WARNING]
> Automatically exporting "Natural Law Decisions" back into `a-organvm` as gate contracts or functions requires write access and may impact existing logic.

## Proposed Changes

### [System-System--System]

#### [MODIFY] [sys.toml](file:///Users/4jp/system-system--system/sys.toml)
Add `protocol` configuration and vocabulary for escrow states.

#### [NEW] [escrow-protocol.md](file:///Users/4jp/system-system--system/derivations/escrow-protocol.md)
Formal documentation of the protocol as a derivation of the 4 Laws.

#### [NEW] [escrow](file:///Users/4jp/system-system--system/escrow)
A new script (Python) or a sub-command for `piece` that implements the research and adjudication loop.

---

### [The Protocol Workflow]

1. **Step 1: Abstraction Submission**
   - The user provides an abstraction (e.g., a "Rule" for scaling).
   - `escrow` creates a "Pending Resolution" piece in `system-system--system`.

2. **Step 2: Implementation Research**
   - `escrow` executes `ripgrep` across `$BODY`, `$MIND`, and `$SEED`.
   - It identifies existing patterns, tests, and comments that relate to the abstraction.

3. **Step 3: Ideal Consultation**
   - `escrow` matches the abstraction against the 13 Axioms and 75 Atoms.
   - It identifies conflicts or missing dependencies in the formal logic.

4. **Step 4: Natural Law Decision**
   - The protocol generates a `DECISION` (a new file in `a-organvm` or a updated `sys.toml` entry).
   - This decision "returns" from escrow to the operational plane.

## Open Questions

- Should the `escrow` tool be a standalone executable or an extension of the `piece` CLI?
- What are the exact paths for `$BODY`, `$MIND`, and `$SEED` to be baked into the config?
- How should "Natural Law" communicate a REJECTION of an abstraction?

## Verification Plan

### Automated Tests
- Test `escrow --research` with a known keyword present in `agentic-titan`.
- Test `escrow --adjudicate` to ensure it correctly identifies an axiom violation (e.g., breaking Law 4 scale invariance).

### Manual Verification
- Run a full escrow loop for the "Parameter Path as Identity" abstraction from the Universal Rendering Thesis.
