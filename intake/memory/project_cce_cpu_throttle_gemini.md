---
name: CCE CPU throttling + Gemini local-session spike
description: CPU fix (taskpolicy, trigram pre-filter, --throttle) deployed; Gemini macOS app cache decrypted (AES-256-GCM), full content needs web API
type: project
---

## CCE CPU Throttling (2026-04-16) — IMPLEMENTED

Four-layer fix for `com.4jp.cce-refresh` LaunchAgent burning 100% CPU:

1. **`taskpolicy -b`** in `refresh_local_sessions.sh` — confines to E-cores (deployed)
2. **`--throttle 0.001`** CLI flag threaded through entire call chain (deployed, 9 files)
3. **Trigram Jaccard pre-filter** in `detect_near_duplicates()` — replaces O(n²) SequenceMatcher with hash-based screening. ~10-20x speedup. Both chatgpt + claude import modules. (deployed)
4. **LaunchAgent schedule** — Nice 10→19, interval 6h→12h, timeout reduction. (DEFERRED — verify algorithmic fix in production first)

277 tests pass. Code committed but not yet pushed at session end.

**Why:** ChatGPT refresh regularly timed out at 45min. Two Python processes at 100% CPU caused system sluggishness on 16GB M3 Mac.

**How to apply:** Changes in `conversation-corpus-engine` repo on `main` branch. LaunchAgent plist (`~/Library/LaunchAgents/com.4jp.cce-refresh.plist`) needs manual Nice→19 bump after verifying next cycle.

## Gemini Local-Session Spike (2026-04-16) — INVESTIGATION COMPLETE

Gemini macOS app (`com.google.GeminiMacOS`) stores conversations locally.

### What works
- **Decryption**: AES-256-GCM. Two 32-byte keys stored as hex-encoded protobuf in macOS keychain (service: `Gemini Safe Storage`, account: `Gemini Keys`). Key ID in each record's metadata selects which key.
- **Cache**: `~/Library/Caches/com.google.GeminiMacOS/Gemini/user1/ChatInfo2.store` — Core Data SQLite with 51 conversations. `ZCHATINFOSTOREDMODEL` has UUID, Robin conversation ID, timestamp, encrypted protobytes.
- **Auth**: `~/Library/Application Support/com.google.GeminiMacOS/Data/user1/auth` — encrypted with key 1, contains OAuth2 access token (`ya29.*`), refresh token, Google account ID. Scopes include `auth/gemini`, `auth/assistant`.
- **Chrome cookies**: 15 Google session cookies readable, active web session confirmed (`SNlM0e` CSRF token obtained).

### What doesn't work yet
- **Messages table is empty** — app caches metadata only, not full conversation content
- **Web API**: `batchexecute` RPC IDs rotate per deployment; need browser network interception to capture current ones
- **gRPC API**: App uses `google.ai.generativelanguage.v1main` protobuf over gRPC; needs protobuf definitions

### Next steps
- Use Chrome MCP or DevTools to intercept `batchexecute` calls and map current RPC IDs
- Or ship metadata-only adapter now, add full content path later
- Spike script at `scripts/spike_gemini_cache.py` (not committed — investigation artifact)
