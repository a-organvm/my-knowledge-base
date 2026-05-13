---
name: Use the agent fleet — Claude fires them, user doesn't
description: Claude controls Codex/Gemini/OpenCode via agent-dispatch CLI; user should never have to fire agents manually
type: feedback
originSessionId: 119e98b1-bd3e-4993-bbd6-74464dc8c746
---
Claude fires the agents. The user does not. When the user says "use the agents," they mean Claude should dispatch work via `agent-dispatch codex|gemini|opencode` — not generate commands for the user to run.

**Why:** The user said explicitly: "I'm not firing anything. I want you to control the whole thing, but use the fucking agents." The dispatch CLI (`agent-dispatch`) is available at `~/.local/bin/agent-dispatch`. Claude can invoke it via Bash.

**How to apply:**
- For mechanical work (file creation, boilerplate, config generation): `agent-dispatch codex --dir <repo> "prompt"`
- For research/content velocity: `agent-dispatch gemini --dir <repo> "prompt"`
- For infrastructure/refactoring: `agent-dispatch opencode --dir <repo> "prompt"`
- Monitor system load before dispatching (16GB RAM constraint)
- Verify agent output after completion
- Maximum 2 external agents simultaneously (RAM constraint)
