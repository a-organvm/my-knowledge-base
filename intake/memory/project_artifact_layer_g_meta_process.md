---
name: Layer G — Meta-process (repetition as second-order generative form)
description: Spec for codifying recurring event-sequences as YAMLs invocable by name. Closes the cascade — future cascades execute by name without re-articulation. SPEC-ONLY.
type: project
originSessionId: f3beab49-8440-4336-b4db-299e2933f5a1
---
**What**: Each repeated choreography becomes a YAML at `meta-processes/*.yaml`: trigger specs, inputs, choreography steps, output invariants, forbidden moves. Detection: ≥3 instances of structurally similar sequence → candidate; ≥1 instance + explicit user directive → canonical. Codification operator: extract pattern from instance log → emit YAML. Invocation: `dm meta run <id> --inputs ...` executes the choreography.

Layer G is Layer E one order higher: E distills atoms (instance → generative rule); G distills event-sequences (instances → choreography rule). Both inverse-pair operations: distill (compress to rule), re-project (expand to surface or instance).

Six initial meta-processes from today's cascade: `cascade-a-layer`, `save-dated-plan`, `acknowledge-hook-fire`, `insight-mockup-plan-forks`, `decompose-to-generative-form`, `surface-disagreement`. After codification, future cascades invoke by name; user no longer re-explains.

**Where**:
- Plan: `2026-04-27-meta-process-repetition-second-order-generative.md` (chezmoi 1e7e9d4)
- Target build: `~/Workspace/organvm/my-knowledge-base/meta-processes/*.yaml` (6 initial), repetition detector, codification UI, executor

**Project**: `organvm/my-knowledge-base`

**For whom**: User — operationalizes feedback_process_codification.md rule + answers user's "instead of repeating myself anymore" directive

**State**: SPEC. None built. Highest-leverage immediate work because it makes future sessions cheaper.

**Pending feedback**:
- Detection threshold (default ≥3 candidate / ≥1+directive canonical)
- Reflexivity boundary (default yes, fixed-point convergence)
- User authority for canonical promotion (default user-approval; auto-promote at ≥10 instances optional)

**Next action**: Slice G3 — write the 6 initial meta-process YAMLs from today's cascade. Highest priority because every future session benefits. Slice G1/G2 (detector + codification UI) come later.
