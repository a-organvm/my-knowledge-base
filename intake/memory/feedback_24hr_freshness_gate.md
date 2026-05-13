---
name: 24-hour job freshness gate
description: NEVER build materials or apply to jobs older than 24 hours — user has asked for this repeatedly and it keeps being violated
type: feedback
originSessionId: 98e6abc9-e524-43f7-90b0-0b9a84a4b6d7
---
Jobs must be posted within the last 24 hours before any materials are built, cover letters written, or applications submitted. No exceptions.

**Why:** The user has requested this rule multiple times ("iron and stone"). Applying to stale postings wastes energy that should go to fresh, high-signal opportunities. The pipeline was designed to enforce this but the rule keeps being bypassed by sessions that don't check posting dates first.

**How to apply:** Before ANY application pipeline work — scoring, tailoring, cover letter writing, advancing — check the `posting_date` field in the pipeline YAML. If `(today - posting_date) > 1 day`, STOP. Do not build materials. Source fresh jobs instead via `source_jobs.py` or manual search.
