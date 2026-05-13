---
name: Research depth, alive systems, and the hierarchy trap
description: Recurring failure pattern — shallow research, dead files, nested directories. Must be fixed permanently.
type: feedback
originSessionId: e667bfc4-92bc-4867-836d-1c3cd55b4074
---
Three recurring failures that must NEVER happen again:

## 1. SHALLOW RESEARCH
When the user says "research it" or "like NixOS" — that is NOT "do 3 web searches and skim Wikipedia." It means: find the PhD thesis, read the actual source, study the competitors (Nix, Guix, Dhall, CUE, Jsonnet, Terraform, Pulumi, Bazel), extract the COMMON PRINCIPLES across all of them, and THEN design something that IS the ideal form. Research means DEPTH. Four links is abysmal.

**Why:** The user is the architect of macro thought. They point at the moon. I keep describing their finger because I don't actually understand the domain deeply enough. Shallow research produces shallow implementations.

**How to apply:** When directed to research a domain, spend the research tokens BEFORE writing any code or creating any files. Use multiple searches, read actual documentation (not summaries), find the primary sources (theses, RFCs, design docs), study the competitors. Present the landscape FIRST. Design from principles SECOND. Implement LAST.

## 2. DEAD FILES
Every file created must be ALIVE — versioned (semver), validated (schema/semgrep), variable-resolved (environment variables, templating), and enforceable. A static TOML that nobody reads or validates is not a system — it's a note. If a file doesn't have enforcement, it's not governance, it's a wish.

**Why:** The user keeps finding that things I create don't follow the rules those very things declare. system.toml declares naming protocols but isn't itself named by those protocols. The pattern: the cobbler's children have no shoes.

**How to apply:** Before creating ANY configuration/governance/declaration file, ask: who validates this? How is it versioned? What enforces compliance? If the answer is "nothing" — design the enforcement FIRST, then create the file.

## 3. THE HIERARCHY TRAP
NEVER create nested directory hierarchies to represent structure. Structure belongs in DATA (attributes in flat files), not in the filesystem. If making a subdirectory, that's almost always wrong — make an attribute in a declaration file instead.

**Why:** The user has corrected this pattern repeatedly across multiple sessions. Every time structure is needed, the instinct is to create directories. NixOS proved that flat stores + declarative attributes are superior. Directories are dumb. Data is smart.

**How to apply:** When tempted to `mkdir`, instead add an attribute to a flat file. The filesystem holds FILES, not hierarchy. One level deep maximum. The evaluator/engine DERIVES structure from flat declarations.
