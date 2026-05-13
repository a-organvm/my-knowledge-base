# Phase Epilogue: The Crucible (Hardening & Realization)

## Goal Description
The Monorepo is completely scaffolded, but core mathematical engines are still heavily commented stubs. In this ultimate phase, we will implement the actual TypeScript algorithms mapped from the foundational psychology documents. We will also harden the repository by fixing the root `Makefile` to accommodate the user's local `npm/npx` environment and create an orchestration initializer.

## Proposed Changes

### Workstream Root (Environment)
- **[MODIFY] `Makefile`**: Switch `yarn` commands to `npm run` and `npx turbo run` to ensure local execution viability.
- **[NEW] `setup.sh`**: Creates an idempotently safe bootstrap script that configures `docker-compose up -d` and installs dependencies.

### Workstream Shared (The Mathematical Core)
- **[MODIFY] `src/shared/libs/integrity.ts`**: Implement `calculateIntegrity`, calculate decay, tier gating, and `calculateAccuracy` functions based on the $1.955$ Loss Aversion and $+5 / -15$ variables.
- **[MODIFY] `src/shared/libs/behavioral-logic.ts`**: Implement the `useGraceDay` and `grantOnboardingBonus` deterministic logic structures.

### Workstream 1 (API Core)
- **[NEW] `src/api/services/escrow/aegis.service.ts`**: Create the `AegisProtocolService` that actively enforces the `MIN_SAFE_BMI` (18.5) and `MAX_WEEKLY_LOSS_VELOCITY_PCT` (2%) guardrails to reject dangerous physical goals instantly.

## Verification Plan
1. Construct the algorithms natively in TypeScript without external package reliance.
2. Execute `npx turbo run build test`.
3. Verify `make test` runs from the root effectively.
