# Reader-Side Resolution in Append-Only Environments with Decay

**Origin:** Extracted from agentic-titan issue #20 conversation with Matthew Diakonov (@m13v), 2026-03-18 through 2026-03-24. His question about conflicting pheromone traces exposed a pattern that was implemented but unnamed.

**Independent convergence:** m13v's `tmux-background-agents` uses TTL-based file locks — binary version of the same principle. Two independent systems arriving at the same resolution pattern is evidence of a structural attractor.

---

## The Pattern

In systems where multiple agents write to a shared environment without coordination, conflict resolution can be deferred entirely to read-time rather than enforced at write-time.

### Formal Properties

Let `F` be a field (shared environment), `W` the set of write operations, and `R` the set of read operations.

1. **Append-only writes:** `∀ w ∈ W: F' = F ∪ {w}` — writes never overwrite or delete existing entries
2. **Contradiction tolerance:** `∀ w₁, w₂ ∈ W: contradict(w₁, w₂) ⟹ both persist in F` — the field does not resolve contradictions
3. **Decay function:** `∀ entry ∈ F: intensity(entry, t) = intensity(entry, t₀) × (1 - decay_rate)^(t - t₀)` — unreinforced entries fade
4. **Reinforcement:** `∀ w ∈ W: if ∃ entry ∈ F matching w, then intensity(entry) += δ` — repeated signals amplify
5. **Reader resolution:** `∀ r ∈ R: resolve(r, F) = agent_logic(all entries at location)` — the sensing agent decides, not the field

### What This Is NOT

| Pattern | Resolution At | Guarantee |
|---------|--------------|-----------|
| ACID transactions | Write-time | Strong consistency |
| Eventual consistency | Background convergence | All replicas converge |
| Last-write-wins | Write-time (timestamp) | Latest survives |
| CRDTs | Merge function per type | Automatic convergence |
| **Reader-side resolution** | **Read-time** | **None — reader decides** |

The field makes no convergence guarantee. It stores everything, decays everything, and leaves the intelligence to the consumer. This is a deliberate trade-off: zero coordination overhead at the storage layer, at the cost of requiring smart readers.

### Why This Works for Agent Systems

Agent systems have a property that databases don't: **the readers are intelligent.** A sensing agent can:
- Compare intensities (recency/reinforcement as proxy for confidence)
- Check depositor IDs (trust weighting)
- Cross-reference trace types (a WARNING at the same location as a RESOURCE is informative)
- Use its own context to break ties (domain knowledge the field doesn't have)

This makes reader-side resolution natural for multi-agent systems and unnatural for traditional data stores where readers are dumb query engines.

### Biological Analogues

- **Ant pheromone trails:** Ants deposit trails to food. Trails that lead to food get reinforced by returning ants. Trails that lead nowhere evaporate. No ant "decides" which trail wins — the reinforcement/decay dynamic resolves it.
- **Crow roost dynamics:** Crows at information centers observe departure trajectories. Contradicting departures (different directions) coexist. Individual crows decide which trajectory to follow based on their own hunger and the intensity of the signal.

### Generalization Beyond Pheromone Fields

The pattern applies anywhere contradictions are expected and coordination is expensive:
- Shared file systems with TTL locks (m13v's implementation)
- Event streams where consumers maintain their own projections
- Collaborative editing where conflicting suggestions coexist until a human resolves
- Intelligence analysis where contradicting reports accumulate and the analyst decides
- Market signals where contradicting indicators coexist and the trader's model resolves

### Relationship to Sibling Patterns

- **Idempotent checkpoint writes** (LangGraph): repeated writes are safe. Reader-side resolution: *contradictory* writes are safe.
- **Forward-only FSM governance** (ORGANVM/Hive): state transitions are monotonic. Reader-side resolution: field state is monotonically growing (append-only) with decay as the only deletion mechanism.
- **Stigmergy** (general): indirect coordination through environment modification. Reader-side resolution is the conflict-handling strategy within stigmergic systems.

---

*Backflow source: contrib--m13v/agentic-titan#20, question 4 of 4*
*Cross-reference: hive/stigmergy.py (implementation), hive/fission_fusion.py (consumer)*
