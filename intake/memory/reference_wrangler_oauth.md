---
name: Cloudflare wrangler OAuth — rotating refresh tokens
description: Wrangler uses rotating OAuth refresh tokens; testing with curl burns the token; recovery via `wrangler login` with browser re-auth
type: reference
originSessionId: 80581eb0-933d-4de3-a31f-f0c420955109
---
Cloudflare's wrangler CLI uses **rotating OAuth refresh tokens** — each token exchange invalidates the previous refresh token.

**Danger:** Testing the refresh token with `curl` (or any manual exchange) consumes it. The wrangler CLI then holds a stale token and all subsequent operations fail with auth errors.

**Recovery:** Run `wrangler login` to re-authenticate via browser. This issues a fresh token pair.

**How to apply:** Never manually test wrangler OAuth tokens. If auth breaks, `wrangler login` is the fix. If debugging CF auth issues, use `wrangler whoami` (read-only, doesn't rotate).
