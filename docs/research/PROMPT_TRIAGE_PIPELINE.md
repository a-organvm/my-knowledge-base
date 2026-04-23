# Architectural Plan: Prompt Triage & Execution Pipeline

## The Problem
- **Corpus Size:** 31,761 atoms extracted from 10 months of prompts.
- **Backlog:** 81.9% (25,972) UNREVIEWED.
- **Context Loss:** Directives vanish between sessions. Fresh starts lead to redundant work and missed requirements.

## The Goal
Triage the entire corpus to surface persistent directives, key architectural decisions, and unresolved tasks.

## 1. Pipeline Architecture

### Phase A: Extraction & Normalization
- **Source:** Existing `intake/` and `atomized/` directories.
- **Process:** Ensure all atoms have a stable ID, timestamp, and source-session reference.

### Phase B: Automated Classification (LLM-Based)
- **Model:** Use a fast LLM (e.g., GPT-4o-mini or Gemini 1.5 Flash).
- **Taxonomy:**
  - **Directive:** Explicit instruction for a future state (e.g., "Always use Vanilla CSS").
  - **Decision:** Architectural "Why" (e.g., "Switched to SQLite for better local indexing").
  - **Context:** Reference data (e.g., "Here is my resume").
  - **Chitchat:** Disposable conversation filler.
- **Output:** A tagged JSON metadata layer for each atom.

### Phase C: The Triage Interface (The "Tinder for Prompts")
- **UI:** A simple web or CLI tool that presents one atom at a time.
- **Actions:** 
  - **KEEP (High Signal):** Promote to a "Canonical Directives" file.
  - **TODO (Unresolved):** Add to the Task Queue (JSON/YAML).
  - **DISCARD (Low Signal):** Mark as reviewed and hide.
  - **BATCH DISCARD:** Automatically hide all "Chitchat" tags.

### Phase D: Session Integration (The "Recursive Handoff")
- **Mechanism:** Modify the agent's start-of-session script to:
  1. Load `CANONICAL_DIRECTIVES.md`.
  2. Load `ACTIVE_TASK_QUEUE.yaml`.
  3. Present a summary of the 5 highest-priority pending directives.

## 2. Implementation Roadmap

| Milestone | Task | Priority |
|-----------|------|----------|
| **0.1** | Script to batch-tag atoms using an LLM. | High |
| **0.2** | CLI tool for rapid Review/Triage. | High |
| **0.3** | Automated generation of a `SESSION_BACKLOG.md` on every startup. | Medium |
| **1.0** | Full integration with the ORGANVM `conductor` ecosystem. | Medium |

## 3. Success Metrics
- **Review Percentage:** Increase from 18.1% to >90%.
- **Context Density:** Reduction in "Fresh Start" turns by 40%.
- **Directive Persistence:** 100% of "KEEP" tagged directives are present in every subsequent session context.
