---
name: Root cause, not symptoms — never backwards-engineer
description: Never patch symptoms; find and fix the root cause in the engine/pipeline/source. Band-aids on outputs are system failures.
type: feedback
originSessionId: e87291f8-2c4d-4c83-ae9c-f06770fece85
---
We do not backwards-engineer anything. When something arises, find the root cause.

**Why:** Patching symptoms (reopening atoms, adding verification layers, boosting scores) creates technical debt. The real fix is in the engine that produced the wrong output. Examples from this session:
- DONE atoms without evidence → root cause: measure_implementation.py doesn't record evidence sources
- Aggressive closures needing reopening → root cause: deep_triage.py uses single-heuristic closure
- 431 copies of the same directive → root cause: no deduplication/merge step in the atomization pipeline

**How to apply:** Before writing a fix, ask: "what engine produced the wrong output?" Fix THAT engine. If you're writing a script that corrects another script's output, you're backwards-engineering. Fix the source script instead.
