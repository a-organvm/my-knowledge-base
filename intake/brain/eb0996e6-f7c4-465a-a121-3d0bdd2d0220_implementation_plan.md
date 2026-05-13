# Phase 5: Tripartite Identity Assembly (The Law of Three Heartbeats)

Your observation that "unique identification is assembled from different locations, coming together as that thing" fundamentally alters the Naming Calculus. It asserts that true identity in this system is not a localized vacuum state, but the **convergence of distributed truth**. 

_"Three pulses, three heartbeats, three taps at the door."_

## 1. The Redefined Genesis Proof
We will rewrite the core identity generation axiom in `axioms/system--naming-calculus.md`.
Instead of the hash being based purely on a single local payload definition, the identifier Hash is mathematically assembled from three required loci (locational references). 

**Proposed Formula**:
$$ U_{id}(P, L_1, L_2, L_3) = P \parallel \text{SHA256}(L_1 \oplus L_2 \oplus L_3)_{0..4} $$
Where:
- $L_1$: The Formal Representation (e.g., its entry in the `system-system--system` IRF index).
- $L_2$: The Operational Representation (e.g., its usage in the Triptych repos or active workspace).
- $L_3$: The Governance Representation (e.g., its dedicated GitHub Issue).

## 2. Infrastructure Updates
### Component: `bin/sys-uid`
- **[MODIFY]** The UID generator must be upgraded. Rather than accepting a random JSON payload, it will explicitly require the three `loci` (URIs, hashes, or node proofs) to stitch the identity together.

### Component: `registry/schemas/entity.schema.json`
- **[MODIFY]** The schema will be updated to enforce the `heartbeats` property. An entity is structurally invalid if it cannot prove its three points of reference in the wider ecosystem.

## 3. The Temporal Bootstrap Problem (A Question for You)
If the identity string (`ent_XXXXX`) inherently requires the GitHub Issue URL ($L_3$) to be generated... how do we make the GitHub Issue if the GitHub Issue needs to mention the identity string in its title? 

> [!IMPORTANT]
> To solve the "chicken and egg" problem of assembling identity from locations that require the identity, how do you envision this occurring observationally?
> 
> **Option A (The Embryonic State)**: The entity exists temporally as a local flat-hash (a single heartbeat) and is considered "embryonic". Only when the other two references are established does the system execute a `MERGE_HEARTBEATS` event, resolving its final true Tripartite Identity.
> 
> **Option B (The Pure Convergence)**: The three external elements (index entry text, github issue ID, repo filepath) act as the primary keys, and the `ent_` ID is strictly a trailing shadow identifier.
> 
> Which mechanic represents your vision of "coming together as that thing"?
