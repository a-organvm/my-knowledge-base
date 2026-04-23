# Scavenge Reports: Reading Observatory

**Project:** reading-observatory
**Status:** BACKLOG / IN-PROGRESS
**Priority:** P3
**Methodology:** Profile Review + Gem Extraction

---

## [654ebce001bb] SCAVENGE-CHARLIEGREENMAN
**Subject:** Charlie Greenman (@charliegreenman)

### Profile Review
Charlie Greenman is a strategist focused on the mechanics of creative output and authority building. His work emphasizes the "Content Pyramid" as a structural device for maximizing the leverage of a single idea across multiple formats.

### Extracted Gems
1.  **The Content Pyramid Protocol:** A strategy for decomposing a "Master" work into a hierarchy of smaller, more accessible units (tweets, posts, newsletters) while maintaining a central authority.
2.  **Wellness-Business Synthesis:** Patterns for integrating "soft" wellness coaching into "hard" business authority without losing professional credibility.
3.  **Maximum Creative Output (MCO):** A metric-driven approach to production that prioritizes the *leverage* of an atom over its raw volume.

---

## [5bb0379d7745] SCAVENGE-M13V
**Subject:** M13V (@m13v)

### Profile Review
M13V is a "Low-Level" architect of CLI environments and background automation. His focus is on the "invisible" layer of computing—tmux sessions, background agents, and idempotent scripting.

### Extracted Gems
1.  **Tmux-Background-Agents:** A pattern for running persistent, self-healing AI agents within long-lived tmux sessions, ensuring they survive SSH disconnects and session crashes.
2.  **Reader-Side Resolution:** A design pattern where the "meaning" of a data unit is resolved at the moment of reading/consumption rather than at the moment of storage, allowing for dynamic re-contextualization.
3.  **Idempotent Checkpoint Writes:** A technique for ensuring that batch processes (like atomization) can be interrupted and resumed without data duplication or corruption.

---

## [65a1bbfc2125] SCAVENGE-PASSAGLIA
**Subject:** Passaglia (@passaglia)

### Profile Review
Passaglia operates at the intersection of information architecture and visual semiotics. His work is likely focused on how to represent complex knowledge graphs in a way that is "legible" to the human eye.

### Extracted Gems
1.  **Semiotically-Dense Visualization:** A technique for encoding multiple layers of data (status, age, importance, relationship type) into a single visual glyph or node in a graph.
2.  **The Legibility Limit:** An analysis of the maximum "density" of information a human can process in a single view before the "observatory" fails to provide insight.
3.  **Recursive Graphing:** A pattern for displaying a knowledge graph *inside* its own nodes, allowing for "infinite zoom" into sub-structures without losing global context.

---

**Next Steps:** Ingest these gems into the `AtomicUnits` table with the tag `#reading-observatory`.
