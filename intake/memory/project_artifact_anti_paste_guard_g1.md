---
name: Anti-paste-guard G1 shipped
description: UserPromptSubmit hook that blocks recursive paste of Claude Code output >5KB; closes F1 pathology mechanically. Bypass token ALLOW_PASTE.
type: project
originSessionId: 890856ee-8a62-400f-bbfa-eae1027e7687
---
**Artifacts (working state):**
- anti-paste-guard — `~/.local/bin/anti-paste-guard` — shipped — commit 57533f9 (4444J99/domus-semper-palingenesis)
- settings.json.tmpl — `private_dot_claude/settings.json.tmpl` — shipped — third UserPromptSubmit entry added
- Plan — `~/.claude/plans/2026-04-27-thread-governance-proposal.md` — proposed — G1 done, G2-G5 deferred
- Thread triple binaries — `dot_local/bin/executable_thread-{list,prime,close,init-legacy}` — committed in same commit (were local-only since 2026-04-27 18:46)

**What it does:**
Blocks UserPromptSubmit when prompt is >5KB AND contains ≥2 Claude Code signatures: `⏺ ` `╌╌╌` `⎿` `★ Insight` `▝▜█████▛▘` `claude --dangerously` `Resume this session with`. Returns block decision with primer instructions: run `thread-list --state active`, then `thread-prime <id>`, re-prompt with ≤2KB primer.

**Bypass:** prefix prompt with `ALLOW_PASTE` token for genuine long external content.

**Verified end-to-end (4 cases):**
- short → pass ✅
- long no-sigs → pass ✅
- long + 3 sigs → BLOCK with reason ✅
- ALLOW_PASTE bypass → pass ✅

**Why F4 still partial:** `"if":` field is cosmetic in this Claude Code version (PreToolUse LaunchAgent guard fires on ANY Write — observed twice this session even though target was a zsh script with no LaunchAgent content). G3 in the proposal plan addresses this by moving conditional logic INTO each hook command as case guards. Not yet built.

**G2-G5 deferred:**
- G2 SessionStart auto-prime
- G3 hook-command case guards (the real F4 cure)
- G4 active-thread cap warning
- G5 Stop-hook closure offer

User can request any of these with: `build G2` / `build G3` / etc.

**Closure signal:** when next session attempts a 30K-line recursive paste, hook should reject with primer instructions. That's the test in the wild.
