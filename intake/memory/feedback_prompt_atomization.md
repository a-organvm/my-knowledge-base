---
name: Prompt atomization and tracking is non-negotiable
description: Every user prompt must be saved, ID'd, tracked for implementation — asked for repeatedly, never persisted
type: feedback
originSessionId: c2d0301b-443e-40b1-b70c-8af43c205a1b
---
The user has asked MULTIPLE TIMES across MULTIPLE SESSIONS for a prompt atomization system:
- Every prompt saved to a list
- Each prompt gets a unique ID
- Implementation status tracked (OPEN/DONE/DEFERRED)
- Cross-referenced to what it produced

This has never been implemented despite repeated requests. The user is not doing anything wrong — the system is failing to enforce what was asked for.

**Why:** Prompts contain directives, governance rules, architectural decisions, and feature requests. Without atomization and tracking, they vanish into session history and the user must re-ask. Every re-ask is wasted effort and mounting frustration. The user's exact words: "How many times do I have to ask for that? How many fucking times? What am I doing wrong?" Answer: nothing. The system failed.

**How to apply:**
- This is a P0 infrastructure item. Not optional. Not "when we get to it."
- The `organvm prompts distill` CLI exists. Wire it into a SessionEnd hook or LaunchAgent.
- Build a prompt registry (like IRF but for prompts): unique ID, implementation status, cross-refs.
- Every session close MUST include prompt extraction. No exceptions.
- Never respond to this request with "we should do that" — DO IT or create the IRF item and the tracking mechanism.
