# Caller Onboarding Example

**Atom ID:** caller-onboarding-example
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Overview

This example demonstrates how a new user (caller) onboards to the My Knowledge Base system, from first export through their first intelligent query.

## Prerequisites

- Node.js 18+ installed
- API keys for OpenAI and Anthropic (optional for Phase 2/3 features)
- At least one AI conversation source (Claude.app, ChatGPT, Gemini, or local markdown)

## Step 1: Installation

```bash
git clone https://github.com/organvm-i-theoria/my-knowledge-base.git
cd my-knowledge-base
npm install
```

## Step 2: Environment Setup

```bash
# Create .env file
cp .env.example .env

# Add API keys (optional -- system works without them for Phase 1 features)
echo "OPENAI_API_KEY=sk-..." >> .env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

## Step 3: Initialize the Database

```bash
npm run prepare-db
# Output: Database initialized with schema at ./db/knowledge.db
```

## Step 4: First Export

### Option A: ChatGPT (easiest -- bulk JSON export)

1. Visit https://chat.openai.com
2. Settings > Data controls > Export data
3. Download and extract the ZIP
4. Place `conversations.json` in `./intake/chatgpt/`

```bash
npm run export:dev -- --source=chatgpt
# Output: Exported 247 conversations, atomized into 2,964 units
```

### Option B: Local Markdown Files

```bash
# Place markdown files in ./intake/local/
cp ~/Documents/notes/*.md ./intake/local/

npm run export:dev -- --source=local
# Output: Ingested 42 documents, atomized into 518 units
```

### Option C: Claude.app (requires browser)

```bash
npm run export:dev -- --source=claude
# Opens Playwright browser, navigates Claude.app, scrapes conversations
```

## Step 5: First Search

```bash
# Full-text search
npm run search "recursive data structure"

# Output:
# 1. [insight] Recursive structures benefit from...  (score: 0.92)
# 2. [code]    function traverse(node) { ...         (score: 0.87)
# 3. [decision] Chose recursive descent over...      (score: 0.81)
```

## Step 6: Enable Semantic Search (Phase 2)

```bash
# Generate embeddings for all units (requires OPENAI_API_KEY)
npm run generate-embeddings -- --yes
# Output: Generated embeddings for 2,964 units ($0.02 cost)

# Semantic search
npm run search:semantic "how do I handle deeply nested data"
# Finds semantically related content even without exact keyword matches
```

## Step 7: Launch Web UI

```bash
npm run web
# Open http://localhost:3000

# Explore:
# - Search tab: hybrid search with filters
# - Graph tab: D3 visualization of knowledge connections
# - Tags tab: browse by auto-generated tags
# - Settings tab: system stats and configuration
```

## Step 8: Enable Intelligence (Phase 3)

```bash
# Extract insights (requires ANTHROPIC_API_KEY)
npm run extract-insights all --save --parallel 3
# Output: Extracted 142 insights from 2,964 units ($0.89 cost)

# Auto-tag with context awareness
npm run smart-tag --limit 100 --save --parallel 4
# Output: Tagged 100 units with contextual tags ($0.20 cost)

# Discover relationships between units
npm run find-relationships --save
# Output: Found 87 relationships across 2,964 units ($1.20 cost)
```

## Expected Outcome

After completing onboarding, the caller has:

1. A populated SQLite database with atomized knowledge units
2. Full-text search across all conversations
3. (Optional) Semantic search via vector embeddings
4. (Optional) AI-extracted insights, smart tags, and relationship graph
5. A web UI for exploratory browsing and graph visualization

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|---------|
| `OPENAI_API_KEY not set` | Missing .env variable | Add key to .env file |
| `ECONNREFUSED on port 8000` | ChromaDB not running | Start ChromaDB or use FTS5-only mode |
| macOS permission popup | Apple Notes / Chrome access | Grant Terminal access in System Settings |
| `No conversations found` | Empty intake directory | Verify source files exist in ./intake/ |

## Related Documents

- `README.md` -- Full system overview
- `QUICKSTART.md` -- Quick start guide
- `CONTRIBUTING.md` -- Development setup
