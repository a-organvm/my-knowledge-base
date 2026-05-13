# Stakeholder Portal Completion Task List

## Core Objective: "Alpha to Omega" Completion
Address all seven identified gaps to move the project from a solid backend to a cohesive, production-ready product.

### Phase 1: Planning & Infrastructure (Gaps 1, 4, 5)
- [x] **Gap 4: Environment Variable Audit & Validation**
    - [x] Create `scripts/validate-env.ts` to check required vars.
    - [x] Update `.env.example` with any missing production-critical vars.
- [x] **Gap 1: Deployment & Build Verification**
    - [x] Run `npm run build` locally and fix any build errors.
    - [x] Verify manifest validation passes.
- [x] **Gap 5: Database & Migrations**
    - [x] Run `npx drizzle-kit generate` to sync schema.
    - [x] Run `npx drizzle-kit migrate` (or document the process for production).
    - [x] Verify seeding process via `seed.yaml` (Implemented `seed-db.ts`).

---

### Phase 2: Pipeline & Backend (Gaps 3, 6)
- [x] **Gap 3: Manifest Pipeline Restoration**
    - [x] Recover or re-implement `scripts/generate-manifest.py` (Integrated into `ingest-worker.ts`)
    - [x] Ensure `manifest.json` generation is part of the ingestion flow.
- [x] **Gap 6: Ingestion Engine Finalization**
    - [x] Commit untracked changes in `src/lib/ingestion/`
    - [x] Finalize the refactor in `src/lib/ingestion/ingest-worker.ts`
    - [x] Ensure integration with the manifest pipeline.

---

### Phase 3: Frontend Integration (Gaps 2, 7)
- [x] **Gap 2 & 7: UI Integration (The Ask Page)**
    - [x] Extract CSS tokens from prototype
    - [x] Refactor `ChatInterface.tsx` for premium look
    - [x] Refactor `EvidencePanel.tsx`
    - [x] Integrate "Last Synced" state indicator.

---

### Phase 4: Finalization & Commit
- [x] **Stage & Commit All Changes**
    - [x] Group commits logically (Infrastructure, Backend, UI).
    - [x] Ensure all untracked files are accounted for.
- [x] **Final Project Walkthrough**
    - [x] Verify end-to-end functionality (Ingestion -> Retrieval -> UI).
    - [x] Perform manual UI/UX audit.
