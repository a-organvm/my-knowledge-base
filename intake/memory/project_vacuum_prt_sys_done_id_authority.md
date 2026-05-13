---
name: VACUUM — PRT/SYS/DONE ID authority is undefined
description: PRT-/SYS-/DONE- IDs used throughout memory and plans return zero matches in fossil-record.json; the authority store for these IDs is undiscovered or undefined
type: project
originSessionId: 0d4fd2e1-02de-4c24-b0bc-90a55b5cc292
---
# VACUUM: PRT/SYS/DONE ID Authority Undefined

**Surfaced**: 2026-04-25 during relay verification audit (`~/.claude/plans/2026-04-25-relay-verification-achilles-handoff.md`).

**The claim**: Memory ledger and plans reference IDs like `PRT-048`, `SYS-156`, `DONE-447`, `DONE-455` as if they belong to a triple-referenced tracking system (per universal rule #23 *"every entity exists in 3+ locations: IRF, repo, GH issue"*).

**The reality**: `grep -h -o "PRT-[0-9]*\|SYS-[0-9]*\|DONE-[0-9]*" /Users/4jp/Workspace/a-organvm/fossil-record.json` returns **0 matches**. The fossil-record file exists but does not store these IDs in this format.

**Why:** Without a discoverable authority store, the IDs function as labels-without-referent. Memory entries cite PRT-048 as "designed not built" — but there is no canonical place to look up what PRT-048 actually is, who opened it, when, or what its full state machine looks like. Identity-by-convergence (rule #23) is broken when one of the convergence points is missing.

**How to apply:** Achilles session must determine before doing IRF hygiene work:
1. Where do PRT-/SYS-/DONE- IDs live as their authority record? Candidates:
   - Distributed across per-repo IRF files (search needed)
   - In `meta-organvm/praxis-perpetua/library/` somewhere (121 active SOPs there)
   - In a different `*.json` ledger not yet located
   - In GitHub issues with a labeling convention (which org? all orgs?)
   - **Or**: there is no authority store, and these IDs are memory-only artifacts that need a real ledger built
2. If no authority store exists, build one (atomize as system-priority work — this blocks rule #23 compliance).
3. Until resolved, treat all PRT-/SYS-/DONE- IDs in memory as **memory-only** — they are not yet triple-referenced.

**Severity**: High for system integrity (rule #23 violation pattern), medium for near-term execution. The Achilles plan's Tier 1 #4 ("IRF hygiene — 12 PRT items") cannot proceed cleanly until the authority is located or declared.

**Investigation start**:
```sh
# Distributed IRF search
find ~/Workspace -maxdepth 4 -name "irf*.json" -o -name "fossil*.json" -o -name "ledger*.json" 2>/dev/null
grep -rln "PRT-04[0-9]" ~/Workspace/meta-organvm ~/Workspace/a-organvm 2>/dev/null | head
gh search issues "PRT-048" --owner 4444J99 --owner ORG-PERSONAL 2>&1 | head
```
