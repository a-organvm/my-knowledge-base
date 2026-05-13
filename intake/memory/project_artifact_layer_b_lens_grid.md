---
name: Layer B — Lens-grid (spatial TUI)
description: Spec for multi-lens domain sketch in terminal; classifications.jsonl + lens YAMLs + TUI renderer with disagreement panel; SPEC-ONLY, slice 1 unbuilt.
type: project
originSessionId: f3beab49-8440-4336-b4db-299e2933f5a1
---
**What**: Three-layer architecture for terminal-based domain sketch:
- L1 — `classifications.jsonl` sidecar (compute-once, append-only) per atom
- L2 — Lens YAMLs (status-5, predicate, hanging, weight, density, etc.) — open registry
- L3 — Renderers: statusline (1 lens, 1 line), tmux pane (3 lenses), full TUI `dm sketch` (N lenses + disagreement panel)

The disagreement panel surfaces atoms whose glyph differs across loaded lenses — these ARE the metaversal indeterminacy made visible.

**Where**:
- Plan: `2026-04-27-domain-sketch-lens-grid-terminal.md` (chezmoi 1e7e9d4)
- Target build: `~/Workspace/organvm/my-knowledge-base/scripts/classify.py` (NEW) + `scripts/sketch.py` (NEW, ~400 lines using `rich`) + `lenses/*.yaml` (NEW, 6 to start) + `~/.local/bin/dm-sketch` (NEW shim)

**Project**: `organvm/my-knowledge-base` + `organvm-corpvs-testamentvm`

**For whom**: User — terminal sessions surface what's open / hanging / in-flight spatially

**State**: SPEC. Slice 1 unbuilt.

**Pending feedback**:
- Lens-set default (all 6 vs curated 3 "morning" preset)
- Atom kinds in scope (prompt + plan atoms only vs include commits/IRF/memories/issues)
- TUI library: rich (default, faster) vs textual (full async, mouse, animation)

**Next action**: Slice 1.1 — `classify.py` v1 over existing classifications (status, predicate, hanging, weight). Slice 1.2 — 6 lens YAMLs + TUI renderer with `rich`. Disagreement panel as Slice 3.
