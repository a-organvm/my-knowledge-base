---
name: Micah Longo — privilege boundary
description: Hard rule — no case content from active litigation enters any shipped artifact; categories of forbidden encoding listed
type: feedback
originSessionId: 2d8e6d78-e5b0-4f97-9ccb-6dedc0d1feba
---
**Rule:** No content from the active litigation (Anthony Padavano + opposing parties) or any communication with attorney Micah Longo about that case may be encoded into any saved memory, plan, skill, repo, or shipped artifact. Ever.

**Why:** Attorney-client privilege protects strategy, communications, and work product. Encoding case content into substrate would (a) waive privilege if substrate ever becomes discoverable, (b) contaminate the legal-domain skill so it cannot be honestly productized, (c) conflate the fiduciary relationship with future commercial relationships, and (d) damage trust with Micah pre-pitch. This boundary is the credibility proof for any future Praxis Curia conversation.

**How to apply:**

### Forbidden encoding categories
1. Specific case facts (claims, parties, dates, locations, witnesses, exhibits, docket numbers)
2. Legal strategy (theory of liability, affirmative defenses, motion strategy, settlement posture)
3. Privileged communications (anything Micah said in counsel; anything Anthony said to Micah seeking counsel)
4. Attorney work product (drafts, research notes, internal analysis prepared by or for counsel)
5. Settlement positions (figures, terms, timing, willingness markers)
6. Opposing-party data (their counsel, their strategy, their disclosures)
7. Discovery materials (any document produced or received in discovery)
8. Deposition content (testimony, exhibits, transcripts)
9. Court filings that are not yet on the public docket
10. Even paraphrased versions of any of the above

### Permitted (with care)
- Generic legal-practice patterns that exist in 2+ public sources independently AND are not attributed to Micah
- Public-source citations (FRCP, ABA model rules, public bar opinions, academic legal scholarship, public reporters)
- The fact that Anthony has worked with Micah (already in public memory)
- Observations about Micah's professional cadence/rhetorical mode (encoded only in `collaborator_micah.md` — *the shape of working*, not *what was said*)

### When in doubt
- **Cut.**
- Default decision: forbidden until proven safe by (a) finding 2+ public sources for the pattern, (b) confirming non-attribution.
- If a pattern only makes sense because of this case, it is contaminated and must be cut.

### Trigger to relax (partially)
First to occur of:
- Settlement signed and on the public docket
- Case dismissed or judgment entered AND any appeal window closed
- Micah explicitly invites the conversation in writing

Even after trigger: case-specific content remains forbidden. Only the *substrate-discipline* observations (i.e., "I ran a privilege firewall and it worked") become pitchable. Substantive case content stays sealed indefinitely.

### Audit
On-demand command (NOT a LaunchAgent — per `feedback_no_launchagents.md` HARD rule):

```bash
grep -rE -f ~/Library/PrivilegeAuditDB/blocklist.txt \
  ~/.claude/ \
  ~/Workspace/organvm/ \
  ~/Workspace/4444J99/domus-semper-palingenesis/ \
  ~/Workspace/a-i--skills/
```

Zero hits expected. Any hit = HARD BLOCK incident; quarantine artifact, audit recent commits, rotate firewall.

## Cross-references

- Privilege firewall (operational): `~/Workspace/organvm/organvm-corpvs-testamentvm/docs/privilege-firewall.md`
- Collaborator memory (paired): `collaborator_micah.md`
- Plan: `~/.claude/plans/going-through-a-lawsuit-fizzy-moth.md`
- LaunchAgent rule: `feedback_no_launchagents.md`
