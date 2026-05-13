---
name: Suggestions point to ideal forms
description: User suggestions are pointers to ideal forms, not literal implementation specs — always ask "what is the best version of this?" before building
type: feedback
originSessionId: eb876139-2eb0-4c33-a815-2ce4abdb2467
---
When the user suggests something (e.g., "email triage"), the suggestion is NOT a literal instruction to implement exactly what was described. It is a pointer toward an ideal form — the best possible version of that concept.

**Why:** The user explicitly called this out after the mail-triage LaunchAgent (opening Mail.app every 30 minutes) froze their 16GB machine repeatedly. The suggestion "email triage" pointed toward *intelligent inbox filtering that runs silently* — not a resource-heavy GUI app polling on a timer. The gap between "what was said" and "what was built" was the gap between the ideal and a bad implementation.

**How to apply:** Before implementing any suggestion, stop and ask: "What is the ideal form of this?" Challenge the implementation path — not just whether it works, but whether it's the *right shape*. A suggestion about email triage should yield server-side Gmail filters, not a local LaunchAgent. A suggestion about file organization should yield a classifier, not a cron job that moves files. The suggestion is the seed; the ideal form is the tree. Build the tree, not a stick that looks like the seed.
