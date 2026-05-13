# Implementation Plan

## Goal Description
Fix the currently failing test suite, fill out stubs in metrics generation, and ensure the PDF resumes generated have proper plain-text extraction for ATS scanners as requested in the evaluation-to-growth report.

## Proposed Changes

### Tests and Metrics

#### [MODIFY] `src/data/__tests__/data-integrity.test.ts`
- Update the `system-metrics.json` assertions to match the new upstream schema.
  - Remove expectations for `code_substance`, `flagship_vivification`, `praxis_targets`.
  - Add expectations for `omega`, `essays`, `sprints`, `github_issues`, `adrs`, `schemas`, `ci_workflows`, `automated_tests`, `documentation_words`.

#### [MODIFY] `scripts/generate-system-data.py`
- Update `compute_vitals()` to correctly extract metrics that have been moved to the top-level of the upstream `system-metrics.json` object.
- Currently it looks for a `"manual"` key which no longer exists, causing `vitals.json` to have zeros and failing the data-integrity tests. For example, changing `m.get("automated_tests", ...)` to `canonical.get("automated_tests", ...)`, and setting reasonable static defaults or computing `code_files`/`test_files` if they are omitted entirely.

### PDF Resume ATS Extraction

#### [MODIFY] `scripts/generate-resume-pdfs.mjs`
- Update the Playwright `page.pdf()` call to properly supply `tagged: true` (which enhances ATS extraction of logic and text reading order).
- This fulfills the "Audit PDF Resumes" step in the evaluation report to guarantee better ATS plain-text parsing.

## Verification Plan

### Automated Tests
- Run `npm run test` to ensure `data-integrity.test.ts` passes and the overall suite is green.
- Run `npm run test:quality-ratchet-kit` to ensure no skeletons or stubs remain broken in the package kit.
- Run `npm run build:resume` and test ATS output.

### Manual Verification
- Manually run `pdftotext` or `cat` on the output PDFs to verify logical content flow for ATS readability.
