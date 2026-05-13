# The Next Great Leap: Colossal Forward Propulsion

## The Strategic Objective

We have successfully executed the **No Contact Pivot**, establishing the Iron Core (Phase Alpha) and The Shield (Phase Beta). The APIs for the double-entry ledger, Fury router, and contracts are instantiated. 

To achieve **glorious, colossal, momentous forward propulsion**, we must now ignite the **End-to-End Adversarial Loop**. This means connecting the isolated backend engines directly to their human interfaces, transforming Styx from a set of silent APIs into a living, fully weaponized behavioral market.

We must simultaneously execute three massive structural unifications: **The Panopticon Genesis**, **The Judge's Awakening**, and **The Mobile Sensor Shift**.

---

## Proposed Changes: The Engineering Roadmap

### 1. The Panopticon Genesis (Phase Gamma UI Unification)
The `fury` API module and `consensus.engine.ts` currently lack their human operational layer. We must build the *Minority Report*-style UI.
#### [**MODIFY**] `src/web/src/components/FuryWorkbench/`
- Build the **Active Investigation Split-Screen**: Left pane displays whistleblower digital exhaust (texts, call logs); right pane contains the cryptographic attestation controls (Guilty/Not Guilty).
- Wire `zustand` to the `fury.controller.ts` WebSocket/SSE stream to feed live bounty targets to active Furies.
- Enforce the **Honeypot Injection Hook**: The UI must blindly render injected "known-fail" proofs without tipping off the Fury, feeding accuracy scoring back to `fury.worker.spec.ts` algorithms.

### 2. The Judge's Awakening (Phase Delta Desktop Launch)
The `src/desktop` Tauri application is currently a blank slate. The `admin` API module exists but has no sovereign interface.
#### [**NEW**] `src/desktop/src/...` (Tauri App Architecture)
- **The Dispute Tribunal**: Scaffold the Tauri React UI to pull from the `admin` API. This is the "God Mode" dashboard.
- **Ledger Audit & Hash Collider**: Create read-only data grid views of `ledger_entries` for financial forensics, and a visual matrix for pHash duplicate detection (identifying users submitting identical whistleblower proof).
- **Network Authentication**: Hardcode VPN/Corporate IP checks into the desktop boot sequence before allowing API handshakes.

### 3. The Mobile Sensor Shift (Phase Beta Completion)
As mandated by the "No Contact" pivot, fitness metrics are obsolete. We must strip legacy biometric logic and harden the Whistleblower intake loop.
#### [**MODIFY**] `src/mobile/src/services/` & `ios/` & `android/`
- **Strip Health/Fitness Bridges**: Decouple and remove `HealthKitReader.swift` and `HealthConnectReader.kt`. Sensor ingestion must focus *entirely* on digital exhaust and behavioral tracking.
- **Harden Secure Camera**: Update `CameraModule.tsx` to enforce live-capture only (blocking Camera Roll) and watermark images with the "Weigh-in Word" and secure temporal timestamps.

### 4. B2B Enterprise Architecture (Phase Omega Scaffolding)
#### [**NEW**] `src/api/src/modules/b2b/connectors/`
- Complete the wiring for `datalake.service.ts` to push aggregated, anonymized behavioral statistics into the enterprise webhooks, initiating the B2B SaaS consumption billing logic (`billing.service.ts`).

---

## Verification Plan

### Automated Tests
- **E2E Playwright Run (`src/web`)**: Validate that a mock Fury can log in, receive a contract from the queue, vote, and affect the `consensus.engine`.
- **E2E Maestro Run (`src/mobile`)**: Verify that the Secure Camera prevents photo library access and successfully captures timestamped, watermarked digital exhaust.
- **The Simulator Spoof & Phantom Money Checks**: Rerun `01-phantom-money-check.ts` and `02-simulator-spoof-check.ts` post-integration to guarantee the Ledger and Intake loops remain strictly zero-trust.

### Manual Verification
- **The Judge Tribunal Test**: Compile the `src/desktop` Tauri app locally. Verify that the "God Mode" dashboard can inspect an active contract, view the pHash data of uploaded media, and successfully issue a "Ban" mutation to the `admin` API.
- **The Panopticon Stress Test**: Spin up 3 mock desktop browsers, log in as 3 separate Furies, and test the real-time BullMQ distribution across the Next.js `FuryWorkbench` concurrently.

---

> [!IMPORTANT]
> **Strategic Alignment Check**
> This roadmap represents massive architectural synthesis. Before we execute the first line of code, review these priorities. Shall we begin by bootstrapping **The Panopticon Genesis (Web Workbench)** or **The Judge's Awakening (Desktop App)**?
