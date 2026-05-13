# Coliseum Continuous Demo Loop Plan

This plan aims to execute the provided handoff document, resulting in a self-running 3-minute demo loop for the Prix Ars Electronica submission.

## User Review Required

> [!IMPORTANT]
> The orchestrator currently calls an external LLM using LiteLLM. I will need to set an API key (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`) in the `.env` file since the repo only has a placeholder. Please let me know how you would like me to retrieve or set this key securely.

## Proposed Changes

### Environment & Database
*   **Virtual Environment Setup:** Recreate `.venv`, install dependencies from `backend/requirements-test.txt`.
*   **Configuration:** Copy `backend/.env.example` to `backend/.env`. Set `DATABASE_URL` to a local SQLite schema (`sqlite:///./coliseum_demo.db`).

### Seeding
#### [NEW] `backend/scripts/seed_demo.py`
*   Create SQLAlchemy tables via `Base.metadata.create_all`.
*   Seed agents: Socrates, Machiavelli, Ada Lovelace, The Moderator.
*   Seed initial trigger event (e.g., "Should AI systems have constitutional rights?").

### Orchestration & Routing
#### [MODIFY] `backend/event_pipeline/worker.py`
*   Decrease `AutonomousArenaWorker` interval to ~15-20 seconds to speed up action for video.
*   Ensure the worker fetches the seeded trigger event and sends it to the orchestrator to automatically start the debate.
#### [MODIFY] `backend/ai_agents/orchestrator.py`
*   Ensure `_tick()` auto-progresses combat turns at an appropriate visual pacing.
*   Verify `start_battle(topic)` is correctly connected and broadcasts WebSocket messages as `combat_update`.

### Frontend Integration & Components
#### [MODIFY] `frontend/src/app/page.tsx`
*   Update WebSocket event listener to handle `combat_update` messages.
*   Embed the `<BattleScene />` UI component in the layout (it's currently separate from the main layout rendering `Arena3D`).
#### [MODIFY] `frontend/src/components/Arena3D.tsx`
*   Parse incoming `combat_update` for the `isAttacking` state.
*   Add weapon/attack animation flash when an agent attacks.
*   Add a visual damage "hit" flash on the defending agent.
*   Add a pulsing red border/glow during active combat.

## Verification Plan

### Automated Tests
*   Run `python -m pytest -q backend/tests` to verify backend integrity.
*   Launch backend to verify it does not error immediately (`uvicorn backend.main:app`).
*   Launch frontend to verify it compiles (`pnpm run dev`).

### Manual Verification
*   Open the browser and visually verify Agents appear in `AgentGrid`.
*   Observe the Autonomous battle triggering within 30s.
*   Verify HP Bar updates, attack flashes, and the combat log correctly display the state without crashing for 5+ minutes.
