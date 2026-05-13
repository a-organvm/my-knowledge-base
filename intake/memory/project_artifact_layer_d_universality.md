---
name: Layer D — Universal atom + coverage + self-awareness
description: Spec for substrate universality — every storage location scanned, substrate observes itself, fractal magnification. SPEC-ONLY; iCloud + Apple Notes + Voice Memos + Photos + 137-Downloads ingestion all uncovered.
type: project
originSessionId: f3beab49-8440-4336-b4db-299e2933f5a1
---
**What**: Three principles operationalized:
- Universal atom — single envelope schema for every kind (prompt, artifact, note, email, photo, commit, voice_memo, screenshot, memory, plan, hook, statusline, ...)
- Universal coverage — one scanner per storage location, registry-driven
- Self-awareness — substrate's own scripts/lens-YAMLs/plans/hooks/statusline are atoms; observed by the same lens system that observes user content

Coverage gap inventory (concrete from this session):
- iCloud Mobile Documents: `~/Library/Mobile Documents/com~apple~*/` (TextEdit + Pages + CloudDocs `06_Reference_and_Research`, `04_Creative_and_Writing`, `05_Professional_and_Career`, `07_Technical_and_Archives`) — NOT covered
- Apple Notes (sqlite at `~/Library/Group Containers/group.com.apple.notes/`) — NOT covered
- Voice Memos, Stickies, Photos, screenshots, Safari bookmarks — NOT covered
- ~/Downloads (137 files including 1.1GB Gemini hex-zip + 3 Drive Takeout subsets + 31 HTML + 20 PDF) — partial (ChatGPT/Claude WORKING; Gemini HANGING; Drive/HTML/PDF have NO HANDLER)
- Substrate-meta (own scripts, plans, hooks, statusline) — NOT yet promoted to atoms

**Where**:
- Plan: `2026-04-27-universal-atom-coverage-self-awareness.md` (chezmoi 1e7e9d4)
- Target build: `scripts/universalize.py`, `scanners/registry.yaml`, `scanners/{statusline_capture,icloud_textedit,apple_notes,stickies,voice_memos,photos,screenshots,safari_bookmarks,gmail_ingest,github_artifacts,substrate_meta}.py`
- Substrate output: `~/Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/universal-atoms.jsonl` (NEW)

**Project**: `organvm/my-knowledge-base` + `organvm-corpvs-testamentvm`

**For whom**: User — substrate must hold every task at once

**State**: SPEC. None of the scanners built.

**Pending feedback**:
- Photos / voice memos / Gmail beyond MCP-live: opt-in only? (default yes)
- Universal-atom storage location: stay in corpvs vs new `organvm-substrate` repo? (default stay until >100MB)
- Statusline bug: fix immediately or fold into Slice D1? (default fold)
- Hook atoms: persona-as-content boundary, archetype completeness threshold

**Next action**: Slice D1 — `universalize.py` over existing atom stores + `scanners/statusline_capture.py` + statusline fix (first-light). Slice D2 — iCloud + Notes + Stickies scanners.
