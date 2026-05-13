---
name: All streams require separating
description: Every distinct stream of work, output, commit, hook, agent, or memory must occupy its own channel — never bundle distinct streams into a single artifact
type: feedback
originSessionId: 1fa11d69-285a-4b7d-ab24-106fb873d179
---
All streams require separating.

**Why:** Bundled commits, conflated output, multi-purpose hooks, merged agent logs, and combined memory writes destroy traceability and collapse provenance. Each stream has its own lifecycle, audit trail, and revert vector; merging them means a defect in one taints the others and you cannot bisect, revert, or attribute. The recurring failure mode is the cargo-train commit / the multi-purpose hook / the bundled handoff — each looks efficient, each destroys recoverability. Codified 2026-04-27 after commit 57533f9 bundled G1 + thread substrate + F2/F3 commit-hygiene fix as one freight.

**How to apply:**
- **Commits**: Each G-series cure (G1, G2, G3, ...) ships as its own commit — never bundled with another Gx or with substrate work or with cleanup. One concern per commit.
- **Substrate primitives**: Each primitive (thread-list, thread-prime, thread-close, thread-init-legacy) is its own stream — separate file, separate commit, separate review.
- **Hooks**: PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, Stop are independent channels — never share command bodies. If a hook needs to react across phases, write distinct handlers per phase.
- **Agents**: Claude, Codex, Gemini, OpenCode, Cursor outputs each go to their own log/memory/session path — never merge into a single combined transcript.
- **Memory**: auto-memory, plan files, IRF rows, atom backlog, conductor handoffs each have their own write path — never collapse one write into another.
- **Pick-one menus are stream-conflation symptoms**: When tempted to ask "G3 first or G4 first?" — that's the cargo-train asking which car to load. Answer: ship all in logic order, each as its own separated stream.
- **Output**: When reporting work, separate the insight stream from the action stream from the status stream from the next-step stream. Don't braid them.
- **Bundled "packs" are anti-patterns**: A "thread-governance pack" or "session-close-out bundle" is the symptom. Each artifact ships individually with its own provenance.
