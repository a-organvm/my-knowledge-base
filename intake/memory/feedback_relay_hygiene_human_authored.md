---
name: Human-authored relays go stale on concurrent ship — verify-before-act is structural
description: Session-start relays drafted by the user from mental model will go stale the moment any concurrent session ships work. SessionStart hygiene hook is the existing safeguard. Future fix is a relay-draft CLI.
type: feedback
originSessionId: e4d7bfeb-8e46-4516-9f37-84e1c754a1cd
---
## Root cause (verified 2026-04-25)

The 5-item catch-all relay opened both this session and the parallel sister-catch-all session. By the time either session began acting, three of its five items were already stale:

- DONE-475/476 collision — already resolved (commit `6aa7cd4`, this session, ~22:08).
- atomic-map plan source — restored from -v1 archive (this session, ~22:10).
- Becka McKay outreach — closed permanently in MEMORY.md (this session, before the relay was written).

Both sessions independently ran the hygiene check the SessionStart hook prescribes (`Memory = hypothesis, not fact. Any state recalled from a previous session MUST be verified against current disk state before acting.`) and caught the staleness. **The mechanism worked.** The vacuum did not radiate; no double-shipping occurred.

## What this is, and isn't

This is **not a process failure.** Both sessions verified before acting. The hygiene hook is doing its job.

This **is a structural property** of human-authored session relays: they are snapshots taken at author-time. The moment any concurrent session ships, the relay is partially stale. The user writes the relay from their mental model of "what's open right now"; that model cannot include in-flight or just-completed work in other sessions.

## Why human-authored relays will always go stale

- Sessions ship asynchronously. The user spins up a new lane in a different terminal; they do not stop the work in other lanes to update the new lane's framing.
- Mental models are slower to update than git logs. The user knows the full intent of work in flight; they often don't know which exact commit landed five minutes ago.
- Relays must be specific to be useful (file paths, IDs, repo names). The cost of relays being specific is the cost of going stale fast.

## Corrective: relay-draft CLI

Build `organvm relay draft` that constructs a session-start brief from current disk state, not the user's mental model. Sketch:

```bash
organvm relay draft \
  --lane catch-all \
  --exclude hokage-chess,elevate-align,personas \
  --since 2026-04-25T18:00 \
  > /tmp/relay.md
```

The CLI:
1. Reads recent IRF rows since `--since`.
2. Reads recent commits across the workspace since `--since`.
3. Reads MEMORY.md for entries marked `CLOSED`, `DO NOT CONTACT`, `BLOCKED`, etc., and **excludes them** from outreach/follow-up sections.
4. Reads the DONE counter and notes any orphan claims (claimed but not yet recorded in IRF).
5. Lists open vacuums radiating from recent completions.
6. Produces a relay markdown the user can copy verbatim into a new session prompt.

The user is still the author of the lane definition (what's in/out of scope). The CLI is the data source for what's *currently* in those lanes — it cannot drift behind concurrent ships because it reads disk at draft time.

Build this as a small tool under `~/Workspace/meta-organvm/organvm-corpvs-testamentvm/scripts/relay/draft.py` or as a sub-titan (Hermes — messenger between sessions). It is not Chronos/Mnemosyne/Gaia territory.

## How to apply (until the CLI exists)

Every session that opens with a multi-item relay MUST run hygiene against disk before drafting any plan. Concretely:

- Before acting on any item: read the relevant file, grep the IRF, check `git log --oneline -10` in the relevant repo.
- If a relay item names an action whose underlying state has shipped, drop the item and note it in the plan as "verified resolved."
- If a relay item contradicts a memory marker (`CLOSED`, `DO NOT CONTACT`, `BLOCKED`), the memory marker wins. Do not propagate the stale relay state into the new session's plan.
- Surface the verified-stale items back to the user as the first beat of the session, so the user knows their relay was partially stale and can update their tracking elsewhere.

## Cross-link

- Universal rule #12: Memory triggers reconciliation. Memory is hypothesis.
- Universal rule #57: Tracking instruments ≠ authority. Authority = triple-referenced disk locations.
- This memory extends both rules to human-authored session relays specifically.

## Vacuum radiation atom

The corrective `organvm relay draft` CLI is itself a vacuum radiating from this finding. File it as an OPEN atom for the keeper-tooling backlog when the titan-keeper plan is implemented.
