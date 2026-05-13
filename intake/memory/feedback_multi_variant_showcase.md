---
name: Multi-variant showcase over binary pivot
description: When a client-decision reveals a fork between two design options, build both as variants and present simultaneously rather than picking one for them
type: feedback
originSessionId: 5a485c0a-8c2d-4af3-a88c-63d09aca2467
---
When the work surfaces a binary fork (e.g., spiral renderer: extruded geometry vs sprite-starburst), do NOT treat it as "pick one and ship." The structural gap the question reveals is that *clients can't decide without comparing*, so the right move is to build both as toggleable variants and present simultaneously.

**Why:** Anthony said this verbatim 2026-04-25 in response to the spiral glow pivot question — "It speaks to a gap that can be filled by being able to present clients with multiple examples at once." A binary internal-question becomes a feature. The ability to render multiple variants concurrently is itself a deliverable; clients gain agency by seeing options side-by-side rather than receiving a single take.

**How to apply:**
- Spiral / Maddie: spiral renderer already has `?variant=stars` URL param — extend with `?variant=sprites`, `?variant=symbols`, etc. AND build a `/showcase` page that renders them in a grid for direct comparison.
- Hokage / Rob: same pattern for landing page hero treatments, value-ladder copy variants, persona-specific funnels (the landing-engine plan B12 already has this baked in via personas × narratives).
- Future client work: when in doubt between two design choices, default to "build both, let client choose by comparing." Compare URL toggles + showcase pages.
- Cost guard: don't build *every* permutation — build the small set of *meaningfully different* variants. The point is decision-enabling comparison, not exhaustive enumeration.

**Anti-pattern:** Don't ask the client "do you want A or B?" before showing both — they often can't tell from words alone, and asking forces them to do the imagination work that the comparison would do for free.

**Generalizes to:** any creative output for clients (visual, copy, structural). The deliverable is *the comparison*, not the chosen variant.
