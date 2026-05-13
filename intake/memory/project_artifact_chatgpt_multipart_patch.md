---
name: Multi-part conversations.json patch (ChatGPT + Claude)
description: conversation-corpus-engine now natively ingests split exports (N sibling bundles under one parent dir) on both ChatGPT and Claude adapters
type: project
originSessionId: 5a485c0a-8c2d-4af3-a88c-63d09aca2467
---
**What:** Engine-level support for split exports. When a ChatGPT or Claude export gets too large, it ships as multiple zips, each with its own `conversations.json`. Previously: manual concatenation. Now: `discover_bundle_roots()` detects either a single bundle or N sibling bundles under one parent; import flow aggregates and dedupes.

**Where:**
- `~/Workspace/organvm/conversation-corpus-engine/src/conversation_corpus_engine/import_chatgpt_export_corpus.py` + matching tests
- `~/Workspace/organvm/conversation-corpus-engine/src/conversation_corpus_engine/import_claude_export_corpus.py` + matching tests

**Project:** conversation-corpus-engine (organvm-i-theoria, GRADUATED tier)

**State:** shipped 2026-04-25
- ChatGPT — commit `1785fa2`
- Claude — commit `cb2bc9e`

**Surface changes (both adapters):**
- New: `discover_bundle_roots(input_path: Path) -> list[Path]` — single-dir, file input, or sorted multi-part subdirs
- Extended: `copy_bundle_files(..., prefix=None)` — multi-part sources land under `source/<part-name>/`
- Result dict adds: `bundle_part_count`, `bundle_part_names`, `duplicate_conversations_skipped`
- README mentions parts when multi-part
- `resolve_bundle_root` preserved unchanged (back-compat for any external callers)

**Provider differences captured:**
- ChatGPT: dedup key is `conversation_id`, account-scoped file is `user.json` (singular)
- Claude: dedup key is `uuid`, account-scoped files are `users.json` + `projects.json` + `memories.json` (all loaded only from primary bundle)

**Tests:** 16 new total (8 per adapter × 2 adapters). Full suite: 298 passed.

**Backwards compat:** single-bundle layout unchanged on both — `source/conversations.json` stays flat, no prefix.

**Open follow-ups (not done — defer until user asks):**
- 6 other providers in PROVIDER_CONFIG (gemini, grok, perplexity, copilot, deepseek, mistral) likely benefit from the same pattern but each has a different export format; not all may support split exports.
- `thread_path` in threads-index for multi-part still hardcodes `output_root/source/conversations.json` (legacy single-bundle pointer); downstream consumers don't appear to rely on it being a real path, but a per-part path would be more honest.

**Why:** "Patch engine: native multi-part conversations.json support" was the open backlog item from prior session. Heavy users' exports routinely split, and manual concatenation loses the per-part audit trail. The patch keeps source files separated by part (better forensics) while presenting a unified corpus downstream.
