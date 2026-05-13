---
name: Full hanging-items implementation plan (2026-04-25)
description: Cross-session inventory of 39 hanging items across spiral/hokage/conversation-engine/system/client lanes with dependency graph, parallel dispatch, and sequenced critical path
type: project
originSessionId: 5a485c0a-8c2d-4af3-a88c-63d09aca2467
---
**What:** Comprehensive plan covering every open thread across three parallel Claude sessions today (engine/infra, spiral-glow, Hokage-strategy). 39 items grouped into 5 domains, dependency-graphed, with ranked decision points awaiting user.

**Where:**
- Live: `~/.claude/plans/2026-04-25-hanging-items-full-implementation-plan.md`
- Chezmoi source: `~/Workspace/4444J99/domus-semper-palingenesis/private_dot_claude/plans/2026-04-25-hanging-items-full-implementation-plan.md`

**Project:** cross-cutting (no single repo)

**State:** shipped 2026-04-25 — chezmoi auto-commit + auto-push handled propagation

**Domain breakdown:**
- A. Spiral / Maddie: 9 open + 1 in-flight (glow agent)
- B. Hokage / Rob: 14 open + 1 in-flight (export Q)
- C. Conversation engine: 4 open
- D. System / Infra: 9 open
- E. Client / Comms: 3 open (Maddie, Rob, Becka)

**9 user-decision points (top 5 ranked):**
1. A1 spiral glow pivot (sprite vs ship)
2. B1 ChatGPT projects (5 named: build now, on-demand, shelf)
3. B5 Kit API key (Hokage funnel)
4. A4+A6 CF auth (custom domain + CI auto-deploy, single auth unblocks both)
5. D1 resolve-bootstrap config (20 hardcoded path violations)

**Critical chains:**
- A1 → A2 → A3 → B12 (landing-engine spiral-then-Hokage; ~6h downstream)
- B8 → B9 (LCC port → Character Sheet; ~10h downstream)
- B5 unblock → Hokage funnel live

**Highest-leverage unblocked work for me:** B2 (ChatGPT json-per-conversation adapter — extends the multi-part pattern I shipped today, addresses brainstorm-export-20260423 ingest pain).

**Pending feedback:** none — plan written autonomously, awaiting user to act on decision points.

**Next action:** wait for user to clear decision queue OR proceed on isolated unblocked work (B2, C2, C3, D8, D9 partial).

**Why:** "Build a full implementation plan for all hanging" was the user's literal directive. Plan respects universal rules: #5 plans-are-artifacts (committed + pushed), #20 never-reduce-scope (no items dropped), #21 no-preemption (ranks but doesn't decide for user), #53 atoms-permanent (D7 atom backlog surfaced for triage, not closure).
