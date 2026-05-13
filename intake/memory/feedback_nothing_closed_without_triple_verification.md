---
name: Nothing closed without triple verification by Claude, never by agents
description: NEVER mark anything as closed/done/superseded/abandoned — only the human closes; Claude can suggest after triple-checking but agents cannot close
type: feedback
originSessionId: 15f36576-2dae-4cf8-b0fc-dda1dcebcfe3
---
NEVER close, supersede, abandon, or mark done ANY atom, prompt, task, or intention. The human closes. Period.

**Why:** The user has corrected this 4+ times in a single session (2026-04-23). Every time the system auto-classified things as "done" or "closed," it was wrong. "The AI responded" ≠ done. "A file exists" ≠ the ideal form. "Similar prompt" ≠ same intention. "Wrong repo" ≠ irrelevant. Each prompt is a facet of an ideal form — only the human knows if the form has materialized.

**How to apply:** 
- Auto-triage results are CONTEXT, not verdicts
- Agent outputs are REPORTS, not closures
- Status changes require triple verification BY CLAUDE (not sub-agents), and even then are SUGGESTIONS to the human
- The correct status for everything is NEEDS_REVIEW until the human says otherwise
- Sub-agents should NEVER write status changes to review-results.db — they report findings, Claude synthesizes, human decides
