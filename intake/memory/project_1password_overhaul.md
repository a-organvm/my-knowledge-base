---
name: 1Password shell integration overhaul
description: Tiered secret management (Tier 2 cached, Tier 3 lazy) — fixed op inject bug, gh plugin, GH_TOKEN validation (2026-03-13 to 2026-03-18)
type: project
---

1Password shell integration overhauled 2026-03-13, with follow-up GH_TOKEN fix on 2026-03-18.

**Why:** `op inject --in-file <(...)` was broken in background subshells on macOS zsh — process substitution fd gets closed. Cache at `~/.cache/op-secrets` had empty values for all 4 secrets. Each failed `op read` call produced verbose "No accounts configured" errors.

**How to apply:**
- Tier 2 (cached): GITHUB_TOKEN + GEMINI_API_KEY — cached at `~/.cache/op-secrets` (mode 600) with 60-minute TTL, background refresh
- Tier 3 (lazy): NPM_TOKEN + SONATYPE_GUIDE_TOKEN — on-demand via `npm-with-token` and `sonatype-with-token` wrapper functions, never touch disk
- Fix: Uses `mktemp` file instead of process substitution for `op inject --in-file`
- Cache validation: rejects files with empty values (`grep -q '=$'`)
- Single `op whoami` auth guard — zero `op` calls if not authenticated
- `gh` uses 1Password shell plugin for biometric auth (`op plugin init gh`)
- Aliases: GH_TOKEN, GITHUB_MCP_PAT, GITHUB_PERSONAL_ACCESS_TOKEN all set from GITHUB_TOKEN; GOOGLE_API_KEY from GEMINI_API_KEY

**Files modified:**
- `~/.config/op/secrets.zsh` — rewritten (tiered, mktemp fix)
- `~/.config/op/plugins.zsh` — created (sources `~/.op/plugins.sh`)
- `~/.config/zsh/20-tools.zsh` — added plugins.zsh sourcing

**GH_TOKEN issue (2026-03-18):** After overhaul, GH_TOKEN env var was set to an invalid/stale token that blocked `gh` CLI. Required `unset GH_TOKEN` to let gh fall back to its own auth. Fixed by ensuring cache refresh produces valid tokens.
