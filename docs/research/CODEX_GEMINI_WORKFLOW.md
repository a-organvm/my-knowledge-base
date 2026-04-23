# Workflow SOP: Model Delegation (Codex vs. Gemini)

## Objective
Establish a high-signal, efficient workflow that leverages the strengths of specific AI architectures: **Codex/Copilot/Cursor** for low-level execution and **Gemini/Claude** for high-level reasoning and research.

## Delegation Logic

### 1. Codex: The Mechanical Arm
**Best For:**
- Boilerplate generation (components, CSS, types).
- Simple refactoring (renaming, moving logic).
- Unit test scaffolding.
- Routine lint fixes and style adjustments.
- Autocompleting established patterns.

**Workflow Pattern:**
- Use directly in the IDE.
- Feed it short, concrete prompts or rely on context-aware autocompletion.
- "Mechanical Dispatch": Don't waste reasoning tokens on tasks that can be autocompleted.

### 2. Gemini: The Strategic Head
**Best For:**
- System architecture design.
- Bug root-cause analysis across multiple files.
- Researching new technologies or APIs.
- Planning complex feature implementations.
- Auditing existing code for design flaws.

**Workflow Pattern:**
- Use for the **Research** and **Strategy** phases of the development lifecycle.
- Provide full context (file trees, package.json, documentation).
- "Research Dispatch": Use Gemini to find the "What" and "Why" before using Codex for the "How."

## Practical Example: Adding a New API Endpoint
1. **Gemini:** "Research the best way to implement a paginated SQLite endpoint for Knowledge Units. Propose the schema and API design."
2. **Strategy:** Review Gemini's proposal and finalize the architecture.
3. **Codex:** "Create the TypeScript interface for this endpoint based on the proposal. Now, write the Express route handler. Now, write the test case."
