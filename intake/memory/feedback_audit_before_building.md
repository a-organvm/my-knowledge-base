---
name: Audit existing state before building new structure
description: Always check what already exists (Gmail labels, LaunchAgents, dotdirs) before creating new patterns — Triage/* labels cost more to fix than the original build
type: feedback
originSessionId: caa53287-9125-4617-ae4f-43e9056d902d
---
Always audit existing system state before introducing new structure. In the mail-triage session (2026-04-21), Triage/* Gmail labels were created without checking that a 66-label taxonomy (Marketing/Newsletter, Dev/GitHub, Finance/Banking, etc.) already existed. The fix — moving 141 messages back, rewriting routing, verifying IMAP path resolution — cost more than the original implementation.

**Why:** The user's system has accumulated years of structure. New automation must integrate with what exists, not create parallel hierarchies. The cost of auditing is always less than the cost of unwinding.

**How to apply:** Before creating ANY new label, folder, mailbox, LaunchAgent, or config structure: enumerate what exists first. `osascript`, `launchctl list`, `ls`, `chezmoi status` — the tools exist. Use them. The pattern is: audit → classify → extend. Never: assume → create → discover → fix.
