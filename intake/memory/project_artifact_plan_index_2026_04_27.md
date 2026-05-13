---
name: Plans INDEX.md built (drift closure)
description: Generated /Users/4jp/.claude/plans/INDEX.md from 299 disk plans, added single MEMORY.md pointer to honor 200-line cap
type: project
originSessionId: 81389e44-295f-4cd8-bf0c-0092ee30d5c5
---
**What:** Closed plan-index drift named in case-wide deep dive §V.1. Drift was worse than estimated: 299 plans on disk vs. 4 entries indexed by `plans/` pattern in MEMORY.md.

**Where:**
- Index file: `/Users/4jp/.claude/plans/INDEX.md` (43KB; 299 entries; date-sorted newest-first; markdown table with file link + first-heading title)
- MEMORY.md pointer: single line under new `## Plans Index` section (above `## User`)

**Project:** /Users/4jp/.claude/ (cross-cutting persistence layer)

**State:** shipped 2026-04-27

**Approach:** Generative — Python one-liner walks `~/.claude/plans/*.md`, extracts first non-frontmatter heading, sorts by date prefix (filename) falling back to mtime. INDEX.md is regenerable; do not hand-edit.

**Why this shape:** MEMORY.md has hard 200-line truncation (per auto-memory system reminder). Dumping 299 pointers there would self-destruct. External INDEX with single-pointer entry honors the cap and keeps the catalog complete.

**Regeneration:** Re-run the inline Python from `what-s-logically-next-extensibly-eager-giraffe.md` Stream B-6 path. Should be wrapped into a `~/.local/bin/plans-index` script later if drift recurs.

**Pending:** `~/.claude/projects/-Users-4jp/memory/project_*.md` files also have a similar drift pattern (memory directory likely exceeds MEMORY.md indexed entries). Same fix pattern would apply.
