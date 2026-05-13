# Beta Promotion Workflow + Trace-ID Regression Tests

Add a beta promotion workflow, web component tests for trace-ID rendering on admin/HR pages, and mobile screen-level tests for trace-ID display on auth/create-contract screens.

## Proposed Changes

### 1. Beta Promotion Workflow — Already Complete ✅

The beta promotion workflow **already exists** and is fully wired in:

- [beta-promotion.yml](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/.github/workflows/beta-promotion.yml) — Full pipeline: `preflight` → `manual_approval` (optional, gated by `require_manual_approval` input) → `deploy_beta_api` / `deploy_beta_web` → `smoke_beta` (runs `beta-smoke.sh`) → `promotion_ready`
- [deploy.yml](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/.github/workflows/deploy.yml) — Already calls `beta-promotion.yml` as a reusable workflow **in parallel** with `staging-promotion.yml` (lines 23–28)

**No changes needed.** The workflow runs `scripts/smoke/beta-smoke.sh` and has an optional `require_manual_approval` boolean input that gates on a `beta-promotion-approval` environment.

---

### 2. Web Trace-ID Regression Tests (admin/HR)

Both the admin page and HR page use `<SupportTraceMessage>` to render error states with trace IDs. The existing test only covers the component in isolation — we need page-level regression tests to catch if admin/HR error rendering breaks.

#### [NEW] [page.test.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/web/app/admin/page.test.tsx)

- SSR rendering tests using `renderToStaticMarkup` (same pattern as existing `SupportTraceMessage.test.tsx`)
- Test cases:
  - Renders `SupportTraceMessage` with trace-ID in admin error state
  - Does not render trace-ID without `[request_id:]` suffix
  - Renders SupportTraceMessage for honeypot/ban/resolve result areas

#### [NEW] [page.test.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/web/app/hr/page.test.tsx)

- SSR rendering tests for HR error state with trace-ID
- Test cases:
  - Renders `SupportTraceMessage` with trace-ID in HR error state
  - Does not render trace-ID without suffix
  - Feature-flag disabled state renders correctly

> [!NOTE]
> These tests will import the `SupportTraceMessage` component directly and test its rendering with admin/HR error string patterns, since the full page components require mocking `useRouter`, `useAuth`, and `api` — we'll test the trace-ID rendering integration directly.

---

### 3. Mobile Screen Tests for Trace-ID (auth / create-contract)

No screen-level component tests exist today. Using the project's existing pattern (shallow call + `collectText` from `SupportTraceErrorBanner.spec.tsx`), we'll add focused trace-ID rendering tests.

#### [NEW] [LoginScreen.spec.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/mobile/screens/LoginScreen.spec.tsx)

- Shallow render with error containing `[request_id:]` suffix → verify trace-ID text appears
- Shallow render with plain error → verify no trace-ID rendered
- Verify core screen elements render (title, inputs, button)

#### [NEW] [RegisterScreen.spec.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/mobile/screens/RegisterScreen.spec.tsx)

- Same pattern: trace-ID in error, no trace-ID without suffix, core elements render

#### [NEW] [CreateContractScreen.spec.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/mobile/screens/CreateContractScreen.spec.tsx)

- Verify trace-ID banner presence in error state
- Verify core screen elements render (stream chips, submit button)

> [!NOTE]
> Mobile tests use the existing `react-native` mock at `__mocks__/react-native.ts` which maps RN primitives to HTML elements. Tests call screen components as functions with minimal props (mocking navigation/services) and use `collectText` to verify output.

## Verification Plan

### Automated Tests

```bash
# Web tests
cd src/web && npx jest --verbose

# Mobile tests
cd src/mobile && npx jest --verbose
```

All new test files follow the existing project patterns and will be picked up by the testPathPatterns glob automatically.
