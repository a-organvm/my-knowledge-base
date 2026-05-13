---
name: Trinity dispatch — 3 agents per task, merge results
description: Always fire 3 agents in parallel for non-architectural work; Claude only does masterminding + merge
type: feedback
originSessionId: 7596d22d-ad09-4226-bbc9-de84801fb0ac
---
The dispatch table was wrong. It treated agents as primary/backup (sequential fallback). The correct model:

**Claude**: Architecture, audit, masterminding, merge/cleanup ONLY. Everything else is delegated.

**Everything non-architectural**: Fire 3 agents simultaneously (Codex + OpenCode + Gemini), get 3 independent results, merge the best parts. Claude reviews and shapes the merged output.

**Why:** 
- Different agents have different strengths (Codex: scaffolding, OpenCode: infrastructure, Gemini: research/content)
- Redundancy — if one fails, two others deliver
- Quality through synthesis — merge produces better output than any single agent
- Speed — all run in parallel, no sequential waiting
- OpenCode is a "fantastic beast" — treating it as backup-only wastes capability

**How to apply:** When dispatching any non-strategic task, ALWAYS fire at minimum Codex + OpenCode + Gemini in parallel on the same prompt. Compare outputs. Merge. Claude cleans up and commits. The only exception is when the task is truly Claude-only (system architecture, cross-organ governance, strategic decisions). (2026-04-23)
