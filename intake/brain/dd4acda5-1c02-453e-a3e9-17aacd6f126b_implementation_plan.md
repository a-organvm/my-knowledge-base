# Implementation Plan: Stakeholder Portal Evaluation-to-Growth Evolution

*Note: The full Evaluation-to-Growth analysis is saved at `~/.gemini/plans/2026-03-05-evaluation-to-growth.md` inside the project root.*

## Goal Description
Enhance the stakeholder portal's architecture and user experience based on the Evaluation-to-Growth audit. We will unify the Python ingestion script into the native TypeScript queue system, upgrade the UI to a premium glassmorphic aesthetic to combat the "clinical" feel, and harden the database indexing (HNSW) for scale.

## Proposed Changes

### Backend Ingestion Unification
We will migrate parsing and manifestation out of Python and into Next.js internal jobs to unify the stack.

#### [NEW] [ingest-worker.ts](file:///Users/4jp/Workspace/meta-organvm/stakeholder-portal/src/lib/ingestion/ingest-worker.ts)
- Create a TypeScript-native worker that reads repositories, parses Markdown/HTML, and chunks them using `langchain/text_splitter`.
- Have this worker push embeddings to PgVector directly via Drizzle ORM, deprecating the external Python script.

#### [MODIFY] [schema.ts](file:///Users/4jp/Workspace/meta-organvm/stakeholder-portal/src/lib/db/schema.ts)
- Ensure the `embeddings` table schema supports explicit index generation if it doesn't already.

#### [NEW] [0007_add_hnsw_index.ts](file:///Users/4jp/Workspace/meta-organvm/stakeholder-portal/src/lib/db/migrations/0007_add_hnsw_index.ts)
- Generate a new migration file containing: `CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);` for `pgvector` scale hardening.

### UI & Aesthetics
We will add "Pathos" by upgrading the UI to a dynamic, premium theme.

#### [MODIFY] [tailwind.config.ts](file:///Users/4jp/Workspace/meta-organvm/stakeholder-portal/tailwind.config.ts)
- Add custom colors (deep darks, vibrant accents) and utilities for glassmorphism/backdrop-blur.

#### [MODIFY] [layout.tsx](file:///Users/4jp/Workspace/meta-organvm/stakeholder-portal/src/app/layout.tsx)
- Apply the new premium dark-mode background globally.
- Inject a "global sync state" footer or header that informs the user when the AI's knowledge was last updated.

#### [MODIFY] [ChatInterface.tsx](file:///Users/4jp/Workspace/meta-organvm/stakeholder-portal/src/components/ChatInterface.tsx)
- Embed "Suggested Prompts" to alleviate stakeholder prompt-paralysis.

## Verification Plan

### Automated Tests
- Run `npm run test` to execute the existing test suite: `retrieval.test.ts`, `docs-connector.test.ts`, etc., ensuring the new HNSW index and TS-ingestion don't perform regressions.
- Specifically verify context truncation holds up under the new ingestion strategy.

### Manual Verification
- View `npm run dev` in the browser to manually inspect the new premium glassmorphic UI and confirm that "Suggested Prompts" accurately auto-fill into the chat box.
- Inspect the Dashboard/Layout to confirm "Last Sync State" is visible and drawing from the DB.
