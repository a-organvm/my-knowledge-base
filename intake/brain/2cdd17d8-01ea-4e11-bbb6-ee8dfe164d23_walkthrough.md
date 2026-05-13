# Post-Flood Q→A Extraction Walkthrough

## What Was Done

Extracted **83 unique specification documents** from 18 branched ChatGPT conversation transcripts in `post-flood/`.

### Process

1. **Parsed** all 18 source files at `## Q:` / `## A:` markers → found **176 Q→A pairs**
2. **Deduplicated** by content hash (many files were branches sharing early Q/A) → removed **92 duplicates**  
3. **Filtered** 1 trivial stub → **83 substantive answers**
4. **Generated** clean standalone `.md` files with:
   - YAML frontmatter (`title`, `date_extracted`, `source_file`, `source_qa_index`, `prompt`, `tags`, `status`)
   - Auto-derived title from first heading or bold text
   - Auto-derived domain tags from 18-keyword vocabulary
   - Clean body with ChatGPT artifacts and branch markers stripped

### Output Structure

Each document in `post-flood/` looks like:

```yaml
---
title: "Adaptive System Variable & Structural Evolution Framework"
date_extracted: "2026-03-15"
source_file: "Name-and-Structure-Changes.md"
source_qa_index: 3
prompt: "provide comprehensive theoretical specification design documet"
tags: [architecture, events, evolution, governance, ...]
status: extracted
---
```

Followed by the clean answer body.

### File Layout

| Location | Contents |
|----------|----------|
| `post-flood/*.md` | 83 clean extracted documents |
| `post-flood/archive_original/*.md` | 18 original conversation transcripts |

### Script

Extraction script: `/tmp/extract_qa_docs.py`
