---
name: Dotfiles sprawl audit — Phase 0 + Docker/Codex cleanup DONE
description: 2026-04-17 audit — 40+ dotdirs catalogued; Phase 0 DONE; Docker/Codex cruft cleaned 2026-04-23; just check-all fully green; password rotation still OPEN (BACKLOG-001)
type: project
originSessionId: caa53287-9125-4617-ae4f-43e9056d902d
---
Full HOME root audit performed 2026-04-17. Plan at `~/.claude/plans/eager-baking-steele.md`.

## SECURITY — Phase 0 COMPLETE (files deleted)

Seven compromised/artifact files deleted from HOME: `fetch_recent_gmail.py`, `search_gmail_extended.py`, `extract_work_tasks.py`, `recent_emails.json`, `work_emails_range.json`, `job_search_extended_results.txt`, `gmail-ops.zip`. Empty `.gmail-mcp/` directory also deleted.

**STILL OPEN (BACKLOG-001):** Gmail app password `dxmz yydz pbmo shjk` needs revocation in Google Account Security. Not blocking mail-triage (uses osascript, not IMAP), but the credential is burned.

## Dotdir Disposition (40+ dirs)

- **25 already XDG-symlinked** (working correctly)
- **3 XDG base dirs** (.cache, .config, .local — correct)
- **2 chezmoi-tracked** (.claude, .ssh)
- **1 need XDG-symlink** (.thumbnails — questionable on macOS, empty dirs) — NOT YET DONE
- **.npm** added to XDG symlink array (2026-04-21)
- **15 tool-managed** (add to .chezmoiignore) — NOT YET DONE
- **1 deleted** (.gmail-mcp — done 2026-04-21)

## LaunchAgent Status — CLEANED (2026-04-21)

Orphaned `com.user.gmail_labeler` and `com.user.mail_automation` templates deleted from chezmoi source. Replaced by `com.4jp.mail-triage` (active, 30-min cadence). `.chezmoiignore` suppressions removed. Loader script updated.

## XDG Symlink Cleanup — 2026-04-21

6 dead apps removed from ensure-xdg-symlinks array (blender_ext, claude-server-commander, codex, dropbox_bi, mcp-auth, playwright-mcp). `npm` added. Dead symlinks cleaned via run_once script. 14GB `_agents/` cache deleted. Stale `~/domus-semper-palingenesis/` removed.

Memory-sync daemon (`domus-memory-sync`) was blocking chezmoi for 5+ mins — rewritten with batch `chezmoi add`, `LAST_SYNC` timestamp, and pgrep guard.

## MCP Docker→Native Conversion — 2026-04-20

Docker-based MCP servers converted to native Homebrew installs. `github-mcp-server` installed via `brew install`. 8 MCP config files updated across Claude Code, Claude Desktop, Cursor, Continue, OpenCode, Gemini, Codex. Two LaunchAgents removed from chezmoi source: `com.4jp.mcp.servers.plist.tmpl`, `com.4jp.env.mcp.plist.tmpl`. Docker UNINSTALLED entirely (17GB freed, 2026-04-18).

## Docker/Codex Dead Symlink Cleanup — 2026-04-23

`symlink_dot_codex` and `symlink_dot_docker` deleted from source tree. `DOCKER_CONFIG` and `MACHINE_STORAGE_PATH` env vars removed from 15-env.zsh.tmpl. `docker-cleanup` alias removed from 30-aliases.zsh. Test assertion updated. Plist validation tests now skip when no templates exist. ShellCheck warnings in agent-dispatch resolved. 9 scripts fixed for missing +x. justfile permission check excludes `__pycache__/`. CLAUDE.md task queue and LaunchAgents table updated. `just check-all` fully green (251 BATS + 128 pytest). DONE-422. 8 commits pushed.

**How to apply:** Phase 0 done. MCP native conversion done. Docker/Codex cleanup done. Phase 2 (.thumbnails XDG-symlink, 15 dotdirs to .chezmoiignore) is queued but not blocking.
