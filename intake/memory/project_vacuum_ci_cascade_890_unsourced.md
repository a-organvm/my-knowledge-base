---
name: VACUUM — 890 CI failures number is upstream-unsourced
description: The "~890 CI failures across 14 repos" number cited in the Achilles workload + close-out audit has no traceable upstream tracking ledger; must be re-derived before any cascade work
type: project
originSessionId: 0d4fd2e1-02de-4c24-b0bc-90a55b5cc292
---
# VACUUM: 890 CI-Failures Number Has No Authority

**Surfaced**: 2026-04-25 during relay verification audit (`~/.claude/plans/2026-04-25-relay-verification-achilles-handoff.md`).

**The claim**: Achilles workload Tier 1 #3 cites *"CI cascade — ~890 failures, 14 repos"*. Close-out audit (`i-need-you-to-merry-thimble.md` line 184) tags this as *"NOT DONE / not tracked / no commits, no PRT"*.

**Why:** Both downstream documents reference the number without naming the source. No fossil-record entry. No PRT ID. No `gh run list` snapshot persisted to disk. The number is claim-without-receipt — which means any cascade work driven by it would be operating on undocumented scope.

**How to apply:** Before treating "890 CI failures" as actionable scope in any future session:
1. Re-derive via `gh run list --json conclusion,workflowName,name,headBranch,event,databaseId --limit 200` across the 14 repos (which 14? also undocumented — first sub-vacuum).
2. Persist the snapshot (timestamp, repo, count, status) to a tracked location — fossil-record.json or a dedicated `ci-cascade-snapshot-YYYY-MM-DD.json`.
3. Only then treat the number as load-bearing.

**Sub-vacuum**: The "14 repos" is also unsourced. Achilles needs to enumerate the candidate set first (likely the GRADUATED-tier ORGANVM repos but unverified).

**Severity**: Medium. Not blocking near-term work, but the relay's recommended Tier 1 includes CI cascade as #3 priority and a dispatch candidate. Acting on an unsourced number wastes Codex/OpenCode tokens.
