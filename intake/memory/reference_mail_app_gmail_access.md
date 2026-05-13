---
name: Gmail access — Mail.app vs Gmail MCP tradeoffs
description: Mail.app osascript freezes machine on 16GB/Tahoe; Gmail MCP tools preferred for both reads and writes; Mail.app only as last resort
type: reference
originSessionId: eb876139-2eb0-4c33-a815-2ce4abdb2467
---
**UPDATED 2026-04-21:** The Mail.app osascript approach caused machine freezes when run via LaunchAgent (30-min timer). On 16GB RAM + macOS Tahoe beta, Mail.app is too heavy for background automation.

**Current recommendation:**
- **Gmail MCP tools** (`mcp__claude_ai_Gmail__*`) for both reads and writes — search_threads, get_thread, create_draft, list_labels
- **Gmail server-side filters** for automated triage — no local process needed
- **Mail.app via osascript** only as manual, interactive last resort (not in automation)

**Why the change:** LaunchAgent `com.4jp.mail-triage.plist` was disabled 2026-04-21 after repeatedly freezing the machine. The ideal form of email triage is server-side (Gmail filters/labels), not client-side polling.

**How to apply:**
- Gmail account: `padavano.anthony@gmail.com`
- For inbox scanning: `mcp__claude_ai_Gmail__search_threads` with query syntax
- For reading: `mcp__claude_ai_Gmail__get_thread`
- For automated classification: create Gmail filters (server-side, zero local cost)
- Do NOT create LaunchAgents that open Mail.app
