---
name: Triple-check before closing atoms
description: Nothing gets closed without triple verification; single-heuristic closures are forbidden; the triage pipeline was too aggressive
type: feedback
originSessionId: e87291f8-2c4d-4c83-ae9c-f06770fece85
---
Nothing gets closed without triple checking. The triage pipeline closed 15,289 atoms on single heuristics (age, universe completion rate, content pattern) — reopening audit found 1,616 should have stayed OPEN.

**Why:** Single-point-of-failure closures create invisible debt. The CLOSED-INFERRED heuristic (universe >75% done → assume atom is done) was 100% wrong at P1+ priority — 723 high-priority atoms dismissed by a weak statistical inference. CLOSED-CONTEXT was 47% wrong (425 of 906 contained actionable work).

**How to apply:**
- DONE requires evidence from at least 2 sources (git + IRF, or git + GitHub, etc.)
- CLOSED requires the content to be genuinely non-actionable AND non-generative (can't produce vacuum atoms)
- Never close based on age alone, universe completion alone, or content pattern alone
- The measurement engine's multi-evidence approach (7 sources) is the right rigor — extend it to closures

**Addendum 2026-04-28 (closure-card repo verification):**
For any closure card listing commits across multiple repos: resolve each repo to absolute path via `find ~/Workspace -maxdepth 3 -name <repo> -type d` *before* declaring missing. Verify each SHA via `git -C <abs-path> cat-file -t <sha>`. A single failed `cd` is NOT evidence of fabrication — it is a search failure. The phantom-audit pass on 2026-04-28 declared 3/4 repos non-existent because it searched `~/Workspace/<repo>` instead of `~/Workspace/organvm/<repo>`; all 8 commits were real. Bold-and-fast verification loses to careful-and-complete.
