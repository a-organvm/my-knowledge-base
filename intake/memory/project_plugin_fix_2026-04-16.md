---
name: Claude Code plugin marketplace fix 2026-04-16
description: Diagnosed and fixed 4 plugin load failures; discovered hooks regression; identified chezmoi persistence vacuum
type: project
---

## Plugin marketplace restored (2026-04-16)

**Root cause:** `~/.claude/plugins/marketplaces/claude-plugins-official/` directory was absent — the git clone had silently failed (SSH). Claude Code reported all `@claude-plugins-official` plugins as "not found."

**Fix applied:**
- Cloned `git@github.com:anthropics/claude-plugins-official.git` → `~/.claude/plugins/marketplaces/claude-plugins-official/`
- Removed `superpowers@claude-plugins-official` from `settings.json` `enabledPlugins` — plugin was removed from the marketplace upstream
- Restored `if` conditions to PreToolUse hooks in `settings.json` — a linter/formatter had stripped them, causing ALL Bash calls to trigger all 3 outbound preflight messages instead of only `gh pr comment *`, `gh issue comment *`, `gh pr review *`

**Why:** Marketplace uses SSH git source; SSH clone can fail silently in background daemon contexts.

**How to apply:** If plugin errors recur, first check `ls ~/.claude/plugins/marketplaces/claude-plugins-official/` — if absent, re-clone. If `if` fields disappear from hooks again, restore them manually (the schema validator strips unknown fields).

## Persistence vacuum — PARTIALLY RESOLVED

**Correction (2026-04-17):** `private_dot_claude/` DOES exist in the chezmoi source at `~/Workspace/4444J99/domus-semper-palingenesis/private_dot_claude/`. It contains `CLAUDE.md.tmpl`, `settings.json.tmpl`, hooks, plans, projects, scripts, templates, and `README.md`. The original claim that "private_dot_claude does not exist" was wrong — it referenced the deployment artifact path (`~/domus-semper-palingenesis/`) instead of the chezmoi source path.

**Remaining gap:** `~/.claude/projects/*/memory/` files are NOT chezmoi-tracked. Memory parity for these files depends on the session archival system, not chezmoi.
