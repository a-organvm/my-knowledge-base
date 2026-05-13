---
name: MCP secrets hardened via chezmoi modify script
description: GitHub PAT and Neon API key moved from plaintext .claude.json to 1Password-backed env vars resolved at chezmoi apply time (2026-04-13)
type: project
---

MCP server secrets in `~/.claude.json` are now managed by `modify_dot_claude.json.tmpl`, not manually pasted.

**Why:** GitHub PAT (`ghp_Ttup...`) and Neon API key (`napi_m25w...`) were stored as plaintext literals in `.claude.json`, visible to any user-space process and potentially committed to git via chezmoi autoCommit.

**How to apply:**
- `modify_dot_claude.json.tmpl` reads `GITHUB_PERSONAL_ACCESS_TOKEN` (from `gh auth token` via `secrets.zsh`) and `NEON_API_KEY` (from 1Password via `secrets.zsh` cache) at chezmoi apply time
- GitHub PAT sourced fresh from `gh auth token` — never static
- Neon key in 1Password at `op://Personal/Neon API Key/credential` — rotated 2026-04-13
- If env vars are missing, those server configs are skipped (guard: `if gh_token:` / `if neon_key:`)
- The modify script also manages `conductor` and `voice-scorer` MCP servers

**Previously remaining vacuums (both resolved 2026-04-14):**
- ~~IRF-DOM-029: Voice-scorer non-functional~~ → confirmed working (IRF description was stale, reconciliation sprint 2026-04-14)
- ~~IRF-DOM-030: Conductor untested~~ → mcp 1.27.0 installed in venv, connectivity verified (reconciliation sprint 2026-04-14)
