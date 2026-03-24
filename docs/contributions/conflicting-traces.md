# Conflicting Traces

**Origin:** Absorbed from @m13v's question on agentic-titan
**Source:** https://github.com/organvm-iv-taxis/agentic-titan/issues/20#issuecomment-4115160082
**Triggers:** unnamed_pattern, convergence, assumption_divergence
**Target Organ:** I

---

## The Question That Opened This

> The stigmergy approach is really interesting. Pheromone decay solving the stale-state problem is elegant - we ended up doing something cruder with TTL-based file locks that agents check before acting.

How do you handle conflicting traces? Like if two agents deposit contradicting RESOURCE traces about the same target - does the higher intensity win, or is there a merge strategy?

## Assumption Divergence

The question assumes a resolution or handling strategy that differs from our implementation. This divergence is the insight — our approach is worth naming precisely because it departs from the expected pattern.

## Unnamed Pattern

The question points at a behavior or property in our architecture that exists in the code but has not been given a formal name or articulated as a reusable principle.

### Properties (to be formalized)

1. *[What invariant does this pattern maintain?]*
2. *[What does it guarantee under failure?]*
3. *[What does it explicitly NOT guarantee?]*

## Independent Convergence

The questioner described an independent implementation that solves a similar problem with a different mechanism. When two systems evolve the same solution shape independently, the pattern is a structural attractor — worth formalizing because it emerges from the problem's constraints, not from copying.

## Relationship to Existing Theory

- *[How does this relate to forward-only FSM governance?]*
- *[How does this relate to idempotent checkpoint writes?]*
- *[How does this relate to reader-side resolution?]*

---

*Absorption Protocol — auto-formalized 2026-03-24*
*Backflow source: agentic-titan, @m13v*
