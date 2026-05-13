---
name: Cross-session lane parsing — "X active" = elsewhere, not here
description: When the user names an active project at session open, default-assume it lives in a DIFFERENT session unless they say "in this session"
type: feedback
originSessionId: ba40d4ca-4793-4925-bc17-febb52d17fa1
---
When opening a fresh session and the user says something like "session open else w maddie proj active" / "X is going" / "we're working on Y in another session" — default-assume X is **another session's** lane and pick a **different** one.

**Why:** 2026-04-25 — user wrote "session open else w maddie proj active". I read "else w" as "with" and dove into the Maddie spiral repo. User had to interrupt: "dude i said we're working on maddie in another session." Multiple Claudes are running in parallel per "trinity dispatch" — naming a project at session open usually disambiguates which session is doing what, not assigns the new session to that lane.

**How to apply:**
1. If the user mentions a project at session open without an explicit "work on it here", treat it as **lane signaling** — it's busy elsewhere, find the next-best lane.
2. Read the master session relay first; pick from its sequenced critical path that does NOT collide with the named-busy lane(s).
3. If the relay shows multiple non-colliding moves, just pick the cheapest highest-leverage one and go (per "do what is asked / never preempt + auto mode").
4. Only ask for a lane if the relay shows nothing actionable that doesn't collide.
