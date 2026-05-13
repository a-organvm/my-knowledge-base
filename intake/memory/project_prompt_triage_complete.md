---
name: Prompt triage + priority stratification 2026-04-22
description: 24,599 atoms triaged, 6-dimension priority engine built, 2,012 duplicates consolidated — 14,898 OPEN
type: project
originSessionId: 119e98b1-bd3e-4993-bbd6-74464dc8c746
---
## What Was Done

On 2026-04-22, the prompt triage pipeline was built and run to completion, then the priority stratification layer was added and aggressive closures were corrected. On continuation (same day), 2,012 duplicate atoms were consolidated via similarity engine:
- 24,599 atoms across 10 months of sessions (Nov 2025 - April 2026)
- DONE: 6,361 (25.9%) — evidence-verified
- OPEN: 14,898 (60.6%) — priority-scored P0-P3
- ARCHIVED: 2,012 (8.2%) — duplicates consolidated to canonical atoms
- 140MB of generated JSON (.gitignored — regenerable from pipeline)
- OPEN went 977 → 2,596 → 13,771 → 16,910 → 14,898 after evidence verification + dedup
- Every DONE atom has recorded evidence (git/IRF/GitHub/file/hook/memory)
- Priority engine: 6 dimensions (recency, type urgency, universe criticality, content specificity, cross-reference density, completion trajectory)
- Closure rule: nothing closed without triple-check; single-heuristic closures are forbidden

## Infrastructure Built

6 new scripts at organvm-corpvs-testamentvm/data/prompt-registry/:
- triage_non_actionable.py, deep_triage.py, finish_triage.py
- apply_triage_results.py, generate_work_queue.py, route_atoms.py

measure_implementation.py expanded from 5 to 7 evidence sources.
Session-start hook reads from open-atoms-cache.json, shows top 15 OPEN atoms.

## Pipeline Refresh

```bash
cd ~/Workspace/meta-organvm/organvm-corpvs-testamentvm/data/prompt-registry
python3 extract_all_prompts.py && python3 atomize_prompts.py
python3 triage_non_actionable.py && python3 measure_implementation.py
python3 deep_triage.py && python3 generate_work_queue.py && python3 route_atoms.py
```

## Dispatch Routing (977 OPEN atoms)