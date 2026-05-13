---
name: No conversation loss to compression
description: Exported sessions MUST contain full prompt chains — compacted conversations are unacceptable artifacts
type: feedback
originSessionId: c2d0301b-443e-40b1-b70c-8af43c205a1b
---
Conversations are not disposable. Every prompt, every response, every tool call must be recoverable. When Claude Code compacts a conversation and the user exports it, the exported .txt captures only the post-compaction state — losing all early prompts. This is unacceptable.

**Why:** The user builds systems from conversation history. Prompts are operational artifacts, not ephemeral chat. Losing them to compression defeats the purpose of session exports. The user's exact words: "WE DO NOT HAVE CONVERSATIONS FOR MY FUCKING HEALTH--there must be FULL AND ENTIRE CONVERSATIONS."

**How to apply:**
- Before exporting a session, check if it's been compacted. If so, warn the user that the export will be incomplete.
- Always look for alternative full-conversation sources: JSONL session files, `organvm session transcript <id> --unabridged`, Claude Code local storage.
- When reviewing exported sessions, flag which ones are incomplete due to compaction rather than presenting partial data as complete.
- Never treat compacted exports as authoritative records of what the user said.
