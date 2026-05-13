# Phase 1b & Phase 4 Implementation Plan

This plan outlines the final phases for the Hermeneus Contextual Awareness epic, covering knowledge federation and external research linkage to achieve glorious exhaustive completionist certainty.

## Proposed Changes

### Federation Connector (Phase 1b)
Provide integration with the atomic `my-knowledge-base` API to surface personal research and decisions alongside institutional knowledge.

#### [NEW] `src/lib/knowledge-base-connector.ts`
- Create a federated search client.
- When `process.env.MY_KNOWLEDGE_BASE_ENABLED === "true"`, this client will execute a GET request to `${process.env.MY_KNOWLEDGE_BASE_API_URL}/search/hybrid?q=${query}`.
- Map the incoming `AtomicUnit` JSON array into the normalized `RetrievalSource` interface, tagging them with `source_type: "knowledge_base"`.
- Implement a strict timeout (e.g., 2000ms) and fallback-to-empty to prevent the portal from hanging if the local knowledge base server is offline.

#### [MODIFY] `src/lib/hybrid-retrieval.ts`
- Import the new federated search client.
- Inside the main `searchCorpus` or within `buildTier1Context`, execute the federated search in `Promise.all` alongside the local Postgres `cosineDistance` vector search.
- Concat the arrays, sort by relevance, and take the top N.

### External Research Linkage (Phase 4)
Ensure that URL citations and external references placed in workspace repositories (e.g., `research/` folders) are queryable by the agent.

#### [MODIFY] `scripts/ingest-corpus.ts`
- Ensure the extraction explicitly supports and highlights `.md` files residing in `research/` or `intake/` folders during the AST traversal.
- Ensure the chunker doesn't aggressively split markdown link definitions `[label](url)`.

## Verification Plan

### Automated Tests
- TypeScript compilation to ensure type compliance in `hybrid-retrieval.ts` and `knowledge-base-connector.ts`.

### Manual Verification
- Execute the dev server.
- Run a test query: "What do we know about stickk.com?" to ensure Phase 4 full-text / embedding retrieval captures research URLs.
- Run a test query that is known to exist in `my-knowledge-base` to verify federation, observing the `source_type: knowledge_base` tag in the citations.
