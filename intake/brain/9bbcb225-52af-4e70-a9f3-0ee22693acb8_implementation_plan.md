# Phase Delta & Omega Implementation Plan

## Goal Description
Complete the "Arena" (Phase Delta) by enabling dispute resolution and social mechanics, and lay the foundation for "The Empire" (Phase Omega) with B2B/Enterprise hooks.

## User Review Required
> [!IMPORTANT]
> **Geofencing**: We will implement a hard block for IPs from specific US states (AZ, AR, DE) to comply with "Skill Gaming" regulations. This may block legitimate dev traffic if you are in those regions (use VPN).

## Proposed Changes

### 1. Phase Delta: The Arena

#### [NEW] [GeofenceGuard](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/guards/geofence.guard.ts)
- Implement `CanActivate` guard.
- Use a geo-ip library (or mock for dev) to check request IP.
- Block restricted jurisdictions (AZ, AR, DE, etc.).

#### [MODIFY] [AdminController](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/src/modules/admin/admin.controller.ts)
- Add `GET /admin/disputes`: List proofs where `status = 'DISPUTED'` or `status = 'FLAGGED'`.
- Return metadata (Device info, Location, Time).

#### [MODIFY] [AdminPage](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/web/app/admin/page.tsx)
- Add "Dispute Resolution" tab/section.
- Render list of disputed proofs with "Uphold" or "Overturn" buttons.
- Show metadata constraints (e.g., "Uploaded from Camera Roll" vs "Live Capture").

#### [MODIFY] [TavernPage](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/web/app/tavern/page.tsx)
- Add "Leaderboard" sidebar.
- Fetch top users by `integrity_score` (Top 10).
- Show "Streak" (days active).

### 2. Phase Omega: The Empire

#### [NEW] [CrmService](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/services/b2b/crm.service.ts)
- Interface for CRM integration (Salesforce/HubSpot).
- Mock implementation logging sync events.

#### [NEW] [ConsumptionBillingService](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/services/b2b/billing.service.ts)
- Track "Insight Generation" events.
- Store billable metrics in `consumption_logs` table.

#### [NEW] [AnonymizationService](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/services/security/anonymization.service.ts)
- Method `anonymizeUser(user)`: Returns user object with PII redacted (email -> hash, name -> initials).

## Verification Plan

### Automated Tests
- **Geofencing**: Unit test `GeofenceGuard` with mock IPs from allowed/blocked regions.
- **Billing**: Unit test `ConsumptionBillingService` to ensure counts increment.

### Manual Verification
1.  **Dispute Flow**:
    - Manually flag a proof in DB (`UPDATE proofs SET status = 'DISPUTED' ...`).
    - Open Admin Dashboard.
    - Verify proof appears in Dispute list.
    - Click "Resolve". Verify DB updates.
2.  **Geofencing**:
    - Curl API with `X-Forwarded-For: <Blocked_IP>`. Verify 403 Forbidden.
3.  **Leaderboard**:
    - Verify Tavern page shows top users.
