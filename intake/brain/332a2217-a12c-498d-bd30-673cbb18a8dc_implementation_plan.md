# Goal Description

The project aims to establish a formalized ecosystem-wide Markdown hygiene enforcement mechanism. As AI agents and humans constantly generate and append documentation in the `meta-organvm` and `system-system--system` framework, structural rot accumulates (e.g., Markdown linting errors like MD025, MD036, MD040). This plan introduces the rules, automation configs, and remediation scripts to permanently halt this type of issue.

## User Review Required

> [!IMPORTANT]
> The auto-remediation script will use heuristic pattern matching (Regex) to modify markdown files. While it targets typical AI-generation flaws (replacing `**Bold Section**` lacking newlines with `### Bold Section`, replacing duplicate `H1` tags with `H2`, etc.), please review the proposed script boundaries below to ensure it aligns with your aesthetic standards. 

> [!NOTE]
> Node tools like `npx` do not appear fully linked in the base automation shell, so the proposed remediation approach relies strictly on Python 3 for maximum compatibility across your environments. 

## Proposed Changes

### Governance & Standards

#### [NEW] `meta-organvm/praxis-perpetua/standards/SOP--markdown-hygiene-and-linting.md`
- Creates a formal SOP definition that instructs all operational agents on mandatory markdown structuring (Single H1 constraint, strict code-fence language tagging, prohibition on bold-as-headings, and strict trailing newlines).

---

### Configuration & Tooling

#### [NEW] `meta-organvm/.markdownlint.yaml`
- Defines the ecosystem standard config file for `markdownlint`. Even if run locally via your IDE, it will source this global configuration to unify the warning standards. 

#### [NEW] `meta-organvm/scripts/hygiene/md_lint_fixer.py`
- A zero-dependency Python script designed to crawl specified `.md` files or directories and perform targeted "find-and-replace" transformations for the most common violations:
    1. Replaces line-isolated `**Text**` with `### Text`
    2. Appends dummy `python` or `markdown` syntax blocks to empty ` ``` ` blocks
    3. Handles trailing newline issues.
    4. Converts secondary `# Headings` to `## Headings`.

---

### Immediate Target Remediation

The `md_lint_fixer.py` script will be run across the three files you identified to immediately resolve their IDE warnings. 

## Verification Plan

### Automated Tests
- The Python script will be run against the `post-flood/archive_original` files listed in the prompt to ensure the `MD025`, `MD036`, `MD041`, etc. errors disappear.

### Manual Verification
- You will be asked to reload the targeted files in your IDE to verify that the linting error UI annotations have successfully cleared without compromising the content payload.
