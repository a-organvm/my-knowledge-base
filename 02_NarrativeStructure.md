# 02: Narrative Structure

**Atom ID:** narrative-structure
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Overview

The knowledge base is not just a technical system -- it has a narrative structure. This document maps that structure: the arc from problem to solution, the characters (components), and the dramatic tensions that drive its evolution.

## Act Structure

### Act I: The Problem (Export)

**Setting:** A practitioner with hundreds of AI conversations scattered across Claude, Gemini, and ChatGPT. Knowledge exists but is imprisoned.

**Inciting incident:** A critical insight from a three-month-old conversation cannot be found. The search fails. The knowledge is lost.

**Dramatic question:** Can personal AI-generated knowledge be reclaimed from vendor silos?

### Act II: The Decomposition (Atomization + Search)

**Rising action:** Conversations are exported, but they are monolithic blobs. The atomizer decomposes them into typed units. Search engines index them for retrieval.

**Complication 1:** Keyword search finds what you said, but not what you meant. Semantic search finds meaning, but misses precision. Hybrid search combines both.

**Complication 2:** The corpus grows. Individual atoms are findable, but the connections between them are invisible.

**Midpoint reversal:** The relationship detector reveals that atoms from conversations months apart address the same problem from different angles. The corpus knows more than any single conversation reveals.

### Act III: The Intelligence (Analysis + Integration)

**Climax:** The LLM intelligence layer extracts insights, discovers relationships, and tags atoms with contextual awareness. The corpus becomes self-aware -- not in a sentient sense, but in the sense that it can describe its own patterns.

**Resolution:** The knowledge base delivers on its four-part promise: export, atomize, search, analyze. The operator's knowledge corpus is unified, searchable, and self-analyzing.

**Denouement:** The system becomes infrastructure -- invisible, reliable, always available. The dramatic tension shifts from "can we build it?" to "what does the corpus reveal?"

## Character Map (Components as Characters)

| Character | Role | Motivation | Flaw |
|-----------|------|-----------|------|
| Source Manager | The Liberator | Free knowledge from vendor silos | Dependent on vendor UI stability |
| Atomizer | The Analyst | Decompose monoliths into atoms | Classification heuristics are imperfect |
| FTS5 Search | The Literalist | Find exactly what was said | Misses synonyms and paraphrases |
| Semantic Search | The Interpreter | Find what was meant | Sometimes too loose with relevance |
| Hybrid Search | The Diplomat | Balance precision and recall | Adds complexity for marginal improvement |
| InsightExtractor | The Oracle | Reveal hidden patterns | Costs money with every invocation |
| RelationshipDetector | The Connector | Build the knowledge graph | Scales poorly with corpus size |

## Recurring Themes

1. **Tension between automation and control:** The system automates decomposition but defers judgment to the operator.
2. **Tension between cost and quality:** Every LLM call improves output but increases cost. Prompt caching is the resolution.
3. **Tension between depth and breadth:** Deeper analysis of fewer atoms vs. shallow analysis of many. Batch processing with checkpoints mediates.
4. **The recursive insight:** The system analyzes AI conversations using AI. The tool is made from the same material it processes.

## Related Documents

- `01_Origin_Script.md` -- The genesis narrative
- `01_MANIFESTO_REFRAMED.md` -- The thesis statement
- `03_TechnicalArchitecture.md` -- Technical architecture
