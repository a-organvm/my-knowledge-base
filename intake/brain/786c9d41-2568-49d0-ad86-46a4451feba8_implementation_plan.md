# Implementation Plan: Phase 4 Growth & Optimization (2026-03-04)

## Goal Description
Following the successful Evaluation-to-Growth phase, where scripts were migrated and the narrative was made more accessible, the portfolio is ready for the "Growth" stage. This plan focuses on ensuring perfect Applicant Tracking System (ATS) extraction for resumes, Productizing the custom `quality-ratchet-kit`, and laying the groundwork for the "Logos" content strategy by creating an essay publishing architecture.

## Proposed Changes

### ATS Optimization for Generated PDFs
Applicant Tracking Systems require clean, sequentially logical text. The current Playwright-generated PDFs include UI elements (like the "Switch Persona" button or "Live Engineering Vitals" header) *before* the applicant's name, which can confuse ATS parsers.

#### [MODIFY] `src/styles/global.css` (or `src/layouts/ResumeLayout.astro` if scoped)
- Introduce a strict `@media print { .no-print { display: none !important; } }` utility class.
- Apply this `.no-print` class to UI controls (theme toggles, "Switch Persona" headers, "Print PDF" buttons).
- Ensure the structural DOM flow starts cleanly with the Name and Professional Summary in the printed version.

### Productize `@4444j99/quality-ratchet-kit`
The bespoke quality infrastructure is robust enough to be a standalone, flagship open-source project.

#### [NEW] `packages/quality-ratchet-kit/README.md`
- Write comprehensive documentation detailing the "Quality Ratchet" methodology, how to configure the policies (`ratchet-policy.json`), and how to use the CLI binaries (`check-bundle-budgets`, `verify-quality-contracts`, etc.).
#### [MODIFY] `packages/quality-ratchet-kit/package.json`
- Polish the metadata (author, repository links, keywords) to prepare it for a theoretical or actual npm publish.

### Expand "Logos" Content Strategy
To leverage the insights from the "Operative Handbook", we need a dedicated section for long-form essays and architectural deep dives.

#### [NEW] `src/content/config.ts` (if not already using Content Collections)
- Define an `essays` or `logos` collection schema using Astro's highly type-safe `defineCollection`.
#### [NEW] `src/pages/logos/index.astro` and `src/pages/logos/[slug].astro`
- Create the index and dynamic routing pages for writing and publishing essays directly in the portfolio, transforming the "Eight-Organ System" documentation into valuable public content.

## Verification Plan

### Automated Tests
- Run `npm run test` and `npm run quality:local` to ensure no build processes break.
- For the `quality-ratchet-kit` changes, ensure `npm run test:quality-ratchet-kit` still passes.

### Manual Verification
1. **ATS Extraction Test:** Run `npm run build:resume` and then use `pdftotext public/resume/Anthony_James_Padavano_Systems_Architect.pdf - | head -n 30` to verify that the first lines extracted are the applicant's name and contact information, not UI buttons.
2. **Logos Inspection:** Run `npm run dev` and navigate to `/portfolio/logos/` to verify the new essay layout renders correctly with a placeholder markdown post.
