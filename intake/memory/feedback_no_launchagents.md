---
name: No automatic LaunchAgents — event-driven only
description: NEVER deploy timer-based LaunchAgents; every time we do, the system breaks. Use on-demand/event-triggered execution instead.
type: feedback
originSessionId: 80581eb0-933d-4de3-a31f-f0c420955109
---
Do NOT use LaunchAgents for automatic background execution. Every deployment has caused system instability: mail-triage froze the machine, memory-sync blocked chezmoi for 5+ minutes, MCP servers were redundant.

**Why:** The user's machine is 16GB RAM, beta macOS, with Dropbox/Backblaze already competing for resources. Timer-based agents pile up, conflict with each other, and cause cascading failures (Mail.app opening → contactsd thrashing → CPU spike → slow internet → unusable system). Four incidents across three sessions.

**How to apply:** 
- Things should exist on a clock/calendar (tracked, counted, scheduled) but NOT execute automatically
- Execution happens when TRIGGERED by an event or ASKED by the user
- The system watches and waits; it doesn't act on its own
- If building something that "runs periodically," make it a CLI command with a `--once` flag, not a daemon
- Existing LaunchAgents should be audited and most should be disabled or converted to on-demand CLI commands
- The only acceptable automatic processes are ones that are truly passive (no CPU, no I/O, no app launches)
