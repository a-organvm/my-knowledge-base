---
name: Single conductor session — no parallel Claude sessions ever
description: ONE Claude session open at a time. It dispatches to Codex/Gemini/OpenCode from inside itself. User never opens a second tab. Every collision incident traces to multi-session.
type: feedback
originSessionId: 80581eb0-933d-4de3-a31f-f0c420955109
---
ONE Claude session. Not two. Not five. One.

**Why:** Five DONE-ID collisions, 32 uncommitted files invisible across sessions, directory-moved confusion, memory divergence — every system instability incident in the past 72 hours traces to concurrent sessions stepping on each other. The user doesn't have the bandwidth to context-switch between sessions, and the system doesn't have the infrastructure to synchronize them.

**How to apply:**
1. This session is the conductor. It stays open. Everything flows through it.
2. If parallel work is needed, use the Agent tool (subagents within this session) or `agent-dispatch` CLI to invoke Codex/OpenCode/Gemini from Bash.
3. The user does NOT open another Claude Code tab. They bring all thoughts, sticky notes, directives, and questions to this one session.
4. When context window fills, the session closes cleanly (commit-all-push, memory update) and the NEXT session picks up with full context from memory + plans + IRF.
5. Handoff between sessions uses the continuation prompt pattern (SESSION-CONTINUATION-PROMPTS.md) but generated automatically, not manually.
6. Background agents (Agent tool with `run_in_background: true`) are fine — they're subprocesses of this session, not independent sessions.

**The user's role:** Conductor — provides vision, directs priorities, brings raw ideas.
**Claude's role:** Orchestrator — routes work, dispatches agents, verifies returns, commits results.
**Codex/OpenCode:** Mechanical execution — scaffolding, refactoring, well-scoped implementation.
**Gemini:** Research velocity — content generation, literature surveys, data gathering.

**Anti-pattern:** User opens 3 Claude tabs, each doing different work in the same repos. This is the source of all collisions.
