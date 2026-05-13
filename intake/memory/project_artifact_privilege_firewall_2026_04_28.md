---
name: Privilege firewall doc 2026-04-28
description: Operational firewall guarding ORGANVM/chezmoi/skills against case content from active litigation; trigger conditions for post-litigation Micah pitch
type: project
originSessionId: 2d8e6d78-e5b0-4f97-9ccb-6dedc0d1feba
---
**What:** Operational privilege firewall — declares 5 categories (SAFE/UNSAFE/GREY), auto-deny patterns, chezmoi exclusion list, pre-commit hook design, trigger conditions for post-litigation Micah pitch.

**Where:** `~/Workspace/organvm/organvm-corpvs-testamentvm/docs/privilege-firewall.md`

**Project:** ORGANVM — judicial substrate (load-bearing for everything that follows)

**For whom:** Anthony's own substrate discipline; eventual credibility proof for post-trigger Micah pitch (Praxis Curia)

**State:** Shipped 2026-04-28 (T1 deliverable from going-through-a-lawsuit plan)

**Pending feedback:** None — operational immediately

**Next action:**
1. Build pre-commit hook at `~/Workspace/4444J99/domus-semper-palingenesis/.chezmoiscripts/pre-commit-privilege-scan.sh` (W4 deliverable)
2. Create blocklist at `~/Library/PrivilegeAuditDB/blocklist.txt` (chmod 600, OUTSIDE chezmoi) with case-specific terms
3. Run audit: `grep -rE -f blocklist.txt ~/.claude/ ~/Workspace/organvm/ ~/Workspace/4444J99/ ~/Workspace/a-i--skills/`

**Trigger conditions for post-litigation pitch:** First to occur of (a) settlement signed and on public docket, (b) case dismissed/judgment entered AND any appeal window closed, (c) Micah explicitly invites the conversation in writing.

**Cross-references:**
- CURIA Phase 0 spec: `~/.claude/plans/2026-04-28-curia-organ-viii-specification.md`
- Plan: `~/.claude/plans/going-through-a-lawsuit-fizzy-moth.md`
- Collaborator boundary: `collaborator_micah_PRIVILEGE_BOUNDARY.md`
- LaunchAgent rule: `feedback_no_launchagents.md` (HARD; pre-commit hook is on-demand only, NOT LaunchAgent)
