---
name: Session close-out discipline
description: User enforces strict session hygiene — commit-all-push, 10-index propagation, N/A=vacuum, memory parity
type: feedback
originSessionId: ae0b2fe6-dfcb-4069-897c-cc02d3e4668b
---
The user has strong expectations for session close-out and governance rigor:

**1. commit[all] push[origin]** — Every modified file must be committed and pushed before session close. No dirty state, no unpushed commits. Check all repos touched in the session.

**2. 10-index propagation is mandatory** — After completing work, check ALL 10 governance indices: registry, IRF, omega, testament, concordance, memory parity, git, plans, session memory, seed.yaml. Default is check-all-10 and skip inapplicable, not check-none.

**3. N/A is a vacuum** — "all the N/As suggest something imperative; it means there is a vacuum where something should be." Never mark something N/A without investigating. If a governance surface has no entry, that's a gap to research, plan, and log.

**4. [(local):(remote)={1:1}]** — Memory parity is existential. If the physical machine dies, the soul (remote backup) must persist. Every Claude memory file must be chezmoi-tracked with autoCommit+autoPush.

**5. Proceed with all you can** — When external blockers exist (billing, human action, dashboard access), fix everything programmatic and note the external items. Don't let external blockers hold up internal progress.

**Why:** User operates a single-operator system where data loss is catastrophic and governance drift compounds silently. The discipline prevents "it worked but nobody updated the records" syndrome.

**6. Working state capture comes FIRST** — Before the 10-index check, capture artifacts (file paths, collaborators, state, pending feedback) and people. This is what makes the next session start warm instead of cold. Volume stats ("19 commits") are secondary to "what we built, where it is, who it's for, and what's pending." See `feedback_artifact_level_memory.md`.

**How to apply:** At session end: (1) capture working state — artifacts with paths and people with context, (2) run the 10-index check, (3) if any surface is dirty fix it, (4) if any surface has N/As log the vacuum, (5) commit and push everything, (6) save session memory with artifacts section first.
