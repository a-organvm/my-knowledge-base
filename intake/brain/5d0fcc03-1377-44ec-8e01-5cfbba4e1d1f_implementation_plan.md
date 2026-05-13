# Implementation Plan: Exhaustive Testing Protocols

We need to establish comprehensive and reliable testing protocols across the entire project to ensure stability, particularly for MVP components like Agents, Events, Voting, and the Frontend UI.

## User Review Required

> [!CAUTION]
> The backend tests currently attempt to connect to a real PostgreSQL database, leading to `InvalidPasswordError`. We will need to decide if we should use an in-memory SQLite database for tests, or if we should mock the database layer entirely. The plan below assumes we will use an **in-memory SQLite DB or mocks** for unit tests.

> [!NOTE]
> For the frontend, Next.js standardizes on Jest and React Testing Library for component testing. We will set this up as the primary testing framework.

## Proposed Changes

### Backend Testing Enhancements

The existing test suite (`backend/tests/`) has 25 tests, with 11 failures and 5 errors due to structural changes since they were written.

#### [MODIFY] `backend/tests/conftest.py` (New or Modified)
- Add fixtures to mock the database connection or setup an in-memory test database, preventing `asyncpg` failures.

#### [MODIFY] `backend/tests/` (Various test files)
- **`test_solana_contracts.py`**: Fix `TypeError` in `SolanaContractManager.__init__()` by passing the correct arguments.
- **`test_voting_flow.py`**: Await coroutines properly to fix `AttributeError: 'coroutine' object has no attribute 'session_id'`.
- Add `# type: ignore` or mock the dependencies where external systems (like Chainlink/Solana) are called.

---

### Frontend Testing Setup

The frontend currently has no testing framework installed. We will configure Jest and React Testing Library.

#### [MODIFY] `frontend/package.json`
- **Dependencies (dev)**: Add `jest`, `jest-environment-jsdom`, `@testing-library/react`, `@testing-library/jest-dom`, `@types/jest`.
- **Scripts**: Add `"test": "jest"`, `"test:watch": "jest --watch"`.

#### [NEW] `frontend/jest.config.js`
- Configure Next.js Jest integration using `next/jest.js`.

#### [NEW] `frontend/jest.setup.js`
- Import `@testing-library/jest-dom` and setup any necessary global mocks (e.g., `ResizeObserver` or `window.matchMedia` for 3D components).

#### [NEW] `frontend/src/components/__tests__/Arena3D.test.tsx`
- Write basic render tests for the `Arena3D` component. Since it uses `react-three-fiber`, we will need to mock the Canvas or provide a basic environment to ensure it mounting doesn't throw errors.

#### [NEW] `frontend/src/app/__tests__/page.test.tsx`
- Write a test to ensure the main UI layout renders correctly and connects to the mocked store.

## Verification Plan

### Automated Tests
1. **Backend Tests**: Run `export PYTHONPATH=$PWD && pytest backend/tests/ --cov=backend` from the project root. Expected result: High pass rate, no connection errors.
2. **Frontend Tests**: Run `cd frontend && pnpm run test`. Expected result: All component tests pass successfully.

### Manual Verification
1. Run `pnpm run dev` and ensure the frontend still loads correctly without any side effects from the testing setup.
2. Manually verify `Arena3D` renders and interacts as expected in the browser.
