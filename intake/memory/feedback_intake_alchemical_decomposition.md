---
name: Intake = alchemical decomposition to primitives
description: All humanities-side intake (language, narrative, concept, prose) must be decomposed to universal primitives before back-end implementation; the language layer is the ideal realm (fantasy rendered in cognition), the system layer must be rule-generated, never a literal transcription of the surface artifact.
type: feedback
originSessionId: 51abb963-9c80-4fdf-a973-dd541b56dab7
---
**Rule:** Every intake event — prompt, doc, conversation, sticky note, transcript, sketch — must pass through alchemical decomposition before any system response is built.

**The two realms:**
- **Ideal realm (humanities side):** language, narrative, concept, prose. This is *fantasy rendered in cognition* — authoritative as specification, but not directly executable. The user lives here.
- **System realm (back-end side):** must be *generated from rules*. Surface artifacts are never copied forward; the rule-set is extracted, then instances are instantiated from the rules.

**The decomposition protocol:**
1. Treat the surface artifact as ideal-realm specification (authoritative *intent*, not authoritative *form*).
2. Decompose to universal primitives — entities, operators, relations, lifecycle states, invariants.
3. Build the generative rule-set / protocol that *could have produced* this artifact and N others like it.
4. Instantiate the system from the rule-set — never from the original artifact's structure.

**Why:** The user comes from the humanities; the natural medium is language/narrative. If the system mirrors the surface, it inherits fantasy structure (one-off, narrative-bound, non-composable, un-extensible). Decomposition + rule-generation makes the system computationally honest while preserving the ideal-realm authority of the original. This is the upstream gate to PDE (Product Domain Engine), DIWS (Domain Ideal Whole Substrate), and accumulated rules #32 (discover rules empirically), #35 (rules first, implementations derive), #36 (seed not specification), #37 (generative not copied) — those four are downstream consequences of *this* axiom.

**How to apply:**
- On any intake: pause before responding. Ask: what are the primitives here? what is the rule that could generate this?
- Never paraphrase the user's prose into a checklist or task list as the system response — that flattens ideal-realm density into shallow tactical artifact. Decompose it instead.
- The output of intake is a **rule-set + primitive inventory**, not a restatement.
- Surface text is the *seed crystal*, not the *crystal lattice*. Build the lattice.
- This applies even to single-sentence prompts. Especially to single-sentence prompts — they are the highest-density seeds.
