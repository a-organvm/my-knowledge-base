---
name: Layer F — Network as substrate (persona + archetype + opportunity)
description: Spec for treating people as multi-domain sub-substrates with archetype mapping, opportunity atom kind, selfish-altruistic ledger, critic mode rendering. SPEC-ONLY.
type: project
originSessionId: f3beab49-8440-4336-b4db-299e2933f5a1
---
**What**: Four sub-systems:
1. Persona scanner — each `~/Documents/personas/*` file becomes a `kind: persona` atom with 8 strata (per DIWS v2.2: ontology, lineage, constellation, gap-map, agent-fleet, production-stack, internal-magnet, external-contribution)
2. Archetype registry — universal types in YAML at `archetypes/*.yaml` with `tends_to_need`, `tends_to_give`, `common_dynamics`, `common_pitfalls`, `navigation_moves`. Initial 8: muse-collaborator, partner-in-functional-silence, dual-venture-founder-client, closed-thread, pre-active-stub, referral-network-node, domain-mirror-peer, infrastructure-collaborator
3. Network graph — typed edges with `domain_cross[]` tags, state (active-warm/dormant/closed/latent)
4. Opportunity atom kind — bound to (persona × archetype-affordance × domain) with selfish-altruistic ledger (their_gain + user_learning columns)

Critic mode (`dm critic <persona>`): deterministic compilation from archetype YAMLs joined to persona current state, produces genre reading + next-beat predictions + archetypal moves to make + "what everyone is overconfident about."

**Where**:
- Plan: `2026-04-27-network-as-substrate-persona-archetype.md` (chezmoi 1e7e9d4)
- Target build: `scanners/personas.py`, `scanners/opportunities.py`, `archetypes/*.yaml` (8 initial), `lenses/network.yaml`, `~/.local/bin/{dm-critic, dm-opportunities}`
- Read targets: `~/Documents/personas/*.md` (rob-bonavoglia, maddie, scott-lefler, etc. + lexicon.yaml siblings)

**Project**: `organvm/my-knowledge-base` + `~/Documents/personas/`

**For whom**: User — the wrench-toucher pivot ("look at network, opportunities for improvement, persona-of-archetype")

**State**: SPEC. None built. Existing collaborator memories (Maddie, Rob, Scott, Becka closed-thread, Jessica pre-active stub) are the seed data.

**Pending feedback**:
- Anthony as persona in own substrate? (default yes, recursive self-reference)
- Archetype completeness threshold (default: tends_to_need + tends_to_give + common_dynamics required)
- Selfish-altruistic ledger granularity (default: persona + opportunity, defer per-edge)
- Network depth horizon (default 1 hop beyond direct relationships)
- Critic mode register (default deterministic; LLM-augmented later optional)
- Wrench radius (default ≤2hr blast-radius bias for next 30 days)

**Next action**: Slice F1 — `personas.py` scanner + 8 archetype YAMLs + bootstrap network graph from existing collaborator memories. Slice F2 — opportunity atomization. Slice F3 — `dm critic`.
