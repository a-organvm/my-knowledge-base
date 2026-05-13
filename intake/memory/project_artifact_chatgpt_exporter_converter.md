---
name: chatgpt_exporter_to_bundle converter
description: Bridges third-party chatgptexporter.com per-conversation JSON dumps into the engine's standard ChatGPT-export bundle so the existing adapter can ingest them
type: project
originSessionId: 5a485c0a-8c2d-4af3-a88c-63d09aca2467
---
**What:** A `scripts/chatgpt_exporter_to_bundle.py` converter in conversation-corpus-engine that handles the third-party "ChatGPT Exporter" browser-extension format (one `ChatGPT-<title>.json` per conversation with `{metadata, messages: [{role, say, time}]}` schema). Converts each into a standard ChatGPT-export mapping-tree conversation, dedupes by link-derived UUID, emits a synthetic bundle, then the user runs the existing `cce provider import chatgpt` pipeline on the bundle.

**Where:**
- Script: `~/Workspace/organvm/conversation-corpus-engine/scripts/chatgpt_exporter_to_bundle.py`
- Tests: `~/Workspace/organvm/conversation-corpus-engine/tests/test_chatgpt_exporter_to_bundle.py`
- Commit: `7e3da5d` (organvm-i-theoria/conversation-corpus-engine#main)

**State:** shipped 2026-04-25. End-to-end verified on `~/Downloads/brainstorm-export-20260423/`:
- 24 input files → 14 unique conversations (10 deduped via `(1)` filename pairs sharing link UUIDs)
- Pipeline output: 14 threads, 75 pairs, 77 action items, 52 unresolved questions, 0 empty/near-dupe/flagged
- Verification corpus written to `/tmp/brainstorm-corpus/` (not federated into production — separate decision)

**Tests:** 13 new (HelpersTests + ConvertOneTests + ConvertDirectoryTests + EndToEndIntegrationTests). Full suite: 311 passed.

**Why two-step instead of full provider integration:**
The engine's recipe (`Adding a Provider` in CLAUDE.md) requires touching 6 files (`provider_catalog.py`, `provider_exports.py`, `provider_discovery.py`, new `import_X_export_corpus.py`, `provider_import.py`, 6 CLI choices). The converter approach gets to ingestion *today* with one new file + tests, no provider wiring. If the user wants `cce provider import chatgpt-exporter <dir>` as a first-class command later, the converter logic ports trivially.

**Open follow-ups:**
- Promote to first-class `chatgpt-exporter` provider in PROVIDER_CONFIG (recipe-compliant).
- Decide whether brainstorm-export-20260423 corpus should be federated into the production conversation-corpus-site (currently sitting in `/tmp/`).
- The 5 named ChatGPT projects from today's screenshots (consult-consuls-console, gay-horror-blender, atomic-knowledge-assembler, machina-mundi-canonici, content-multiplex) are project shells — orthogonal to this corpus ingest. That's the Hokage agent's lane.

**Why:** "B2 ChatGPT json-per-conversation adapter" was the open backlog item from the original session start ("there are a few important priorities for project creation from the chatgpt export"). My multi-part patch from earlier today addressed the official-export-split-into-N-zips case; this addresses the *different* third-party-extension-one-file-per-conv case. Together the engine now handles three ChatGPT export shapes: single bundle, N-part bundle, json-per-conversation extension dump.
