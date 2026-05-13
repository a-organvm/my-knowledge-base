---
name: Rule of three — every capability needs three paths
description: Nothing should depend on a single tool/path; always have 3 ways to accomplish any task; fail over silently, don't surface tool failures to user
type: feedback
originSessionId: eb876139-2eb0-4c33-a815-2ce4abdb2467
---
Every capability must have three independent paths. If one fails, use the next. Never present a tool failure as a blocker to the user.

**Why:** The user explicitly called out the anti-pattern of asking "should I use X?" when X might not work. The system should try X, fail over to Y, then Z, and only escalate when ALL THREE are exhausted. Single-path dependencies are fragile. Asking the user to choose between tools is offloading the system's job onto the human.

**How to apply:**
- Before starting any task, identify at least 3 paths to accomplish it
- Try path 1 silently. If it fails, try path 2. Then path 3.
- Only surface to user after all paths exhausted — and then present the problem, not "which tool should I use?"
- For Gmail specifically: (1) Gmail MCP tools, (2) Gmail API via Python/curl, (3) Mail.app osascript as last resort
- This applies universally: file reads (Read tool / cat / Grep), web access (WebFetch / Chrome MCP / curl), git ops (local git / gh CLI / GitHub MCP)
- "Rule of three" is a universal architectural principle — applies to infrastructure, tool selection, error handling, everything
