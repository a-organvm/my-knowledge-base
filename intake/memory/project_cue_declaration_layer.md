---
name: CUE declaration layer for a-organvm
description: system.toml replaced by system.cue using CUE constraint language; landscape research completed; repo unified
type: project
originSessionId: d6d21892-48cb-47e0-8097-f17ac76dae95
---
## Decision: CUE for the declaration layer (2026-04-21)

Deep landscape research into 8 declarative configuration systems (Nix, Guix, Dhall, CUE, Jsonnet, Terraform/HCL, Pulumi, Bazel) led to selecting CUE as the constraint language for a-organvm's declaration layer.

**Why CUE**: Types and values on the same lattice (self-enforcing by construction). Commutative, associative, idempotent unification (order doesn't matter). No inheritance. Sub-Turing (always terminates). Declaration IS validation — no separate schema needed.

**Why:** system.toml was inert TOML — readable but not evaluable, composable, or self-enforcing. CUE constraints catch violations at evaluation time, not never.

**How to apply:** system.cue is the living law. Run `cue vet system.cue` to validate. Elements, compounds, formations, governance all constrained with types. Invalid states produce errors, not silent wrong values.

## Repo unification (2026-04-21)

Two separate a-organvm locations merged into one:
- `~/Workspace/a-organvm/` is now the canonical clone of `a-organvm/a-organvm.git`
- Contains BOTH the living organism code (5 Python functions, 140 tests) AND the spec files (system.cue, LANDSCAPE.md, fossil records)
- `~/Workspace/organvm/sovereign--ground/holds--same/a-organvm/` is now a STALE redundant clone — should be removed or decommissioned

## Open work
- Compound formulas not yet validated against actual element symbols in CUE
- Signal graph not yet derived from CUE declaration
- immune_verify.py doesn't read system.cue yet (bridge not built)
- Fossil record not yet integrated into CUE constraints
- sovereign--ground/holds--same/a-organvm/ stale clone needs decommission
