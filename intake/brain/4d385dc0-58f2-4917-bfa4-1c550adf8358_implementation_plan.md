# Completing the Alpha-to-Omega Roadmap

This plan focuses on finalizing the remaining unchecked items on the `docs/roadmap.md` and bringing Styx to full roadmap completion.

## User Review Required
No breaking changes. This finalizes missing boilerplate for B2B features, adds terminology compliance for mobile apps, and adds a high-risk payment routing scaffold.

## Proposed Changes

### Documentation & Checkbox Sync
Check off the following tasks in `docs/roadmap.md` that have already been implemented:
- **Phase Beta**: Native Bridges (HealthKit deprecated natively)
- **Phase Beta**: Grace Days & Endowed Progress (already in `behavioral-logic.ts`)
- **Phase Omega**: Consumption Billing (already in `BillingService`)
- **Phase Omega**: Anonymization Layer (already in `AnonymizeService`)

---

### Backend API: B2B CRM Connectors
The HubSpot and Salesforce connectors exist but aren't exposed or utilized by the `B2BModule`.
#### [NEW] `src/api/src/modules/b2b/crm.service.ts`
- Implement a unified `CrmService` that takes `SalesforceConnector` and `HubSpotConnector` as dependencies.
- Expose a `pushEmployeeEvent(enterpriseId, event)` method that routes the event based on enterprise configuration (or pushes to both for now).
#### [MODIFY] `src/api/src/modules/b2b/b2b.module.ts`
- Register `SalesforceConnector`, `HubSpotConnector`, and `CrmService` as providers and export `CrmService`.

---

### Backend API: High-Risk Merchant Routing
To satisfy "High-Risk Merchant Underwriting" and `High-Risk Merchant Routing` fallbacks:
#### [NEW] `src/api/src/modules/payments/payment-router.service.ts`
- Scaffold a `PaymentRouterService` that determines whether to route a transaction to Stripe or a High-Risk Processor (e.g., Corepay) based on user risk score or a feature flag.
#### [MODIFY] `src/api/src/modules/payments/payments.module.ts`
- Register the `PaymentRouterService`.

---

### Mobile App: Linguistic Middleware
To satisfy "Linguistic Middleware" (swapping gambling terms for safe terms to avoid App Store rejection).
#### [NEW] `src/mobile/services/LinguisticMiddleware.ts`
- Create a text processing utility with a dictionary that replaces forbidden terminology (e.g., `Bet -> Commitment`, `Wager -> Pledge`, `Pot -> Vault`, `Stake -> Vault`).
- Expose a `sanitizeUiText(text: string): string` function.

## Verification Plan

### Automated Tests
- Run `make test` (or `cd src/api && npm run test`) to ensure the NestJS dependency graph resolves correctly after adding the CRM services and Payment Router to their respective modules.
- Ensure the TypeScript compiler succeeds for both `api` and `mobile` projects.

### Manual Verification
- Check the `roadmap.md` file visually to ensure all tasks are marked as `[x]`.
