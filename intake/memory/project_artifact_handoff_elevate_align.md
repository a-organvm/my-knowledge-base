---
name: HANDOFF — sovereign-systems--elevate-align
description: Repo-root 5-group relay file capturing every in-flight thread (V4 shapes, mobile polish, CI unblock, custom domain, filter affiliates) so a future session can pick up cold
type: project
originSessionId: 4c7b6f01-3a2b-4ada-9302-d838fe4c0ab1
---
**What:** Single living `HANDOFF.md` at the repo root with 5 self-contained relay prompts. Each group has a trigger condition, why-it-matters context, paste-able prompt block, files to read first, line-numbered implementation entry points, verification commands, and deploy/close steps. Designed so a future session (any agent, any model) can resume one thread without reading the chat history.

**Where:**
- Live file: `~/Workspace/organvm/sovereign-systems--elevate-align/HANDOFF.md`
- Plan source: `~/Workspace/organvm/sovereign-systems--elevate-align/.claude/plans/2026-04-25-handoff-relays.md`
- Mirror in user plans: `~/.claude/plans/hand-off-relays-vast-pnueli.md`

**Project:** `sovereign-systems--elevate-align` (ORGAN-III, organvm-iii-ergon)

**For whom:** Anthony (operator) + future Claude/Codex/OpenCode/Gemini sessions

**State:** shipped — commit `454a047` on main, pushed

**Groups:**
1. V4 Node Shapes — BLOCKED on Maddie's reply to Proposal A
2. Mobile Spiral Polish — READY, opportunistic, parallel-able
3. CI Auto-Deploy Unblock (GH#52) — BLOCKED on Anthony rotating CLOUDFLARE_API_TOKEN
4. Custom Domain Go-Live (GH#3) — BLOCKED on Maddie/Anthony coordinating DNS
5. Filter Affiliate Flow (GH#49) — BLOCKED on Maddie sending water-filter info

**Convention:** Single living file at repo root, not dated. Updates rewrite the file with a new "Last update" timestamp at top. Dated archives go in `.claude/plans/`. Modeled on `~/Workspace/4444J99/hokage-chess/HANDOFF.md`.

**Next action:** When any group's trigger satisfies (Maddie reply, token rotation, DNS change, filter info), open HANDOFF.md, paste the relevant Relay block into a fresh session. After completing a group: edit HANDOFF.md to remove or mark the group done, bump Last update, recommit.

**Companion artifact:** `project_artifact_spiral_maddie.md` — covers the spiral renderer specifically (V1 → V3 history, current code state). The HANDOFF is the multi-thread index; the spiral artifact is the renderer-specific deep state.
