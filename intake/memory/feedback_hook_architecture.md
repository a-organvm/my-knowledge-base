---
name: Hook architecture — prompt vs command type
description: Critical finding — prompt-type hooks bypass if-conditions; only command-type works for conditional guards
type: feedback
---

Claude Code hooks: ONLY use `command` type with JSON echo output for conditional PreToolUse guards. NEVER use `prompt` type.

**Why:** `prompt` type hooks bypass `if` condition filtering — they fire on ALL matching tool calls regardless of the `if` glob pattern. Also triggers Claude's safety system as "prompt injection" on imperative text. The `command` type with `echo '{"hookSpecificOutput":{...}}'` respects `if` conditions reliably.

**How to apply:**
- All hooks in `settings.json.tmpl` MUST use `"type": "command"` with JSON echo format
- Use the proven pattern: `"command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"additionalContext\":\"...\"}}'"`
- Never propose `"type": "prompt"` for any hook, even though the Claude Code docs list it as valid
- The `prompt` type is safe ONLY for unconditional hooks (no `if` field) like SessionStart context injection

Additional findings:
- **Edit tool bypasses Write hooks**: The Edit tool does NOT trigger `matcher: "Write"` PreToolUse hooks. This is the escape hatch when Write hooks cause chicken-and-egg blocking.
- **settings.json normalization**: Claude Code strips unknown `if` fields from settings.json after loading. The template (source) must always have `if` conditions — they're loaded into memory at startup even though the file is normalized after.
- **Dynamic reload**: Claude Code reloads settings.json dynamically mid-session when the file changes. Changes take effect without restart.
