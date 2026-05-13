---
name: Prompt atomization pipeline
description: Full 3-layer prompt extraction pipeline built 2026-04-23; 47K unified atoms across 5 sources
type: project
originSessionId: 15f36576-2dae-4cf8-b0fc-dda1dcebcfe3
---
Complete prompt atomization pipeline built in single session (2026-04-23):

| Component | Script | Output | Count |
|-----------|--------|--------|-------|
| L1 extraction | extract_prompt_atoms.py | prompt-atoms.jsonl | 11,980 |
| L1b short recovery | (inline) | prompt-atoms-short.jsonl | 2,557 |
| L2 decomposition | decompose_prompts.py | sub-prompt-atoms.jsonl | 16,488 |
| L3 status inference | infer_prompt_status.py | (updates prompt-atoms) | 87% DONE |
| Trajectories | trajectory_engine.py | intention-trajectories.jsonl | 113 |
| Merge | merge_atom_stores.py | unified-atoms.jsonl | 47,299 |
| Open backlog | analyze_open_prompts.py | open-prompt-backlog.jsonl | 918 |

Status distribution: DONE 87.2%, OPEN 3.9%, PARTIAL 3.7%, DEFERRED 3.7%, FAILED 1.4%

Scripts at: ~/Workspace/organvm/my-knowledge-base/scripts/
Data at: ~/Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/
JSONL data files are gitignored (regenerable via scripts).

**Why:** This is the user's complete intention history — every prompt across 5 AI platforms, decomposed into sub-tasks, status-inferred, and clustered into persistent intention trajectories.

**How to apply:** When the user asks about backlog, priorities, or "what haven't I done yet" — the open-prompt-backlog.jsonl has 918 unfulfilled items (52 P0, 191 P1). The unified-atoms.jsonl is the master index. Trajectory analysis shows recurring themes and their evolution over 3.5 years.
