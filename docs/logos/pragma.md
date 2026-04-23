# Pragma: The Concrete State of the Knowledge Base

**Status:** IN-PROGRESS
**Date:** April 23, 2026

## 1. Current Inventory
- **Atomic Units:** ~32,000 (extracted from 10 months of prompts).
- **Core Sources:** Claude (89MB), Gemini (Drive), Grok, local notes, academic artifacts.
- **Search Capability:** Hybrid (FTS5 + ChromaDB Vectors).
- **Intelligence Layer:** Insight extraction, auto-tagging, and summarization operational.

## 2. Infrastructure
- **Runtime:** Node.js 25.x / TypeScript.
- **Database:** SQLite (Knowledge) + ChromaDB (Vectors).
- **Automation:** Playwright-based exporters.
- **Federation:** Real-time watcher (Chokidar) and ingestion manager.

## 3. Deployment
- **Local:** `npm run web` at `http://localhost:4001`.
- **Cloud:** Fly.io (express) and Cloudflare Pages (React).

## 4. Known Tensions
- **Context Rot:** 81.9% of the corpus remains unreviewed (triage pending).
- **Redundancy:** High overlap between atomic units from different sessions.
- **Connectivity:** Graph relations are 40% populated; many "islands" of knowledge exist.
