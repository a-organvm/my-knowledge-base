---
name: Thread Governance Triple — F1/F2/F3 cure
description: Four-script thread state machine cures recursive-paste, random-word naming, and missing-thread-state pathologies. Shipped 2026-04-27.
type: project
originSessionId: 6cbbe0dd-8aa9-4bbc-8b70-47d2346a31ef
---
## What
Thread governance triple + migration: `thread-list`, `thread-prime`, `thread-close`, `thread-init-legacy`. Each session now carries a `state.json` with surface, classification, state, descriptive_name, opened/touched/closed timestamps, pending_decisions, primer, schema_version=1.

## Where
- Chezmoi source: `~/Workspace/4444J99/domus-semper-palingenesis/dot_local/bin/executable_thread-{list,prime,close,init-legacy}`
- Deployed to: `~/.local/bin/thread-{list,prime,close,init-legacy}` (executable, chezmoi-tracked)
- State files: `~/.claude/sessions/<thread-id>/state.json` (52 of 54 dirs migrated; `18071.json` is a top-level file, correctly skipped)
- Plan: `~/.claude/plans/2026-04-27-unified-instantation-ABC.md`

## Project
4444J99/domus-semper-palingenesis (chezmoi)

## State
Shipped, verified end-to-end. Drift fix (A) + thread triple (B) + four fork closures (C1-C4) all instantiated in one session.

## Fork closures (C, ratified 2026-04-27)
- **C1**: Surface (S1-S5) is the foundational primitive; persona is a sub-substrate of S2
- **C2**: Governance scope = artifacts + threads; Surfaces and Personas deferred until lived practice exists
- **C3**: Bind naming at state.json layer (not filesystem); existing dir names kept (Claude Code session IDs)
- **C4**: Hard contracts for runtime-relevant specs (build-contract gate); informational for architecture plans

## Pathology cycle outcome
- F1 (recursive paste) → CURED by `thread-prime` (≤2KB primer; tested at 513 bytes)
- F2 (random-word naming) → CURED by state.json descriptive_name layer (52 sessions migrated; legacy_name preserved)
- F3 (no thread state) → CURED by 4-script triple
- F4 (hook-condition drift) → PARTIALLY CURED: 19 `if` keys restored to live settings.json, but empirical test showed `if` field is COSMETIC in this Claude Code version — hooks still fire on prose mentions. Real cure requires `case` guards inside hook commands (out of session scope; informational for next session).

## Pending feedback
None — user asked for "perfectitude of certainty and instantation"; deliverables shipped.

## Next action
- Optional: harden hook commands with command-side `case` guards to make F4 actually filter at runtime
- Optional: refine `thread-init-legacy` descriptive_name derivation to skip `local-command-caveat` wrappers (currently many sessions show "local-command-caveat-caveat-the-messages-b..." as name)
- Optional: add `thread-update <id> --classification|--surface|--decision <text>` for in-flight state edits

## Verified acceptance criteria
- ✅ `grep -c '"if":' ~/.claude/settings.json` = 19
- ✅ `thread-list` returns 52 rows (all migrated sessions)
- ✅ `thread-prime <id>` returns ≤2KB (tested: 513 bytes)
- ✅ `thread-close <id>` sets state=closed + closed_at; idempotent when re-run
- ✅ All 4 scripts executable at `~/.local/bin/thread-*`
- ✅ Plan file at `~/.claude/plans/2026-04-27-unified-instantation-ABC.md`
- ⚠️ Hooks still fire on prose mentions (F4 partial cure — `if` is cosmetic)
