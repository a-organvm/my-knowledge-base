# Phase Delta: The Arena

Activate social dynamics, dispute resolution, and fraud detection. Complete the Validation Gates for production readiness.

---

## Proposed Changes

### Priority 1: pHash Deduplication Pipeline

Wire `PHashService` into proof upload flow to reject duplicate submissions before they reach Furies.

#### [MODIFY] [proofs.controller.ts](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/src/modules/proofs/proofs.controller.ts)

- On `confirm-upload`: download first frame from R2, compute pHash, check against `proof_hashes` table
- Reject with `409 CONFLICT` if duplicate detected (hamming distance < 10)
- Store hash in `proof_hashes` table on success

#### [MODIFY] [proofs.module.ts](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/src/modules/proofs/proofs.module.ts)

- Add `PHashService` to providers

#### [NEW] `migrations/005_proof_hashes.sql`

- `proof_hashes` table: `proof_id UUID, phash VARCHAR(16), created_at TIMESTAMP`
- Index on `phash` for fast hamming lookups

---

### Priority 2: Dispute Resolution Pipeline

Complete the appeal → judge review → resolution flow. `DisputeService` currently only initiates appeals with a $5 fee hold.

#### [MODIFY] [dispute.service.ts](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/services/escrow/dispute.service.ts)

- Add `resolveDispute(proofId, outcome, judgeNotes)` — captures/refunds fee, updates proof status
- Add `getDisputeQueue()` — returns disputes with metadata for The Judge
- Add `assignToJudge(disputeId, judgeUserId)` — locks dispute for review

#### [MODIFY] [admin.controller.ts](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/src/modules/admin/admin.controller.ts)

- Add `POST /admin/disputes/:id/resolve` — judge resolves dispute with notes
- Add `GET /admin/disputes/:id` — full dispute detail with media signed URL, assignment history, votes
- Fix `HoneypotInjectorService` → `HoneypotService` import (renamed in Phase Gamma)

---

### Priority 3: Desktop "Judge's Gavel" Dashboard

Enhance the Tauri desktop app for dispute resolution. Currently has 5 tabs but MacroReview lacks media inspection.

#### [MODIFY] [MacroReview.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/components/MacroReview.tsx)

- Add dispute detail panel: video player (signed URL), Fury votes, user history
- Add "Uphold" / "Overturn" / "Escalate" buttons with judge notes textarea
- Add proof metadata inspection (pHash, timestamps, watermark validation)

#### [MODIFY] [LedgerInspector.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/desktop/src/components/LedgerInspector.tsx)

- Add ledger integrity verification endpoint call (`GET /wallet/integrity`)
- Visual diff highlighting for suspicious entries

---

### Priority 4: Tavern Board (Gamified Leaderboard)

Upgrade the basic `Leaderboard.tsx` to a full social-dynamics-driven leaderboard with streaks, tier badges, and real-time updates.

#### [MODIFY] [Leaderboard.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/web/components/Leaderboard.tsx)

- Tier badges (Bronze/Silver/Gold/Diamond based on integrity score thresholds)
- Streak indicators (consecutive days of compliance)
- Animated rank changes, weekly/monthly/all-time filters
- "Fury of the Week" spotlight section

#### [NEW] `src/api/src/modules/users/users.controller.ts` endpoint

- `GET /users/leaderboard` with `?period=weekly|monthly|alltime` filter
- `GET /users/:id/streak` — current streak and longest streak

---

### Priority 5: Public Activity Feed

Real-time public event feed for social proof and FOMO dynamics.

#### [NEW] `src/api/src/modules/feed/feed.controller.ts`

- `GET /feed` — returns anonymized recent events (proof verified, contract completed, bounty paid)
- SSE `GET /feed/stream` — real-time push of events as they occur
- Anonymization: uses first 4 chars of user hash, never email

#### [NEW] `src/api/src/modules/feed/feed.module.ts`

- Wire `AnonymizationService`, `TruthLogService`

#### [MODIFY] [TavernFeed.tsx](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/mobile/components/TavernFeed.tsx)

- Connect to `/feed/stream` SSE endpoint
- Show event type icons, timestamps, anonymized actor

---

### Priority 6: Validation Gates

Implement the 4 Technical Validation Gates from the roadmap.

| Gate | Test | Status |
|------|------|--------|
| Phantom Money | SQL constraints reject unbalanced entries | Spec exists: `ledger.service.spec.ts` — extend |
| Simulator Spoof | Hardware predicates reject manual data | Needs watermark verification test |
| Twin Upload | pHash rejects duplicate video proof | Wire into Priority 1 |
| Gatekeeper | "Redacted Mode" — no gambling terms in binary | New CI script |

#### [NEW] `scripts/gatekeeper-scan.sh`

- Scan built binaries/bundles for forbidden terminology (Fury, Bounty, Stake, etc.)
- Replace with neutral terms (Review, Reward, Deposit) via linguistic middleware

#### [MODIFY] Test specs

- Extend `ledger.service.spec.ts` with explicit Phantom Money constraint tests
- Add `phash.integration.spec.ts` for Twin Upload gate
- Add watermark validation test in `ProofCaptureScreen.test.tsx`

---

### Priority 7: AdminController Hardening

#### [MODIFY] [admin.controller.ts](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/src/modules/admin/admin.controller.ts)

- Fix broken `HoneypotInjectorService` → `HoneypotService` import
- Add `GET /admin/users/:id` — full user profile with contract/proof/assignment history
- Add `POST /admin/users/:id/integrity` — manual integrity score adjustment with reason
- Add rate limiting to admin mutation endpoints

---

### Priority 8: CHANGELOG & Documentation

#### [MODIFY] [CHANGELOG.md](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/CHANGELOG.md)

- Document Phase Gamma and Phase Delta changes

#### [MODIFY] [roadmap.md](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/docs/roadmap.md)

- Mark Phase Gamma tasks complete, Phase Delta as in-progress

---

## Verification Plan

### Automated Tests
- `npm run test` — all 46+ spec files pass
- New pHash integration test with sample image buffers
- New dispute resolution unit tests
- Gatekeeper scan passes on built bundles

### Manual Verification
- Desktop Judge app: inspect dispute, play media, render verdict
- Leaderboard: verify tier badges and streak display
- Public feed: verify anonymization (no PII leakage)
