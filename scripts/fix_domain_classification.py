#!/usr/bin/env python3
"""Fix misclassified domain tags in prompt-atoms.jsonl.

The original infer_domain() heuristic used overly broad keyword matching,
causing 17/24 architecture-tagged items to be misclassified (ENG 101
curriculum, name analyses, ChatGPT memory dumps, etc.).

This script re-evaluates every atom against tighter, more specific
keyword rules applied in priority order. If no reclassification rule
fires, the existing domain is preserved.

Usage:
    python3 scripts/fix_domain_classification.py [--dry-run]
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ATOMS_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "organvm-corpvs-testamentvm"
    / "data"
    / "atoms"
    / "prompt-atoms.jsonl"
)

# --- Reclassification rules ---
# Each rule: (new_domain, compiled_regex_pattern)
# Applied in order. First match wins. Case-insensitive.
# Patterns are compiled once for performance over 12K atoms.

RULES: list[tuple[str, re.Pattern]] = [
    # Education: ENC1101 / ENG 101 curriculum, teaching, grading
    (
        "education",
        re.compile(
            r"enc\s*1101|eng\s*101|syllabus|assignment\s+criteria|"
            r"student\s+submit|grading\s+rubric|rubric\b|"
            r"\bcanvas\b(?!.*html)|d2l\b|brightspace|"
            r"class\s+outline|week\s+\d+\s+(day|assignment)|"
            r"discussion\s+post|peer\s+review|course\s+schedule|"
            r"learning\s+outcome|attendance\s+polic|office\s+hours|"
            r"instructor\b|(?:next|this)\s+student|"
            r"semester\b|midterm|final\s+exam|"
            r"homework|classwork|lesson\s+plan|"
            r"\bcurriculum\b|pedagog",
            re.IGNORECASE,
        ),
    ),
    # Personal: name analysis, numerology, personal identity
    (
        "personal",
        re.compile(
            r"name\s+analysis|numerolog|etymology\s+of\s+(?:my\s+)?name|"
            r"meaning\s+of\s+(?:my\s+)?name|"
            r"birth\s*chart|astrology\s+chart|"
            r"life\s+path\s+number|angel\s+number|"
            r"personality\s+(?:type|test|assessment)",
            re.IGNORECASE,
        ),
    ),
    # Operations: ChatGPT memory, settings, config dumps
    (
        "operations",
        re.compile(
            r"chatgpt\s+memor|settings?\s+page|memory\s+dump|"
            r"custom\s+instructions|system\s+prompt\s+dump|"
            r"here\s+(?:is|are)\s+my\s+(?:settings|preferences|memories)|"
            r"export(?:ed)?\s+(?:my\s+)?(?:settings|config|preferences)",
            re.IGNORECASE,
        ),
    ),
    # Creative: mythology, MET4, mythOS, 4bloom, RE:GE, Orpheus, music
    (
        "creative",
        re.compile(
            r"\bmytholog|mythos\b|met4\b|mythOS|4bloom|re:ge\b|"
            r"orpheus|sentient\s+(?:ai|artificial)|"
            r"generative\s+(?:art|music)|"
            r"film\s+script|screenplay|poetry\b|poem\b|"
            r"short\s+story|novel\b|fiction\b|"
            r"compose\s+(?:a\s+)?(?:song|music|piece)|"
            r"youtube\s+channel\s+(?:name|description)",
            re.IGNORECASE,
        ),
    ),
    # Business: pitch deck, SOW, business plan, proposals
    (
        "business",
        re.compile(
            r"pitch\s+deck|business\s+plan|"
            r"\bsow\b|statement\s+of\s+work|"
            r"scope\s+of\s+work|project\s+proposal|"
            r"invoice\b|billing\b|pricing\s+(?:model|tier|page)|"
            r"client\s+proposal|freelance\s+(?:contract|rate)|"
            r"service\s+agreement|retainer\b|"
            r"marketing\s+(?:plan|strategy)|brand\s+(?:guide|identity)|"
            r"ulti\s*tool\s*media|digital\s+marketing\s+(?:agency|service)",
            re.IGNORECASE,
        ),
    ),
    # Career: resume, cover letter, job application, interview
    (
        "career",
        re.compile(
            r"resum[eé]\b|cover\s+letter|job\s+application|"
            r"interview\s+(?:prep|question|answer)|"
            r"professional\s+summary|linkedin\s+(?:profile|summary|headline)|"
            r"job\s+(?:search|hunt|posting|description)|"
            r"(?:write|draft)\s+(?:a\s+)?(?:robust\s+)?cover\s+letter|"
            r"hard\s+skills|soft\s+skills|"
            r"portfolio\s+(?:piece|project|website)|"
            r"(?:attached|this)\s+(?:role|job|position)",
            re.IGNORECASE,
        ),
    ),
    # Education (secondary signals -- broader patterns)
    (
        "education",
        re.compile(
            r"(?:student|pupil)(?:'s|s)?\s+(?:submission|work|essay|paper)|"
            r"(?:respond|reply)\s+(?:to|and)\s+(?:the\s+)?student|"
            r"(?:this|alvin|the)\s+student|"
            r"grade\s+(?:this|the|their)|feedback\s+(?:on|for)\s+(?:the\s+)?(?:student|submission)|"
            r"(?:40|30|25|20)\s+students",
            re.IGNORECASE,
        ),
    ),
]


def reclassify(atom: dict) -> str | None:
    """Return new domain if reclassification applies, else None."""
    # Build the text corpus to match against: content + title + thread_title
    content = atom.get("content", "")
    title = atom.get("title", "")
    thread_title = atom.get("source", {}).get("thread_title", "")
    text = f"{title} {content} {thread_title}"

    for new_domain, pattern in RULES:
        if pattern.search(text):
            return new_domain
    return None


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    if not ATOMS_PATH.exists():
        print(f"ERROR: {ATOMS_PATH} not found", file=sys.stderr)
        sys.exit(1)

    # Load all atoms
    atoms: list[dict] = []
    with open(ATOMS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                atoms.append(json.loads(line))

    print(f"Loaded {len(atoms)} atoms from {ATOMS_PATH}")

    # Reclassify
    changes = 0
    # Matrix: (old_domain, new_domain) -> count
    matrix: dict[tuple[str, str], int] = Counter()
    # Per-domain before/after
    before_counts: Counter = Counter()
    after_counts: Counter = Counter()

    for atom in atoms:
        old_domain = atom.get("domain", "general")
        before_counts[old_domain] += 1

        new_domain = reclassify(atom)
        if new_domain and new_domain != old_domain:
            atom["domain"] = new_domain
            matrix[(old_domain, new_domain)] += 1
            after_counts[new_domain] += 1
            changes += 1
        else:
            after_counts[old_domain] += 1

    # Write back
    if not dry_run and changes > 0:
        with open(ATOMS_PATH, "w", encoding="utf-8") as f:
            for atom in atoms:
                f.write(json.dumps(atom, ensure_ascii=False) + "\n")
        print(f"\nWrote {len(atoms)} atoms back to {ATOMS_PATH}")
    elif dry_run:
        print("\n[DRY RUN] No file written.")

    # --- Report ---
    print(f"\n{'='*60}")
    print(f"RECLASSIFICATION REPORT")
    print(f"{'='*60}")
    print(f"Total atoms:    {len(atoms)}")
    print(f"Reclassified:   {changes}")
    print(f"Unchanged:      {len(atoms) - changes}")

    # Transition matrix
    if matrix:
        print(f"\n{'─'*60}")
        print(f"TRANSITION MATRIX (old domain → new domain)")
        print(f"{'─'*60}")
        print(f"{'Old Domain':<20s} → {'New Domain':<20s}  {'Count':>6s}")
        print(f"{'─'*20}   {'─'*20}  {'─'*6}")
        for (old, new), count in sorted(
            matrix.items(), key=lambda x: (-x[1], x[0][0])
        ):
            print(f"{old:<20s} → {new:<20s}  {count:>6d}")

    # Domain distribution before/after
    all_domains = sorted(set(before_counts) | set(after_counts))
    print(f"\n{'─'*60}")
    print(f"DOMAIN DISTRIBUTION (before / after)")
    print(f"{'─'*60}")
    print(f"{'Domain':<20s}  {'Before':>8s}  {'After':>8s}  {'Delta':>8s}")
    print(f"{'─'*20}  {'─'*8}  {'─'*8}  {'─'*8}")
    for d in all_domains:
        b = before_counts.get(d, 0)
        a = after_counts.get(d, 0)
        delta = a - b
        sign = "+" if delta > 0 else ""
        delta_str = f"{sign}{delta}" if delta != 0 else "—"
        print(f"{d:<20s}  {b:>8d}  {a:>8d}  {delta_str:>8s}")

    print(f"\nDone.")


if __name__ == "__main__":
    main()
