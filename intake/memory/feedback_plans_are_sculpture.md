---
name: Plans are sculpture — never delete, never overwrite
description: Hard rule — plan files are sediment in a lineage. Removing one erases the negative space that shaped the next. No exceptions.
type: feedback
originSessionId: e4d7bfeb-8e46-4516-9f37-84e1c754a1cd
---
Plans are never deleted. Every plan is sediment in a sculpture; the act of removing one erases the negative space that shaped the next. Even superseded plans, abandoned plans, plans that turned out to be wrong — they are part of the lineage and must persist on disk.

**Why:** the user said this verbatim 2026-04-25 ("No plan should be deleted. Every plan is the shaping of clay, the scraping of a sculpture"). It is the same rule family as universal #3 (rules additive — every rule accumulates) and #8 (plans are artifacts — commit and push). This memory extends that rule specifically to plan files: deletion is never the right operation. The discovery surfacing this rule was that `~/.claude/plans/we-all-work-in-atomic-map.md` had been deleted while the v1 archive remained — which broke the lineage. The fix was restoration from the archive, not acceptance of the deletion.

**How to apply:**
- Never run `rm`, `mv` (out of plans/), or overwrite on any file under `~/.claude/plans/`, `<project>/.claude/plans/`, or any other plans directory.
- If superseding a plan, write a new dated/v-suffixed file (`YYYY-MM-DD-{slug}-v2.md`, `-v3.md`, etc.) — never modify the prior in place.
- If retiring a plan, move it into `plans/archive/YYYY-MM/` rather than deleting it.
- If you find a plan source missing while the v1 (or other versioned) archive exists: restore the source from the archive. Treat the missing source as data loss that requires recovery, not as an intentional state.
- Plans you wrote yourself in plan mode follow the same rule — once written, they cannot be deleted by you in a later session. Add new plans; don't subtract old ones.
- Audits: periodically `find ~/.claude/plans -type f -name '*.md' | sort` and confirm any `-v[0-9]+` archive has a corresponding non-suffixed source (or that the source was deliberately moved into `archive/`).

**Edge case** — agent sub-plans (`-agent-{id}.md` suffix): these are also plans. Preserve them on the same rule. They are part of the lineage of how the parent plan was decomposed.
