---
name: Where the user's prompts actually live
description: Primary prompt sources by volume and importance — terminal CLIs are the main work surface
type: reference
originSessionId: c2d0301b-443e-40b1-b70c-8af43c205a1b
---
**Primary work surface (terminal CLIs):**
- Claude Code CLI — `~/.claude/projects/*/` JSONL files (EXTRACTED, 5,032 prompts)
- Codex CLI — `~/.codex/history.jsonl` + `~/.codex/archived_sessions/` (EXTRACTED, 1,595 prompts)
- Gemini CLI — needs investigation, likely `~/.gemini/` or similar
- Copilot CLI — needs investigation, likely `~/.github-copilot/` or similar

**Secondary work surface (desktop apps):**
- ChatGPT app — export at `~/Workspace/meta-organvm/intake/data-2026-02-16-00-20-00-batch-0000/conversations.json` (EXTRACTED, 925 prompts, through Feb 2026). Newer conversations need fresh export.
- Claude Desktop app — `~/Library/Application Support/Claude/` has conversation data (NOT YET EXTRACTED)

**Earlier work (lower priority):**
- Gemini app/web — used for rapid app building before terminal workflow. 51 conversations decoded from Chrome Safe Storage but not persisted. Get to eventually.

**Also captured:**
- Specstory (Cursor IDE) — 78 prompts (EXTRACTED)
- Corpus site markdowns — 504 prompts (EXTRACTED)
- Shell history — 36 prompts (EXTRACTED)
