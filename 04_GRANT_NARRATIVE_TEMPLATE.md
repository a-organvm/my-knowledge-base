# 04: Grant Narrative Template

**Atom ID:** grant-narrative-template
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## Purpose

This template provides a reusable structure for grant proposals that reference the knowledge base as a component of a larger project. It is pre-populated with the system's capabilities, evidence, and positioning language.

## Template

---

### Project Title

[Your Project Title]: Leveraging AI Conversation Knowledge Infrastructure for [Domain]

### Abstract (250 words max)

[Opening sentence about the domain problem.]

This project builds on an existing epistemological infrastructure -- the My Knowledge Base system -- that converts AI conversations into durable, searchable, interconnected knowledge. The system currently supports four AI platforms (Claude, Gemini, ChatGPT, and local documents), produces typed atomic knowledge units from conversations, and provides three-modal search (full-text, semantic, and hybrid) with LLM-powered intelligence extraction.

[Your project's specific contribution: how it extends or applies this infrastructure.]

The system has been validated with [corpus size] conversations producing [unit count] atomic units, achieving search relevance (MRR@10) of [value] and intelligence extraction novelty rates exceeding [value]%.

[Expected impact statement.]

### Problem Statement

[Describe the specific problem your project addresses. Reference the four failures from the knowledge base methodology:]

1. Captive knowledge locked in proprietary platforms
2. Monolithic content lacking systematic decomposition
3. Siloed retrieval preventing cross-source discovery
4. Invisible intelligence buried in unanalyzed corpora

### Existing Infrastructure

The applicant has developed and validated a knowledge base system with the following capabilities:

| Capability | Status | Evidence |
|-----------|--------|----------|
| Multi-source export | Production | 4 AI platforms + local files |
| Five-strategy atomization | Production | [N] atomic units generated |
| Three-modal search (FTS + semantic + hybrid) | Production | MRR@10 > 0.7 |
| LLM intelligence extraction | Production | 90% cost savings via prompt caching |
| REST API (38 endpoints) | Production | Documented and tested |
| Web UI with graph visualization | Production | React + D3.js |

### Methodology

[Describe your project's methodology. Reference the four operations:]

1. **Export:** [How your project extends source coverage]
2. **Atomization:** [How your project refines or extends atomization]
3. **Retrieval:** [How your project uses or extends search capabilities]
4. **Intelligence:** [How your project uses or extends LLM analysis]

### Technical Approach

[Architecture diagram and technical details. Reference `docs/ARCHITECTURE.md` for the base system architecture.]

### Budget Justification

| Category | Amount | Justification |
|----------|--------|---------------|
| Personnel | $[X] | [Role and effort] |
| API costs | $[X] | Estimated at $[Y] per 1,000 operations with prompt caching |
| Infrastructure | $[X] | [Hosting, storage, compute] |
| Equipment | $[X] | [If applicable] |
| **Total** | **$[X]** | |

### Timeline

| Phase | Duration | Deliverables |
|-------|----------|-------------|
| 1 | [X months] | [Specific deliverables] |
| 2 | [X months] | [Specific deliverables] |
| 3 | [X months] | [Specific deliverables] |

### Evaluation Plan

[How success will be measured. Reference the system's existing metrics:]

- Search relevance (MRR@10)
- Atomization quality (type distribution, self-containment)
- Intelligence novelty rate
- Cost per operation
- [Your project-specific metrics]

### Dissemination

[How results will be shared. The knowledge base is MIT-licensed and can be referenced as open-source infrastructure.]

---

## Usage Notes

1. Replace all `[bracketed placeholders]` with project-specific content
2. Adjust budget categories to match the grantor's requirements
3. Reference specific grant program priorities in the problem statement
4. Include letters of support if applicable
5. Attach `benchmark-report.md` as supporting evidence

## Related Documents

- `benchmark-report.md` -- Performance evidence
- `literature-review.md` -- Academic grounding
- `04-precedent-analysis.md` -- Competitive landscape
- `docs/ARCHITECTURE.md` -- Technical architecture
