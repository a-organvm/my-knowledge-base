---
name: Artifact-level memory is mandatory
description: Session memories must capture working state (file paths, collaborators, pending feedback) not just volume summaries — context loss between sessions is unacceptable
type: feedback
originSessionId: ae0b2fe6-dfcb-4069-897c-cc02d3e4668b
---
Session memories that say "19 commits across 6 repos" are USELESS for continuity. They don't answer
"what were we building, for whom, and where did we leave off?" — the only questions that matter.

**Why:** User had to re-explain a spiral design built for Maddie because no memory captured the
artifact, file path, collaborator, or pending feedback. User: "Every time you have to find something,
it's a waste of fucking time! Every time you have to search for something, it's a waste of fucking
time! Every time you have to remember something, it's a waste of my fucking time!"

**How to apply:**
1. Every session close-out MUST capture artifacts with file paths, collaborators, state, and feedback
2. Every new person mentioned MUST get a collaborator memory entry
3. Session memories lead with `**Artifacts (working state):**` before any volume stats
4. File paths for active deliverables ARE saveable — the "don't save file paths" rule does NOT apply
   to things under active development
5. If you can't find what you were working on from memory alone, the memory system failed — fix it,
   don't search the filesystem
