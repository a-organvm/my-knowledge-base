---
name: Universal job sourcing — not curated lists
description: Job pipeline must source from universal databases, not a hardcoded list of 91 companies — user has given this rule 10+ times
type: feedback
originSessionId: 98e6abc9-e524-43f7-90b0-0b9a84a4b6d7
---
The application pipeline's `source_jobs.py` currently pulls from 91 manually configured Greenhouse/Ashby/Lever boards. This is wrong. The user wants UNIVERSAL sourcing — any job that matches their skills, from any company, anywhere.

**Why:** The user cannot afford to limit their search to companies they already know about. The curated list creates a ceiling on discovery. Every session that presents jobs from the 91-company list without also running broad sourcing is violating this instruction. The user has stated this rule ~10 times across sessions and it keeps not being implemented.

**How to apply:**
1. Always run `--jobspy` (python-jobspy) for broad Indeed/LinkedIn/Glassdoor scraping in addition to the curated ATS boards
2. The 24-hour freshness gate still applies to ALL sources
3. Score everything through the existing rubric — don't filter by company name, filter by fit score
4. If `--jobspy` is broken or missing, that's a P0 bug to fix, not a reason to fall back to the 91-company list
5. The ideal: a single command that searches everywhere, scores everything, and surfaces the top matches posted in the last 24 hours
