# 01: Manifesto Reframed

**Atom ID:** manifesto-reframed
**Status:** ACTIVE
**References:** 2 cross-references in knowledge base corpus

---

## The Knowledge Reclamation Manifesto

### The Thesis

Every AI conversation you have generates knowledge. That knowledge evaporates. You spend hours with Claude working through a recursive data structure, or an afternoon with Gemini designing a deployment strategy, and afterward that knowledge exists only inside a vendor's chat interface -- unsearchable, unstructured, disconnected from every other conversation you have ever had.

This is not a minor inconvenience. This is a structural epistemological failure.

### The Failure Mode

Four failures compound:

**1. Captive knowledge.** Your conversations live behind vendor UIs with no export pathway. The few available exports (ChatGPT's JSON dump) give you raw data, not usable knowledge.

**2. Monolithic blobs.** A single conversation contains a database schema, a deployment decision, three code patterns, and a conceptual insight about state machines -- stored as one undifferentiated unit. Traditional tools (Notion, Obsidian, Logseq) require you to decompose conversations manually. This is the labor AI should automate.

**3. Siloed retrieval.** There is no way to query across sessions, platforms, or time. "What have I learned about recursive architectures across all my Claude conversations this quarter?" is an unanswerable question with existing tools.

**4. Invisible intelligence.** Conversations contain implicit insights -- recurring themes, latent contradictions, evolving understanding -- invisible without systematic analysis.

### The Response

This knowledge base addresses each failure with a dedicated subsystem:

| Failure | Subsystem | Method |
|---------|-----------|--------|
| Captive knowledge | Multi-source export engine | Playwright scraping, JSON parsing, filesystem reads |
| Monolithic blobs | Five-strategy atomizer | Content-aware decomposition into typed units |
| Siloed retrieval | Three-modal search | FTS5 + semantic + hybrid via RRF |
| Invisible intelligence | LLM intelligence layer | Insight extraction, smart tagging, relationship detection |

### The Commitment

This system treats every AI conversation not as disposable dialogue but as raw epistemological material awaiting decomposition into atomic units of reusable understanding. It is built for one person, not a team. It is local-first, not cloud-dependent. It is automated where possible, human-directed where necessary.

The operator's knowledge corpus is the most valuable intellectual asset they possess. No vendor should hold it hostage. No platform boundary should fragment it. No conversation should be forgotten.

### The Standard

The system is measured against four criteria:

1. **Export coverage:** All major AI platforms supported
2. **Atomization quality:** Units are typed, tagged, and self-contained
3. **Search relevance:** Hybrid search produces relevant results (MRR@10 > 0.7)
4. **Intelligence yield:** >30% of extracted insights are non-obvious

If the system fails any criterion, it is incomplete. If it meets all four, it has delivered on its promise.

## Related Documents

- `00_METHODOLOGY.md` -- The four operations in methodological detail
- `01-core-principles.md` -- Governing principles
- `04-precedent-analysis.md` -- Why no existing system addresses this problem
