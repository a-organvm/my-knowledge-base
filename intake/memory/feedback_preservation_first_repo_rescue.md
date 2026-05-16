---
name: Preservation-first rescue for poisoned local git checkouts
description: When a repo's .git metadata is unwritable or provenance-poisoned, pivot to clean-clone replay and prove no unique data loss before replacing anything
type: feedback
originSessionId: codex-2026-05-16-ai-agent-workload-review
---
When a local checkout's `.git` becomes unwritable (`index.lock: Operation not permitted`, `com.apple.provenance`, or similar), do **not** treat the broken checkout as the only path forward and do **not** start handing the human repetitive shell commands as the primary plan.

**Correct move:** preserve the working tree, route around the poisoned metadata, and prove equivalence before any replacement talk.

**Why:** "Nothing local only" includes stranded working trees. A poisoned `.git` is a routing failure, not permission to abandon the work or push the operational burden back to the human.

**How to apply:**
- Verify the live state from disk; do not trust handoff summaries
- Separate independent workstreams before replaying them; do not collapse them into one rescue commit if the history can stay atomic
- Validate the changed content in the broken checkout first
- Clone a clean copy from remote into a new path
- Replay the verified changes into the clean clone
- Commit and push from the clean clone
- Diff the broken checkout against the rescue clone excluding `.git` and generated caches such as `__pycache__`
- State explicitly whether any unique non-generated data remains stranded
- Only after equivalence is proven may you propose replacing the broken local checkout
- Even then: move or rename aside first, and keep the old tree until the human explicitly authorizes deletion

**Communication constraints:**
- Do not say "the user must run X" until you have exhausted system-executable rescue paths
- Do not present stale relay claims as current state; verify on disk
- Do not imply deletion or removal when the user's governing concern is preservation
- When unique data is preserved, say that plainly

**Applied case (2026-05-16):**
- `a-i--skills` had an OS-poisoned `.git` that rejected both agent-run and human-run `git add`, and even direct `xattr -dr` attempts failed
- The correct recovery was a clean clone rescue, not more xattr ritual
- Replay produced two separate commits:
  - `2e3fedb` `feat(plugins): fold coliseum-from-grain and pentaphase-structural-architect into marketplace`
  - `89b85e4` `feat(closeout): add CLAUDE.md autogen freshness gate`
- Tree comparison proved the broken checkout and rescue clone were identical except for `.git` internals and `__pycache__`
- Therefore no unique source data was lost, and remote parity was restored before any local-replacement discussion
