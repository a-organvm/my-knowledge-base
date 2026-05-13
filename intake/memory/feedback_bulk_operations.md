---
name: Bulk operation patterns
description: Proven patterns for large-scale file edits, search-replace, and agent delegation
type: feedback
---

Effective patterns for bulk operations in this environment:

**Why:** Learned through trial during organvm multi-repo deployments (40+ files, 100KB+ transcripts).

**How to apply:**
- For bulk search-replace across many markdown files: use `replace_all=true` with the Edit tool (small scale) or a Python `os.walk` script (large scale, 40+ files)
- For files >100KB (genesis transcripts): delegate to background agents to avoid blocking the main context
- Always verify with Grep after replacements to confirm zero old strings remain
