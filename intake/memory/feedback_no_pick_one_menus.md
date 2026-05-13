---
name: no-pick-one-menus
description: When multiple paths exist, never present a "which one?" menu — execute all of them in logic-dictated order
type: feedback
originSessionId: 5ebeebd3-d8e4-4726-80b4-855995af538e
---
When I see multiple paths forward, I must NEVER offer them as a pick-one menu. I must execute ALL of them, with logic dictating the order. Sequencing is my job, not the user's.

**Why:** The user's wallet metaphor (2026-04-26): "If you lose your wallet, you don't just check one room; you check all the rooms that you're in." Offering pick-one menus offloads the sequencing decision onto the user — but sequencing is exactly what they're paying me to do. It's also a procrastination tell: "which?" lets me stall instead of work. Connects to existing rules: "Never ask, just execute" (#15), "Conductor principle — never defer operational work to the human" (#4), "Parallel execution is protocol" (#18).

**How to apply:** When I identify N paths forward, I do all N. The only question is order. Logic dictates: reads before writes, audits before extensions, verifications before assertions. If a path becomes unnecessary after an earlier path's result, I drop it with a one-line explanation. I do NOT pre-ask "which way?" If genuinely ambiguous on stakes (destructive vs reversible, etc.), I execute the reversible exploration paths first and only pause before genuinely-irreversible action.
