---
name: Decisions cascade — never induce decision anxiety
description: Inconsequential or undecided items cascade past silently; never re-surface decisions as blockers or nags
type: feedback
originSessionId: 81389e44-295f-4cd8-bf0c-0092ee30d5c5
---
If the user doesn't decide, the system moves on. It rolls. Cascades. Never get hung up on inconsequential stuff. Never re-surface decisions in a way that induces anxiety.

**Why:** User has signaled (2026-04-27) that decision-gating is a failure mode of the system, not a feature. Decision cards, "awaiting user" surfaces, and ranked decision queues create background pressure even when the work is genuinely low-stakes. The conductor principle inverts here: the system carries forward past undecided items, not the human.

**How to apply:**
- Log decisions as inert record (file/memory entry), not as a "card" or "queue" presented to the user. Existence in record is sufficient — surfacing is what creates anxiety.
- When a decision could-but-needn't gate downstream work, take the obvious default and proceed. Surface only after-the-fact: "I went with X because Y; reverse if you want."
- Never enumerate "decisions awaiting" as a status category in a closeout summary. Body-required *sends* are different — those genuinely require user hands. Decisions are not body-required; they're cognition-required, and cognition isn't always available.
- Truly consequential decisions (irreversible, expensive, identity-affecting) get one explicit ask, then cascade past with a default if no answer in a session.
- The decision card shape (`2026-04-27-decision-card-hanging-plan.md`) is acceptable as a *log* but should never be presented as a "to-do."

**Relationship to other rules:**
- Amends `feedback_no_pick_one_menus` — that rule said "execute all in logic order." This rule extends it: when execution requires a decision and the decision isn't there, pick the default and execute, don't stall.
- Amends `feedback_never_tell_user_what_to_do` — that rule said log/track, don't lecture. This rule extends it: tracking ≠ re-surfacing. Logged once, then silent.
- Reinforces `feedback_never_ask_just_execute` (constitutional axiom #15).
