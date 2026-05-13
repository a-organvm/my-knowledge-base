# Refactor Inline CSS to External Files

## Goal Description
The goal is to refactor inline CSS styles in `App.tsx`, `HashCollider.tsx`, and `NetworkGuard.tsx` to external CSS files to resolve IDE warnings and improve code maintainability.

## User Review Required
None. This is a refactoring task to match best practices.

## Proposed Changes

### Desktop App

#### [MODIFY] [App.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/App.tsx)
- Import `./App.css`
- Replace inline styles with class names (e.g., `toast-overlay`, `app-container`, `header`, `sidebar`, `nav-button`).

#### [NEW] [App.css](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/App.css)
- Create new CSS file containing styles extracted from `App.tsx`.

#### [MODIFY] [HashCollider.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/components/HashCollider.tsx)
- Import `./HashCollider.css`
- Replace inline styles with class names.

#### [NEW] [HashCollider.css](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/components/HashCollider.css)
- Create new CSS file containing styles extracted from `HashCollider.tsx`.

#### [MODIFY] [NetworkGuard.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/components/NetworkGuard.tsx)
- Import `./NetworkGuard.css`
- Replace inline styles with class names.

#### [NEW] [NetworkGuard.css](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/components/NetworkGuard.css)
- Create new CSS file containing styles extracted from `NetworkGuard.tsx`.

## Verification Plan

### Automated Tests
- Run `npm run build` in `src/desktop` to ensure no build errors.
- Verify that the new CSS files are created and the TSX files import them.

### Manual Verification
- Inspect the generated CSS files to ensure correct styles are valid.
