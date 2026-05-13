---
name: Session archival system
description: Per-project conversation preservation system built 2026-04-15 — organvm session archive + LaunchAgent automation
type: project
---

Built a full session archival pipeline (2026-04-15) that routes AI conversations to their project repos automatically.

**Components:**
- `organvm session archive` CLI command (organvm-engine `session/archive.py`, 280 lines)
- LaunchAgent `com.4jp.session-archive` — 30-min timer + run-at-login
- `domus sessions sync/status` subcommands
- `.archive-state.json` per-project for idempotent processing

**Per-session output** at `<project>/.claude/sessions/YYYY-MM-DD--<slug>/`:
- `transcript.md` — dialogue (summary mode, filtered tool output)
- `prompts.md` — human prompts only, numbered and timestamped
- `review.md` — 5-phase review scaffold
- `meta.json` — machine-readable metadata
- `session.jsonl` — raw canonical data
- `subagents/` — parallel agent data if present

**Why:** IRF-DOM-029 — session transcripts were local-only at ~/.claude/projects/. If machine dies, all institutional memory lost. Now archived to project repos (git-tracked).

**How to apply:** The LaunchAgent handles everything automatically. `domus sessions sync` for manual trigger. `organvm session archive --dry-run` to preview. Raw .jsonl excluded from git via `.gitignore` patterns (large files).

**Also in this session:** gcloud CLOUDSDK_PYTHON pinned to python3.13, lazy-load path fixed to /opt/homebrew/share/google-cloud-sdk, VSCode extensions dir managed, chezmoi memory conflict resolved.
