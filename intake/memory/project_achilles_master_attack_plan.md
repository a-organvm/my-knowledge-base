---
name: Achilles master attack and victory plan
description: Additive master plan for the Achilles lane; corrects SYS-156 into humans-waiting plus a 1,433-failure CI surface, keeps PRT-048 first, and sequences the real path to closure
type: project
---
# Achilles Master Attack and Victory

**What:** The executable master plan for the Achilles lane requested by the
user after relay verification. This is the "do the work in the right order"
artifact, not another summary relay.

**Where:**
- Live: `~/.claude/plans/2026-04-25-achilles-master-attack-and-victory.md`
- Chezmoi source: `~/Workspace/4444J99/domus-semper-palingenesis/private_dot_claude/plans/2026-04-25-achilles-master-attack-and-victory.md`
- Project copy: `~/Workspace/4444J99/domus-semper-palingenesis/.claude/plans/2026-04-25-achilles-master-attack-and-victory.md`

**Project:** cross-cutting Achilles lane rooted in dotfiles governance, but
touching `a-i--skills`, GitHub notification/CI surfaces, and `a-organvm`.

**State:** written 2026-04-25 as the additive successor to the earlier
Achilles workload compile. Historical v1 remains valid as a record; this file
is the corrected execution order.

**Corrections captured:**
- PRT-048 still comes first and is still unbuilt.
- SYS-156 is not one thing:
  - humans-waiting queue
  - cascading CI failure surface
- The old "~890 failures / 14 repos" scope is retired as unsourced.
- The CI relay's corrected scope is 1,433 unread CI failures out of 1,449
  unread notifications, with 540 from dotfiles alone.
- Bulk-archive is suspended until root causes are fixed.

**Attack order:**
1. Re-open the five Achilles source artifacts.
2. Build PRT-048 in `a-i--skills`.
3. Split SYS-156 into humans-waiting and CI-failure work.
4. Attack dotfiles CI first, then the remaining high-volume repos.
5. Perform IRF hygiene only after the battlefield is legible.
6. Design the multi-lens viewer as its own artifact.

**Victory definition:**
- Minimum: PRT-048 scaffold exists, one dotfiles CI run is root-caused, and
  the humans-waiting queue is reduced to a precise user packet.
- Session: PRT-048 shipped, dotfiles CI fixed or narrowed to a real blocker,
  and the authority gap is actively handled.
- Campaign: top CI repos reduced, authority path established, multi-lens plan
  written, artifacts committed and pushed.

**Pending feedback:** none. The plan is autonomous and ready to execute when
the Achilles lane opens.

**Why:** The previous relay stack proved correctness, but still left the work
as scattered audits. This file converts those audits into an actual attack
sequence.
