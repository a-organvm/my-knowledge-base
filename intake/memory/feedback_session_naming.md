---
name: Session names must be descriptive
description: Claude Code auto-generated session slugs (random word combos) are useless — name sessions by what they DO
type: feedback
originSessionId: c2d0301b-443e-40b1-b70c-8af43c205a1b
---
Auto-generated session names like "elegant-tinkering-summit", "shiny-moseying-wren", "noble-beaming-allen" are meaningless. Sessions must be named by their actual content: "plugin-marketplace-fix", "hook-enforcement-phase3", "cpu-throttling-cce", "domain-architecture-design".

**Why:** The user operates 10+ concurrent sessions. Random word combos make it impossible to identify which session did what. When exporting, archiving, or resuming sessions, the name IS the index. A useless name breaks the entire retrieval chain.

**How to apply:**
- When exporting sessions via `organvm session export`, always provide a descriptive `--slug` that reflects the session's actual work
- When creating plan files, use descriptive slugs in the filename, not the auto-generated session name
- If Claude Code generates a random session name, note the descriptive name in the session's first response so it can be found later
- Advocate for configurable session naming in Claude Code settings if possible
