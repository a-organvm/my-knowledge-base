---
name: Parallel execution is the protocol
description: NEVER do mechanical work sequentially when agents can run in parallel — dispatch Codex/Gemini/subagents simultaneously
type: feedback
originSessionId: 119e98b1-bd3e-4993-bbd6-74464dc8c746
---
Parallel execution is the default mode, not sequential. When multiple independent tasks exist, dispatch them simultaneously to available agents (Codex, Gemini, OpenCode, Copilot, Claude subagents).

**Why:** The user has Codex, Gemini, OpenCode, and Copilot available as dispatch targets. Sequential execution on mechanical tasks wastes the user's time and violates the force-multiplication principle. The system exists so one person operates at institutional scale — that requires parallel execution.

**How to apply:** Before starting any work, identify ALL independent tasks. Dispatch mechanical/tactical work to agents in parallel. Use Claude subagents for research tasks that can run simultaneously. Never hand-test or iterate sequentially on work that can be batched or parallelized. The question is always: "what else should be running right now?"
