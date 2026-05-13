# Remote Sharing Enablement

To share a whistleblower link with a friend remotely, the app's components (API, Web, and Mobile) must transition from `localhost` to public URLs. This plan outlines how to expose your local environment or prepare it for production hosting.

## User Review Required

> [!IMPORTANT]
> Since the mobile app is hardcoded to `localhost:3000` in several places, you must decide if you want to use a tunnel (like `ngrok`) for a quick test or deploy to a permanent host (Vercel/Render).
>
> **Option A: Tunnel (Quickest)**
> 1. Run `ngrok http 3000` to expose the API.
> 2. Run `ngrok http 3001` to expose the Web dashboard.
> 3. Update `.env` and `ApiClient.ts` with the new URLs.
>
> **Option B: Production Deployment (Best for Scaling)**
> 1. Deploy API to Render/Railway.
> 2. Deploy Web to Vercel.
> 3. Point Mobile app to the production API.

## Proposed Changes

### [Component] API & Web Config

#### [MODIFY] [.env.example](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/.env.example)
Add placeholders for public URLs to ensure consistent link generation.

#### [MODIFY] [ApiClient.ts](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/mobile/services/ApiClient.ts)
Ensure `STYX_API_URL` is correctly picked up or updated.

### [Component] Whistleblower Flow

#### [MODIFY] [contracts.service.ts](file:///Users/4jp/Workspace/organvm-iii-ergon/peer-audited--behavioral-blockchain/src/api/src/modules/contracts/contracts.service.ts)
Ensure the generated whistleblower links include the base public URL of the web dashboard.

---

## Verification Plan

### Automated Tests
1. **Link Generation Test**: Run `npx tsx scripts/validation/02-simulator-spoof-check.ts` and verify it constructs a valid-looking link structure.

### Manual Verification
1. **Tunnel Test**:
   - Start local services: `make docker-up` and `make dev`.
   - Start `ngrok` (if using Option A).
   - Attempt to access the `/api/docs` via the public URL.
   - Create a contract in the mobile app and verify the generated link in the database is accessible via the web dashboard.
2. **Whistleblower Submission**:
   - Open the whistleblower link in a browser on a different network (e.g., mobile data).
   - Submit a test "proof" and verify it appears in the `Fury` queue.
