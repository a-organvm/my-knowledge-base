# Spec Extraction and Deduplication Plan

The `post-flood` directory contains 18 markdown files that branch from similar origins (e.g., sharing the same initial Q&A prompts) but diverge into different architectural discussions and specifications.

## User Review Required

> [!IMPORTANT]
> Because many files are branched variations (e.g., `Branch-·-Branch-...`), they contain exact duplicate Q&A blocks from their shared history. My plan is to **deduplicate** these blocks so you don't end up with 10 copies of the "Top-Down Refinement Pipeline Specification". 
> 
> I also plan to write these newly extracted files into a new subdirectory: `/Users/4jp/Workspace/meta-organvm/post-flood/atomic-specs/` to keep them organized and separate from the original branched files. 
> 
> Does this sound like the correct approach? Should any specific groupings (pairings) be strictly enforced, or is it okay if the script groups consecutive Q&A blocks that logically follow each other based on continuation prompts (like "Proceed")?

## Proposed Changes

### [Scripted Parsing & Extraction]

I will write a Python script (`/tmp/extract_specs.py`) to systematically process the files:

#### [NEW] `atomic-specs/` Directory
- The script will create this directory to store the clean, atomic sub-modules.

#### Logic for Extraction:
1. **Parse:** Read all 18 markdown files and split them into distinct conversational blocks using the `## Q:` and `## A:` delimiters.
2. **Title Generation:** Extract the first `#` or `##` heading from the AI's response to use as the title for the new markdown file.
3. **Grouping (Pairing):** If a block is an immediate continuation of the previous block (e.g., the User prompt was just "Proceed" or "..."), the script will pair it with the preceding block. This ensures that "implied specs" that took multiple conversational turns to generate remain cohesive in a single markdown file.
4. **Deduplication:** Hash the content of each extracted spec. If the exact same spec (e.g., the base "Virtual System Architecture" model) was found in multiple branched files, it will only be written to disk once.
5. **Output:** Each unique, cohesive spec will be written to `post-flood/atomic-specs/[Sanitized-Title].md`.

## Verification Plan

### Automated Tests
- The Python script will output a logging summary of how many blocks were parsed, how many unique specs were identified, and what files were created.
- Ensure no data is lost by doing a sanity check over the extracted spec titles.

### Manual Verification
- Review the contents of the `atomic-specs` folder to ensure the specs are properly isolated and readable.
