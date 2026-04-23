#!/usr/bin/env python3
"""Layer 3: Status inference for prompt atoms.

Looks up the assistant response to each user prompt in the DB and infers
whether the prompt was fulfilled: DONE, PARTIAL, FAILED, OPEN, or DEFERRED.

Usage: python3 scripts/infer_prompt_status.py
"""

import json
import os
import sqlite3
from collections import defaultdict
from pathlib import Path

DB_PATH = Path.home() / "Workspace/organvm/my-knowledge-base/db/knowledge.db"
ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)

DONE_SIGNALS = [
    "here is", "here's", "i've created", "i've updated", "i've added",
    "i've fixed", "i've implemented", "successfully", "completed",
    "done", "created the", "updated the", "added the", "fixed the",
    "here are the", "the changes have been", "committed", "deployed",
    "```",  # code block = likely produced output
]

FAILED_SIGNALS = [
    "i can't", "i cannot", "unable to", "unfortunately",
    "i don't have access", "error occurred", "not possible",
    "i'm not able", "beyond my capabilities", "i apologize",
]

DEFERRED_SIGNALS = [
    "next session", "follow up", "follow-up", "later", "todo",
    "we'll come back", "in a future", "we can revisit",
    "when you're ready", "as a next step",
]

PARTIAL_SIGNALS = [
    "i'll need to", "let me know if", "remaining steps",
    "we can also", "additionally you could", "you may also want",
    "there are a few more", "the rest can be", "partial",
]


def classify_response(response: str) -> str:
    if not response or len(response.strip()) < 20:
        return "OPEN"

    lower = response[:1000].lower()

    # Check if response is just a question back
    sentences = [s.strip() for s in response[:500].split(".") if s.strip()]
    if sentences and all(s.endswith("?") for s in sentences[:3] if s):
        return "OPEN"

    # Check signals in priority order
    for signal in FAILED_SIGNALS:
        if signal in lower:
            return "FAILED"

    for signal in DEFERRED_SIGNALS:
        if signal in lower:
            return "DEFERRED"

    for signal in PARTIAL_SIGNALS:
        if signal in lower:
            return "PARTIAL"

    # Explicit done signals
    for signal in DONE_SIGNALS:
        if signal in lower:
            return "DONE"

    # Long substantive response without negative signals = likely done
    if len(response.strip()) > 200:
        return "DONE"

    return "OPEN"


def main():
    print("Loading DB turns index...")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Build thread_id -> sorted turns index
    cursor.execute("SELECT thread_id, turn_index, role, content FROM chat_turns ORDER BY thread_id, turn_index")
    thread_turns = defaultdict(list)
    for thread_id, turn_index, role, content in cursor:
        thread_turns[thread_id].append((turn_index, role, content))
    conn.close()

    print(f"  Indexed {sum(len(v) for v in thread_turns.values())} turns across {len(thread_turns)} threads")

    # Load atoms
    print("Loading prompt atoms...")
    atoms = []
    with open(ATOMS_PATH) as f:
        for line in f:
            if line.strip():
                atoms.append(json.loads(line))
    print(f"  Loaded {len(atoms)} atoms")

    # Infer status for each atom
    status_counts = defaultdict(int)
    provider_status = defaultdict(lambda: defaultdict(int))
    domain_status = defaultdict(lambda: defaultdict(int))

    for atom in atoms:
        thread_id = atom.get("source", {}).get("thread_id", "")
        turn_index = atom.get("source", {}).get("turn_index", -1)

        if not thread_id or thread_id not in thread_turns:
            atom["status"] = "OPEN"
            status_counts["OPEN"] += 1
            continue

        turns = thread_turns[thread_id]

        # Find assistant response after this turn
        response_parts = []
        found_user_turn = False
        for t_idx, t_role, t_content in turns:
            if t_idx <= turn_index:
                continue
            if t_role == "user":
                break  # Next user turn = end of response
            if t_role == "assistant":
                response_parts.append(t_content)
            # Skip tool turns

        response = " ".join(response_parts)
        status = classify_response(response)

        atom["status"] = status
        status_counts[status] += 1

        provider = atom.get("source", {}).get("provider", "unknown")
        domain = atom.get("domain", "general")
        provider_status[provider][status] += 1
        domain_status[domain][status] += 1

    # Write updated atoms
    tmp = str(ATOMS_PATH) + ".tmp"
    with open(tmp, "w") as f:
        for atom in atoms:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.rename(tmp, ATOMS_PATH)

    # Stats
    print(f"\n{'=' * 60}")
    print(f"LAYER 3: STATUS INFERENCE RESULTS")
    print(f"{'=' * 60}")
    print(f"\nOverall status distribution:")
    total = sum(status_counts.values())
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {status:10s}: {count:6d} ({100*count/total:.1f}%)")

    print(f"\nBy provider:")
    for provider in sorted(provider_status):
        counts = provider_status[provider]
        print(f"  {provider}:")
        for status, count in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    {status:10s}: {count}")

    print(f"\nBy domain:")
    for domain in sorted(domain_status, key=lambda d: -sum(domain_status[d].values())):
        counts = domain_status[domain]
        total_d = sum(counts.values())
        open_d = counts.get("OPEN", 0)
        print(f"  {domain:15s}: {total_d:5d} total, {open_d:4d} OPEN ({100*open_d/max(total_d,1):.0f}%)")

    # Top P0 OPEN prompts
    p0_open = [a for a in atoms if a.get("priority") == "P0" and a.get("status") == "OPEN"]
    if p0_open:
        print(f"\nTop P0 OPEN prompts ({len(p0_open)} total):")
        for a in p0_open[:15]:
            print(f"  [{a['domain']:12s}] {a['title'][:70]}")

    print(f"\nOutput: {ATOMS_PATH}")


if __name__ == "__main__":
    main()
