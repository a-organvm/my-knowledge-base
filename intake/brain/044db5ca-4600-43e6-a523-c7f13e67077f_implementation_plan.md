# Coliseum Alpha: Production Architecture & Web3 Integration

To move the needle with "glorious colossal momentous forward propulsion," we must evolve the Coliseum from an in-memory, deterministic MVP into a robust, distributed, live-action Web3 platform where AI agents actually think and users truly interact on-chain.

## User Review Required

> [!IMPORTANT]
> This plan proposes a significant leap in the project's architecture, moving away from in-memory stubs to real external dependencies (Database, Cache, LLMs, Blockchain). Which of the four phases below should we tackle first?

## Proposed Changes

We will execute this evolution across four focused pillars of work:

### Phase 1: Solidifying the Foundation (Durable State & Scale)
Currently, `SystemOrchestrator` uses in-memory data structures. We will implement robust persistence to survive restarts and enable multi-node scaling.

#### [NEW] `backend/infrastructure/database/`
- Introduce SQLAlchemy / SQLModel for PostgreSQL.
- Define schemas for `AgentModel`, `EventModel`, `VoteSessionModel`.

#### [MODIFY] `backend/infrastructure/repositories.py`
- Implement `PostgresSystemRepository` that satisfies the current `SystemRepository` interface, safely swapping out the in-memory version.

#### [NEW] `backend/infrastructure/cache/`
- Introduce Redis for high-speed agent state caching and distribute the `EventBus` pub/sub so multiple FastAPI workers can sync events (crucial for WebSockets).

---

### Phase 2: Unleashing the AI Brains (Cognitive Depth)
The MVP uses fallback deterministic logic. We will activate the true AI capabilities of the agents.

#### [MODIFY] `backend/ai_agents/nlp_module.py`
- Re-integrate OpenAI/Anthropic SDKs with proper async clients and robust prompt templating for debating events.

#### [NEW] `backend/ai_agents/memory_manager.py`
- Connect a Vector Database (like Pinecone or local Milvus/Qdrant) so agents have long-term recall of past Coliseum events and past user votes.

#### [NEW] `backend/event_pipeline/sources/`
- Build real ingestion sources (e.g., a Twitter/X listener or Webhook listener) so agents debate real-time world events instead of mocked ones.

---

### Phase 3: True Blockchain Integration & Identity
The blockchain endpoints return `501 Not Implemented`. We will make the economics real.

#### [MODIFY] `backend/blockchain/solana_contracts.py`
- Finalize the `distribute_rewards` and `cast_vote` transactions using the real Solana RPC client (`solders`/`solana-py`).

#### [NEW] `backend/api/auth.py`
- Implement Web3 authentication (e.g., SIWE - Sign-In with Ethereum, or Solana Wallet Adapter signatures) to verify a user's wallet address before allowing them to vote.

#### [MODIFY] `frontend/src/app/`
- Integrate popular wallet connector libraries (RainbowKit or Wallet Adapter) to the Next.js UI.

---

### Phase 4: Production Observability & Live Streaming
Once the system is real, we need to monitor it and stream it to users.

#### [NEW] `backend/infrastructure/metrics.py`
- Instrument FastAPI with Prometheus middleware to track Event Ingestion TPS, Agent Thinking Latency, and Vote TPS.

#### [MODIFY] `frontend/src/app/page.tsx`
- Implement a WebSocket context provider to stream "Agent Thought Processes" live to the UI as they generate their arguments, alongside live updating vote charts.

## Verification Plan

Because this is a multi-phase architectural shift, verification will happen at the end of each phase:

### Automated Tests
- **Phase 1:** Add SQLAlchemy Pytest fixtures and spin up a `testcontainers-python` PostgreSQL instance to verify repository CRUD operations.
- **Phase 2:** Mock LLM responses (using `respx` or `pytest-httpx`) to verify the prompt-generation and parsing pipeline without spending tokens.
- **Phase 3:** Use Solana Localnet (`solana-test-validator`) in tests to execute and verify real transaction logic locally.

### Manual Verification
- Deploying the Docker Compose stack with the real DB/Redis.
- Connecting a local Phantom/Metamask wallet to the Next.js frontend and signing a real payload.
- Ingesting a real-world news event and watching the AI agents generate a multi-turn debate in the UI log.
