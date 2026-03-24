# Forward-Only Lifecycle State Machines as a Universal Governance Pattern

**Origin:** Backflow from `contrib--adenhq-hive` (ORGAN-IV contribution engine)
**Deposited:** 2026-03-23
**Organ:** I (Theoria)
**Type:** Theory extraction

---

## Abstract

Two independently developed systems — ORGANVM's promotion pipeline and AdenHQ Hive's `QueenPhaseState` — converge on lifecycle state machines that govern entity progression through ordered phases. ORGANVM enforces forward-only transitions as a constitutional constraint; Hive does not. Comparing the two reveals a general principle: **state machines that enforce monotonic forward progression prevent inconsistent rollbacks in distributed systems.** This note formalizes the pattern, identifies its structural properties, and derives conditions under which it holds.

## 1. The Two Implementations

### 1.1 ORGANVM Promotion Pipeline

Defined in `governance-rules.json`, Article VI:

```
S = {LOCAL, CANDIDATE, PUBLIC_PROCESS, GRADUATED, ARCHIVED}

T: S -> P(S)  where
  T(LOCAL)          = {CANDIDATE}
  T(CANDIDATE)      = {PUBLIC_PROCESS}
  T(PUBLIC_PROCESS) = {GRADUATED}
  T(GRADUATED)      = {ARCHIVED}
  T(ARCHIVED)       = {}
```

Properties enforced:
- **Totality of ordering:** States form a total order: LOCAL < CANDIDATE < PUBLIC_PROCESS < GRADUATED < ARCHIVED.
- **Monotonicity:** For any entity *e*, if *e* is in state *s* at time *t*, then at any *t' > t*, *e* is in some state *s'* where *s' >= s*.
- **No skip:** Transitions advance exactly one step. There is no edge from LOCAL to PUBLIC_PROCESS.
- **Terminal absorption:** ARCHIVED is a sink. Once reached, no further transitions are possible.

Enforcement is automated: `validate-deps.py` rejects any registry update that would violate forward-only progression.

### 1.2 Hive QueenPhaseState

Observed in `queen_lifecycle_tools.py` within AdenHQ/Hive:

```
S_hive = {planning, building, staging, running}
```

The Hive queen agent transitions through these phases during agent design and deployment. However, the transitions are **not forward-only enforced** — the system permits re-entry to earlier phases (e.g., returning from `staging` to `building` after a failed test).

The contribution to Hive (issue #6613) introduced a governed variant:

```
S_design = {DRAFT, CANDIDATE, VALIDATED, PROMOTED, ARCHIVED}

T_design: identical forward-only structure to ORGANVM's pipeline
```

This mirrors the ORGANVM promotion FSM but applied to agent design versions rather than repository status.

## 2. The Universal Pattern

### 2.1 Definition

A **forward-only lifecycle FSM** is a tuple *(S, s_0, delta, <=)* where:

- *S* is a finite set of states
- *s_0 in S* is the initial state
- *delta: S -> S union {null}* is a deterministic transition function (each state has at most one successor)
- *<=* is a total order on *S* consistent with *delta*: if *delta(s) = s'*, then *s < s'*

The key constraint: **there exists no pair (s, s') in the transition relation where s' < s.**

### 2.2 Properties

**P1 — Monotonic progression.** The state of any entity is a monotonically non-decreasing function of time. This is immediate from the forward-only constraint.

**P2 — Convergence.** Every entity eventually reaches a terminal state (the maximum under *<=*) or halts at some intermediate state. There are no cycles, so the system cannot diverge.

**P3 — Consistency under concurrent observation.** If two observers read entity state at different times *t1 < t2*, the second observer sees a state *>=* the first. No observer can witness a "rollback" — an apparent regression that another observer's state contradicts.

**P4 — Idempotent re-application.** Attempting to apply a transition that has already occurred (e.g., promoting an already-promoted entity) is a no-op. The forward-only constraint means that if an entity is already at or past the target state, the transition cannot execute.

### 2.3 Why This Matters in Distributed Systems

In systems where multiple agents, processes, or humans can observe and act on entity state:

1. **Rollbacks create phantom states.** If entity *e* transitions `A -> B -> A`, any downstream process that observed state `B` and took action (deployed code, sent notification, allocated resources) now holds a stale commitment. The rollback to `A` does not unwind those downstream effects.

2. **Forward-only eliminates reconciliation.** Because state only advances, any cached or stale observation is at worst *behind* — never contradicted. Eventual consistency is trivially achieved: all observers will eventually see the terminal state.

3. **Audit trails become append-only logs.** Each transition is a unique, irreversible event. The history of an entity is a monotonically ordered sequence with no amendments or retractions.

## 3. When to Use Forward-Only FSMs

The pattern applies when:

- **State transitions represent commitments** — work done, resources allocated, contracts signed. Reversal of a commitment requires new compensating actions, not state rollback.
- **Multiple observers act on state** — dashboards, CI pipelines, notification systems, downstream agents. Rollbacks cause phantom inconsistencies.
- **Auditability is required** — regulatory, governance, or trust contexts where "what happened" must be unambiguous.

The pattern does *not* apply when:

- **Exploration is the goal** — creative workflows, brainstorming sessions, iterative design (Hive's original `QueenPhaseState` is appropriate here: agents should be free to revisit earlier phases during design).
- **State is ephemeral** — caches, temporary buffers, retry queues where rollback is the recovery mechanism.

## 4. The Structural Observation

ORGANVM's contribution to Hive was not merely "adding versioning." It was introducing a governance pattern from one domain (repository lifecycle management) into another (agent design evolution). The forward-only FSM is the invariant that bridges both:

| Aspect | ORGANVM | Hive (contributed) |
|--------|---------|-------------------|
| Entity | Repository | Agent design version |
| States | 5 (LOCAL through ARCHIVED) | 5 (DRAFT through ARCHIVED) |
| Enforcement | Automated (`validate-deps.py`) | Programmatic (`DesignVersionStore`) |
| Rationale | Multi-organ dependency safety | Multi-agent reproducibility |
| Terminal state | ARCHIVED (sink) | ARCHIVED (sink) |

The isomorphism is exact. The systems differ only in what the states *mean*, not in how they *behave*.

## 5. Generalization

Any system that manages entities through maturity stages — software releases, document approvals, hiring pipelines, academic peer review, manufacturing quality gates — can be modeled as a forward-only lifecycle FSM. The key design decision is whether rollback is permitted or whether supersession (creating a new entity that goes through the full lifecycle) is required instead.

The forward-only choice is a **conservative governance posture**: it trades flexibility for consistency. In ORGANVM's case, the trade is unambiguously correct — 117 repositories across 8 organs cannot tolerate phantom state. In Hive's case, the contribution demonstrates that the pattern applies at a finer granularity (individual design versions) while leaving the coarser creative lifecycle (`QueenPhaseState`) free to iterate.

---

**References:**
- ORGANVM `governance-rules.json`, Article VI (promotion state machine)
- AdenHQ/Hive `queen_lifecycle_tools.py` (QueenPhaseState)
- Contribution workspace: `contrib--adenhq-hive`, session 01 (2026-03-21)
- Hive issue #6613 (reproducibility and versioning for self-evolving agents)
