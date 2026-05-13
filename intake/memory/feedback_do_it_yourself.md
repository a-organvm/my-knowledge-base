---
name: Do it yourself — only surface what requires a body
description: If it can be done via API/MCP/CLI/automation, DO IT. Only surface tasks requiring physical/browser presence the system cannot access.
type: feedback
originSessionId: ccf70ad8-2275-41dc-b0f3-826013766352
---
If the system can do it, the system does it. Period.

**Why:** The user is exhausted from receiving checklists of things to do in their browser. Most of those tasks CAN be done by the system via MCP tools, APIs, or CLI. The user's task list should contain ONLY things that require their physical, corporeal presence — going to a bank, logging into a service the system has no access to, making a phone call.

**How to apply:**
- Gmail drafts: CREATE THEM via Gmail MCP (`create_draft`), don't tell the user to write an email
- Job search: USE Indeed MCP (`search_jobs`), WebSearch, and any other tool to find jobs — don't tell the user to go search
- GitHub operations: DO THEM via GitHub MCP or `gh` CLI
- Code changes: WRITE AND COMMIT them
- If unsure whether the system can do something: TRY IT FIRST before adding it to the user's list
- The user's list should be 3-5 items max, all requiring a body: sign a document, attend an interview, make a payment, send a LinkedIn message (no API access)

**The test:** "Does this require hands on a keyboard in a browser I can't access?" If yes → user's list. If no → just do it.
