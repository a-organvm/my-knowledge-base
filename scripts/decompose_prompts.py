#!/usr/bin/env python3
"""Layer 2: Sub-atomic decomposition of prompt atoms.

Rule-based decomposition — no AI API calls. Splits compound prompts into
sub-prompts using structural markers (numbered lists, bullets, semicolons,
conjunctions, embedded questions, multi-paragraph imperatives).

Usage: python3 scripts/decompose_prompts.py
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path

ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)
SUB_OUTPUT = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/sub-prompt-atoms.jsonl"
)

IMPERATIVE_VERBS = {
    "fix", "add", "create", "build", "update", "remove", "delete", "deploy",
    "push", "commit", "merge", "review", "check", "test", "run", "install",
    "refactor", "move", "rename", "copy", "export", "import", "configure",
    "setup", "set", "enable", "disable", "write", "read", "list", "show",
    "find", "search", "replace", "generate", "analyze", "debug", "audit",
    "clean", "clear", "reset", "restart", "stop", "start", "open", "close",
    "send", "draft", "schedule", "plan", "design", "implement", "migrate",
    "upgrade", "convert", "transform", "validate", "verify", "summarize",
    "explain", "describe", "compare", "evaluate", "ensure", "make", "provide",
    "include", "exclude", "apply", "rewrite", "organize", "document",
    "integrate", "optimize", "resolve", "investigate", "extract", "parse",
}

PRIORITY_DEMOTION = {"P0": "P1", "P1": "P2", "P2": "P3", "P3": "P3"}


def classify_sub_type(text: str) -> str:
    lower = text.lower().strip()
    if text.strip().endswith("?"):
        return "question"
    if any(lower.startswith(v) for v in ["fix", "debug", "resolve", "patch"]):
        return "bug_fix"
    if any(lower.startswith(v) for v in ["create", "build", "write", "add", "implement", "generate"]):
        return "creation"
    if any(lower.startswith(v) for v in ["refactor", "clean", "reorganize", "rename", "move"]):
        return "refactor"
    if any(lower.startswith(v) for v in ["review", "audit", "check", "verify", "validate"]):
        return "review"
    if any(lower.startswith(v) for v in ["research", "find", "search", "look", "explore", "investigate"]):
        return "research"
    if any(lower.startswith(v) for v in ["deploy", "push", "commit", "merge", "release"]):
        return "operations"
    return "directive"


def decompose(content: str) -> list:
    """Extract sub-prompts from a compound prompt."""
    subs = []

    # Strategy 1: Numbered lists (1. X  2. Y  3. Z)
    numbered = re.findall(r"(?:^|\n)\s*\d+[\.\)]\s+(.+?)(?=\n\s*\d+[\.\)]|\n\n|\Z)", content, re.DOTALL)
    if len(numbered) >= 2:
        for item in numbered:
            text = item.strip()
            if len(text) > 10:
                subs.append(text)
        if subs:
            return subs

    # Strategy 2: Bullet points (- X  - Y)
    bullets = re.findall(r"(?:^|\n)\s*[-•*]\s+(.+?)(?=\n\s*[-•*]|\n\n|\Z)", content, re.DOTALL)
    if len(bullets) >= 2:
        for item in bullets:
            text = item.strip()
            if len(text) > 10:
                subs.append(text)
        if subs:
            return subs

    # Strategy 3: Semicolons as task separators
    if ";" in content and content.count(";") >= 2:
        parts = [p.strip() for p in content.split(";") if p.strip()]
        # Only split if segments look like tasks (contain verbs)
        actionable = [p for p in parts if any(p.lower().split()[0:1] == [v] for v in IMPERATIVE_VERBS if p.split())]
        if len(actionable) >= 2:
            return actionable

    # Strategy 4: Multi-paragraph with distinct imperatives
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    if len(paragraphs) >= 2:
        imperative_paras = []
        for para in paragraphs:
            first_word = para.split()[0].lower().rstrip(".,;:") if para.split() else ""
            if first_word in IMPERATIVE_VERBS and len(para) > 20:
                imperative_paras.append(para)
        if len(imperative_paras) >= 2:
            return imperative_paras

    # Strategy 5: "Also" as new sub-task
    also_split = re.split(r"(?:\.\s+Also\b|;\s*also\b|\n\s*Also\b)", content, flags=re.IGNORECASE)
    if len(also_split) >= 2:
        valid = [p.strip() for p in also_split if len(p.strip()) > 15]
        if len(valid) >= 2:
            return valid

    # Strategy 6: Embedded questions in directives
    sentences = re.split(r"(?<=[.!?])\s+", content)
    if len(sentences) >= 2:
        questions = [s for s in sentences if s.strip().endswith("?") and len(s.strip()) > 15]
        directives = [s for s in sentences if not s.strip().endswith("?") and len(s.strip()) > 15]
        if questions and directives:
            return [" ".join(directives)] + questions

    return []


def main():
    print("Loading prompt atoms...")
    atoms = []
    with open(ATOMS_PATH) as f:
        for line in f:
            if line.strip():
                atoms.append(json.loads(line))

    print(f"  Loaded {len(atoms)} atoms")

    all_sub_prompts = []
    decomposed_count = 0
    skip_short = 0
    skip_atomic = 0
    sub_counts = defaultdict(int)  # histogram of sub-prompt counts per parent

    for atom in atoms:
        content = atom.get("content", "")

        # Skip conditions
        if len(content) < 100:
            skip_short += 1
            atom["decomposition"] = {"sub_prompts": [], "layer": 2}
            continue

        # Single sentence ending in ? = already atomic
        if content.strip().endswith("?") and "\n" not in content and len(content) < 300:
            skip_atomic += 1
            atom["decomposition"] = {"sub_prompts": [], "layer": 2}
            continue

        subs = decompose(content)

        if not subs or len(subs) < 2:
            atom["decomposition"] = {"sub_prompts": [], "layer": 2}
            continue

        decomposed_count += 1
        sub_counts[len(subs)] += 1
        sub_ids = []

        for idx, sub_text in enumerate(subs):
            sub_id = f"{atom['id']}-sub-{idx}"
            sub_ids.append(sub_id)

            priority = atom.get("priority", "P3")
            if idx > 0:
                priority = PRIORITY_DEMOTION.get(priority, "P3")

            sub_atom = {
                "id": sub_id,
                "parent_id": atom["id"],
                "title": sub_text[:80],
                "content": sub_text,
                "source": atom.get("source", {}),
                "status": atom.get("status", "OPEN"),
                "prompt_type": classify_sub_type(sub_text),
                "actionable": True,
                "tags": atom.get("tags", []),
                "priority": priority,
                "domain": atom.get("domain", "general"),
                "complexity": {
                    "char_length": len(sub_text),
                    "line_count": sub_text.count("\n") + 1,
                },
                "decomposition": {"sub_prompts": [], "layer": 2, "is_sub_prompt": True},
            }
            all_sub_prompts.append(sub_atom)

        atom["decomposition"] = {"sub_prompts": sub_ids, "layer": 2}

    # Write updated atoms
    tmp_atoms = str(ATOMS_PATH) + ".tmp"
    with open(tmp_atoms, "w") as f:
        for atom in atoms:
            f.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.rename(tmp_atoms, ATOMS_PATH)

    # Write sub-prompts
    tmp_subs = str(SUB_OUTPUT) + ".tmp"
    with open(tmp_subs, "w") as f:
        for sub in all_sub_prompts:
            f.write(json.dumps(sub, ensure_ascii=False) + "\n")
    os.rename(tmp_subs, SUB_OUTPUT)

    # Stats
    print(f"\n{'=' * 60}")
    print(f"LAYER 2: SUB-ATOMIC DECOMPOSITION RESULTS")
    print(f"{'=' * 60}")
    print(f"Total atoms processed: {len(atoms)}")
    print(f"Decomposed: {decomposed_count} ({100*decomposed_count/len(atoms):.1f}%)")
    print(f"Skipped (too short <100): {skip_short}")
    print(f"Skipped (already atomic): {skip_atomic}")
    print(f"Total sub-prompts extracted: {len(all_sub_prompts)}")
    print(f"\nSub-prompt count distribution:")
    for count, freq in sorted(sub_counts.items()):
        print(f"  {count} sub-prompts: {freq} atoms")

    # Type distribution
    type_dist = defaultdict(int)
    for sub in all_sub_prompts:
        type_dist[sub["prompt_type"]] += 1
    print(f"\nSub-prompt type distribution:")
    for t, c in sorted(type_dist.items(), key=lambda x: -x[1]):
        print(f"  {t:12s}: {c}")

    print(f"\nOutput files:")
    print(f"  Updated: {ATOMS_PATH} ({ATOMS_PATH.stat().st_size / 1024 / 1024:.1f} MB)")
    print(f"  New:     {SUB_OUTPUT} ({SUB_OUTPUT.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
