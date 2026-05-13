---
name: resolve-bootstrap script + dead-path cleanup
description: Built the missing companion to resolve-audit; pruned 103 dead workspace path entries from .claude.json + codex config.toml
type: project
originSessionId: 5a485c0a-8c2d-4af3-a88c-63d09aca2467
---
**What:** `resolve-bootstrap` — the previously-missing companion script that the resolve-audit hook directive ("connect to resolve-bootstrap instead") was asking for. Re-runnable Python tool that scans deployed configs for project entries pointing to nonexistent dirs, writes timestamped backups, then prunes them.

**Where:**
- Script: `~/.local/bin/resolve-bootstrap` (chezmoi source: `dot_local/bin/executable_resolve-bootstrap`)
- Chezmoi commit: `85ad1bc` (4444J99/domus-semper-palingenesis#master)
- Companion script lives next to it: `~/.local/bin/resolve-audit`

**State:** shipped 2026-04-25. Both ran end-to-end:
- `.claude.json`: 106 → 22 project entries (84 dead pruned)
- `codex config.toml`: 19 dead `[projects."..."]` sections pruned
- Backups: `~/.claude.json.bak.<TS>` + `~/.local/share/codex/config.toml.bak.<TS>`

**Usage:**
- `resolve-bootstrap` — dry-run report (default; exits 1 if any dead entries)
- `resolve-bootstrap --apply` — prune with backup
- `resolve-bootstrap --json` — machine-readable output (combine with --apply)

**What's still flagged (20 audit hits, all LIVE paths):**
The remaining audit violations are *literal hardcoded workspace paths* in the deployed configs — the architectural ideal is paths-via-resolver (env var, registry lookup), but `.claude.json` and codex use literal directory paths as keys to look up project state. Truly resolving these requires a deeper change to how Claude/codex find their projects (out of scope for the bootstrap pruner).

**Open follow-up (D1.5, not done):**
The audit-resolver gap: literal path hits will keep firing in the session-start hook even after pruning, because LIVE workspace paths look identical to the regex. Either:
- Update `resolve-audit` to distinguish dead-vs-live and only flag dead, OR
- Build a resolver layer that lets configs reference paths via logical names + lookup table (bigger arch change)

**Why:** Session-start hook had been firing with "20 hardcoded path violations" for unknown number of sessions. Audit script had `head -10` so the actual scope (84+19 dead) was hidden. User said "do it" 2026-04-25; pruner built and run; cleanup complete; remaining hits are architectural rather than cleanup-able.
