#!/usr/bin/env python3
"""Triage prompt atoms into CONVERSATION_OPS vs DELIVERABLE_REQUESTS.

CONVERSATION_OPS are prompts completed by the conversation itself —
questions, git ops, reviews, listing/searching, explanations, debugging,
config changes. These get auto-marked VERIFIED_DONE.

DELIVERABLE_REQUESTS require something to exist after the conversation
ends — creation, content generation, system design. These stay NEEDS_REVIEW.

Reads prompt-atoms.jsonl for the prompt corpus.
Connects to knowledge.db READ-ONLY for assistant responses when needed.
Writes classification results to review-results.db.

Usage: python3 scripts/ops_triage.py
"""

import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# --- Paths ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)
KNOWLEDGE_DB = PROJECT_ROOT / "db" / "knowledge.db"
REVIEW_DB = PROJECT_ROOT / "db" / "review-results.db"


# --- Classification patterns ---

# Each entry: (pattern_name, compiled_regex)
# Patterns are checked against lowercased prompt content.

CONVERSATION_OPS_PATTERNS = [
    # Questions — the answer IS the deliverable
    ("question:what_is", re.compile(r"^what\s+(is|are|was|were|do|does|did)\b")),
    ("question:how_does", re.compile(r"^how\s+(does|do|did|can|should|would|is|are|to)\b")),
    ("question:can_you_explain", re.compile(r"(can you|could you|please)\s+(explain|clarify|describe|elaborate)")),
    ("question:what_does_mean", re.compile(r"what\s+does\s+.+\s+mean")),
    ("question:why", re.compile(r"^why\s+(is|are|does|do|did|would|can|should)\b")),
    ("question:which", re.compile(r"^which\s+(one|is|are|do|should|would)\b")),
    ("question:where", re.compile(r"^where\s+(is|are|does|do|did|can|should)\b")),
    ("question:is_it", re.compile(r"^(is|are|does|do|did|will|would|should|can|could)\s+(it|this|that|there|the|we|i)\b")),
    ("question:generic", re.compile(r"\?\s*$")),

    # Git ops — the operation IS the outcome
    ("git:commit", re.compile(r"\b(commit|git commit)\b.*\b(push|and push|then push)?\b")),
    ("git:push", re.compile(r"\b(push|git push)\b")),
    ("git:pull", re.compile(r"\b(pull|git pull|fetch)\b")),
    ("git:merge", re.compile(r"\b(merge|git merge|rebase)\b")),
    ("git:status", re.compile(r"\b(git status|git diff|git log|git show|git stash)\b")),
    ("git:branch", re.compile(r"\b(checkout|switch branch|git branch)\b")),

    # Review/audit — the review IS the deliverable
    ("review:review", re.compile(r"\b(review|audit|check|verify|validate|inspect)\s+(this|the|my|our|these|that|those|it)\b")),
    ("review:look_at", re.compile(r"\b(look at|look into|take a look|glance at)\b")),
    ("review:whats_wrong", re.compile(r"\bwhat'?s\s+(wrong|broken|failing|the (error|issue|problem|bug))\b")),

    # Listing/searching — the output IS the deliverable
    ("listing:list", re.compile(r"\b(list|enumerate|show)\s+(all|the|every|me|my|each)\b")),
    ("listing:find", re.compile(r"\bfind\s+(all|the|every|any|where|which|me)\b")),
    ("listing:show_me", re.compile(r"\bshow\s+me\b")),
    ("listing:search", re.compile(r"\bsearch\s+(for|the|in|through|across)\b")),
    ("listing:count", re.compile(r"\b(count|how many|tally)\b")),
    ("listing:whats_in", re.compile(r"\bwhat'?s\s+(in|inside|under|at)\b")),

    # Explanations — the explanation IS the deliverable
    ("explain:explain", re.compile(r"\b(explain|describe|walk\s+me\s+through|summarize|break\s+down)\b")),
    ("explain:tell_me", re.compile(r"\btell\s+me\s+(about|how|what|why|more)\b")),
    ("explain:meaning", re.compile(r"\b(what\s+does|meaning\s+of|definition\s+of)\b")),

    # Debugging — the diagnosis IS the deliverable
    ("debug:why_failing", re.compile(r"\bwhy\s+(is|are|does|do)\s+(this|it|that|the)\s+(failing|broken|not working|crashing|erroring)\b")),
    ("debug:error", re.compile(r"\b(what'?s\s+this\s+error|error\s+message|stack\s+trace|traceback)\b")),
    ("debug:debug", re.compile(r"^debug\b")),
    ("debug:fix_error", re.compile(r"\bfix\s+(this|the)\s+(error|bug|issue|problem|crash)\b")),
    ("debug:troubleshoot", re.compile(r"\b(troubleshoot|diagnose)\b")),

    # Config/settings — the change IS the outcome
    ("config:set", re.compile(r"\bset\s+\w+\s+to\b")),
    ("config:configure", re.compile(r"\b(configure|reconfigure|enable|disable|toggle|turn\s+(on|off))\b")),
    ("config:update_setting", re.compile(r"\b(update|change|modify)\s+(the\s+)?(setting|config|configuration|option|preference)\b")),

    # Navigation/status — informational
    ("nav:cd", re.compile(r"^(cd|ls|pwd|cat|head|tail)\s")),
    ("nav:read_file", re.compile(r"\bread\s+(the\s+)?(file|contents|source)\b")),
    ("nav:open", re.compile(r"^open\s+")),
    ("nav:run", re.compile(r"^run\s+(the\s+)?(test|check|lint|build|script|command)\b")),

    # Conversational directives — feedback within the conversation
    ("conv:more_detail", re.compile(r"^(more\s+detail|be\s+more\s+(specific|detailed|verbose)|expand\s+on)\b")),
    ("conv:shorter", re.compile(r"^(shorter|more\s+concise|brief|tl;?dr)\b")),
    ("conv:different_approach", re.compile(r"\b(try\s+(a\s+)?different|another\s+approach|alternative|instead)\b")),
    ("conv:continue", re.compile(r"^(continue|go\s+on|keep\s+going|proceed|go\s+ahead|next)\b")),
    ("conv:redo", re.compile(r"^(redo|try\s+again|one\s+more\s+time|again)\b")),
    ("conv:acknowledgement", re.compile(r"^(ok|okay|yes|yeah|yep|sure|got\s+it|right|correct|exactly|perfect|great|good|thanks|thank\s+you|thx|ty)[\.\!\,]?$")),
    ("conv:clarification", re.compile(r"^(i\s+mean|what\s+i\s+meant|to\s+clarify|clarification)\b")),
    ("conv:use_format", re.compile(r"^(use|switch\s+to|in)\s+(first\s+person|third\s+person|past\s+tense|present\s+tense|bullet\s+points?|markdown|json|yaml)\b")),

    # Comparison/analysis — the analysis IS the deliverable
    ("analysis:compare", re.compile(r"\b(compare|contrast|difference\s+between|vs\.?|versus)\b")),
    ("analysis:analyze", re.compile(r"\b(analyze|assess|evaluate)\s+(this|the|my|our)\b")),
    ("analysis:pros_cons", re.compile(r"\b(pros?\s+and\s+cons?|advantages?\s+and\s+disadvantages?|trade-?offs?)\b")),
]

DELIVERABLE_PATTERNS = [
    # Creation — something must exist after
    ("create:create", re.compile(r"\b(create|build|write|implement|add|make|generate|scaffold|bootstrap)\s+(a|an|the|new|my)\b")),
    ("create:deploy", re.compile(r"\b(deploy|publish|release|ship|launch)\b")),
    ("create:setup", re.compile(r"\bset\s*up\s+(a|an|the|new|my)\b")),
    ("create:install", re.compile(r"\b(install|add)\s+(the\s+)?(package|dependency|library|module|plugin|extension)\b")),

    # Content generation — must produce an artifact
    ("content:draft", re.compile(r"\b(draft|compose|write)\s+(a|an|the|my|this)?\s*(email|letter|message|essay|article|post|blog|readme|doc|document|report|proposal|resume|cv)\b")),
    ("content:template", re.compile(r"\b(create|make|build|write)\s+(a|an|the)?\s*(template|boilerplate|skeleton|starter)\b")),

    # System design — must produce a plan/architecture
    ("design:design", re.compile(r"\b(design|architect|plan|blueprint|spec\s+out|propose)\s+(a|an|the|my)?\s*(system|service|api|schema|architecture|pipeline|workflow|database)\b")),
    ("design:plan", re.compile(r"\b(create|write|draft)\s+(a|an|the)?\s*(plan|roadmap|strategy|outline)\b")),

    # File operations — must produce files
    ("file:new_file", re.compile(r"\b(create|add|write)\s+(a\s+)?(new\s+)?(file|script|module|class|component|function|test)\b")),
    ("file:migration", re.compile(r"\b(migrate|migration|convert|transform)\b.{0,30}\b(to|into|from)\b")),
]


def classify_prompt(content: str) -> tuple[str, str]:
    """Classify a prompt as CONVERSATION_OPS or DELIVERABLE_REQUEST.

    Returns (classification, pattern_name) where classification is one of:
    - "CONVERSATION_OPS"
    - "DELIVERABLE_REQUEST"
    - "AMBIGUOUS"

    The pattern_name indicates which pattern matched.
    """
    lower = content.strip().lower()

    # Skip very short prompts — likely conversational
    if len(lower) < 10:
        return ("CONVERSATION_OPS", "conv:short_utterance")

    # Check deliverable patterns FIRST — they override ops patterns
    # ("create a review" is a deliverable, not a review request)
    for name, pattern in DELIVERABLE_PATTERNS:
        if pattern.search(lower):
            # But check if this is really a question about creating
            # e.g., "should I create..." or "can you create..." with a question mark
            if lower.rstrip().endswith("?"):
                return ("CONVERSATION_OPS", f"question:about_{name}")
            return ("DELIVERABLE_REQUEST", name)

    # Check conversation ops patterns
    for name, pattern in CONVERSATION_OPS_PATTERNS:
        if pattern.search(lower):
            return ("CONVERSATION_OPS", name)

    # Fallback: check prompt_type from the atom metadata (handled by caller)
    return ("AMBIGUOUS", "no_pattern_match")


def classify_with_context(atom: dict, assistant_response: str | None) -> tuple[str, str]:
    """Classify using both prompt content and assistant response context.

    For ambiguous cases, checks assistant response to determine if the
    conversation completed the request.
    """
    content = atom.get("content", "")
    classification, pattern = classify_prompt(content)

    if classification != "AMBIGUOUS":
        return classification, pattern

    # Use prompt_type from the atom as a secondary signal
    prompt_type = atom.get("prompt_type", "")
    if prompt_type in ("question", "review", "operations"):
        return ("CONVERSATION_OPS", f"type:{prompt_type}")
    if prompt_type in ("creation", "planning"):
        return ("DELIVERABLE_REQUEST", f"type:{prompt_type}")

    # For directives and others, check if the assistant response
    # indicates completion
    if assistant_response:
        resp_lower = assistant_response[:500].lower()
        # If the response contains file creation evidence, it was a deliverable
        creation_evidence = any(s in resp_lower for s in [
            "i've created", "i've written", "here's the file",
            "i've added", "i've built", "i've implemented",
            "created the file", "wrote the file",
        ])
        if creation_evidence:
            return ("DELIVERABLE_REQUEST", "response:creation_evidence")

        # If the response is purely informational, it was conversational
        info_evidence = any(s in resp_lower for s in [
            "here's what", "the answer is", "this means",
            "that's because", "the reason is", "in summary",
        ])
        if info_evidence:
            return ("CONVERSATION_OPS", "response:informational")

    # Final fallback: directive-type prompts within a conversation
    # are usually conversational refinements
    if prompt_type == "directive":
        return ("CONVERSATION_OPS", "type:directive_fallback")

    # Truly ambiguous — keep for review
    return ("DELIVERABLE_REQUEST", "ambiguous:needs_manual_review")


def load_assistant_responses(db_path: Path) -> dict[tuple[str, int], str]:
    """Build index of (thread_id, turn_index) -> assistant_response from chat_turns.

    Connects READ-ONLY to knowledge.db.
    """
    if not db_path.exists():
        print(f"  [WARN] knowledge.db not found at {db_path}", file=sys.stderr)
        return {}

    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cursor = conn.cursor()

    # Load all turns grouped by thread
    cursor.execute(
        "SELECT thread_id, turn_index, role, content "
        "FROM chat_turns ORDER BY thread_id, turn_index"
    )

    thread_turns: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    for thread_id, turn_index, role, content in cursor:
        thread_turns[thread_id].append((turn_index, role, content))

    conn.close()

    # For each user turn, find the assistant response that follows
    response_index: dict[tuple[str, int], str] = {}
    for thread_id, turns in thread_turns.items():
        for i, (idx, role, _content) in enumerate(turns):
            if role != "user":
                continue
            # Collect assistant turns until next user turn
            parts = []
            for j in range(i + 1, len(turns)):
                t_idx, t_role, t_content = turns[j]
                if t_role == "user":
                    break
                if t_role == "assistant":
                    parts.append(t_content)
            if parts:
                response_index[(thread_id, idx)] = " ".join(parts)

    return response_index


def load_prompt_atoms(path: Path) -> list[dict]:
    """Load prompt atoms from JSONL."""
    atoms = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                atoms.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"  [WARN] Malformed JSON at line {lineno}", file=sys.stderr)
    return atoms


def write_results(db_path: Path, results: list[tuple[str, str, str]]) -> int:
    """Write classification results to review-results.db.

    Each result is (prompt_id, status, notes).
    Skips prompts that already have a non-SUPERSEDED review.
    Returns count of new rows written.
    """
    conn = sqlite3.connect(str(db_path), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=10000")
    cursor = conn.cursor()

    # Ensure table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            prompt_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            notes TEXT DEFAULT '',
            reviewed_at TEXT NOT NULL
        )
    """)
    conn.commit()

    # Get existing reviewed prompt IDs (skip those already classified)
    cursor.execute("SELECT prompt_id, status FROM reviews")
    existing = {row[0]: row[1] for row in cursor.fetchall()}

    now = datetime.now(timezone.utc).isoformat()
    written = 0
    batch_inserts = []
    batch_updates = []

    for prompt_id, new_status, notes in results:
        old_status = existing.get(prompt_id)
        # Skip if already has a non-SUPERSEDED status
        if old_status and old_status != "SUPERSEDED":
            continue
        if old_status == "SUPERSEDED":
            batch_updates.append((new_status, notes, now, prompt_id))
        else:
            batch_inserts.append((prompt_id, new_status, notes, now))
        written += 1

    # Write in batches using executemany for speed
    if batch_updates:
        cursor.executemany(
            "UPDATE reviews SET status = ?, notes = ?, reviewed_at = ? WHERE prompt_id = ?",
            batch_updates,
        )
    if batch_inserts:
        cursor.executemany(
            "INSERT INTO reviews (prompt_id, status, notes, reviewed_at) VALUES (?, ?, ?, ?)",
            batch_inserts,
        )

    conn.commit()
    conn.close()
    return written


def main() -> None:
    # Validate paths
    if not ATOMS_PATH.exists():
        print(f"ERROR: Prompt atoms not found at {ATOMS_PATH}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading prompt atoms from {ATOMS_PATH}...")
    atoms = load_prompt_atoms(ATOMS_PATH)
    print(f"  Loaded {len(atoms):,} prompt atoms")

    print(f"\nBuilding assistant response index from {KNOWLEDGE_DB}...")
    response_index = load_assistant_responses(KNOWLEDGE_DB)
    print(f"  Indexed {len(response_index):,} user->assistant response pairs")

    # Classify each atom
    print("\nClassifying prompts...")
    ops_count = 0
    deliverable_count = 0
    pattern_hits: Counter = Counter()
    domain_breakdown: dict[str, Counter] = defaultdict(Counter)
    results: list[tuple[str, str, str]] = []

    for atom in atoms:
        prompt_id = atom.get("id", "")
        thread_id = atom.get("source", {}).get("thread_id", "")
        turn_index = atom.get("source", {}).get("turn_index", -1)

        # Look up assistant response if available
        response = response_index.get((thread_id, turn_index))

        classification, pattern = classify_with_context(atom, response)

        if classification == "CONVERSATION_OPS":
            status = "VERIFIED_DONE"
            notes = f"auto-ops: {pattern}"
            ops_count += 1
        else:
            status = "NEEDS_REVIEW"
            notes = f"auto-ops: deliverable ({pattern})"
            deliverable_count += 1

        pattern_hits[pattern] += 1
        domain = atom.get("domain", "general")
        domain_breakdown[domain][classification] += 1

        results.append((prompt_id, status, notes))

    # Write to review-results.db
    print(f"\nWriting results to {REVIEW_DB}...")
    written = write_results(REVIEW_DB, results)
    print(f"  Wrote {written:,} new/updated reviews")

    # --- Report ---
    total = len(atoms)
    print(f"\n{'=' * 64}")
    print(f"  OPS TRIAGE RESULTS")
    print(f"{'=' * 64}")
    print(f"\n  Total prompt atoms:        {total:>8,}")
    print(f"  CONVERSATION_OPS:          {ops_count:>8,}  ({ops_count / total * 100:.1f}%)")
    print(f"  DELIVERABLE_REQUESTS:      {deliverable_count:>8,}  ({deliverable_count / total * 100:.1f}%)")
    print(f"  New reviews written:       {written:>8,}")

    print(f"\n{'─' * 64}")
    print(f"  Top 20 matched patterns:")
    print(f"{'─' * 64}")
    for pattern, count in pattern_hits.most_common(20):
        pct = count / total * 100
        print(f"    {pattern:<40s} {count:>6,}  ({pct:5.1f}%)")

    print(f"\n{'─' * 64}")
    print(f"  Domain breakdown:")
    print(f"{'─' * 64}")
    print(f"  {'Domain':<20s} {'Conv Ops':>10s} {'Deliverable':>12s} {'Total':>8s}")
    print(f"  {'─' * 52}")
    for domain in sorted(domain_breakdown.keys()):
        counts = domain_breakdown[domain]
        d_ops = counts.get("CONVERSATION_OPS", 0)
        d_del = counts.get("DELIVERABLE_REQUEST", 0)
        d_total = d_ops + d_del
        print(f"  {domain:<20s} {d_ops:>10,} {d_del:>12,} {d_total:>8,}")

    print(f"\n{'=' * 64}")
    print(f"  Done. Reviews in: {REVIEW_DB}")
    print(f"{'=' * 64}")


if __name__ == "__main__":
    main()
