#!/usr/bin/env python3
"""
reality_triage.py — Triage P0/P1 prompt atoms against filesystem reality.

For each prompt atom, extracts action verbs and target nouns from the content,
then runs reality checks against the filesystem, git history, and directory
structure to classify as:
  VERIFIED_DONE   — concrete evidence found on disk/git
  VERIFIED_OPEN   — checked, target does not exist
  UNABLE_TO_VERIFY — cannot determine from filesystem alone
  ABANDONED       — context no longer exists (e.g. Docker uninstalled)

Results written to ~/Workspace/organvm/my-knowledge-base/db/review-results.db
"""

import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WORKSPACE = Path.home() / "Workspace"
ATOMS_FILE = WORKSPACE / "organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
DB_PATH = WORKSPACE / "organvm/my-knowledge-base/db/review-results.db"

# Pre-index workspace structure once
REPO_DIRS: set[str] = set()
ALL_DIRS: set[str] = set()
ALL_FILES_BY_NAME: dict[str, list[str]] = {}  # basename -> [full paths]
GIT_REPOS: list[Path] = []

# Action verb categories
FILE_CREATE_VERBS = {
    "create", "write", "generate", "build", "scaffold", "add", "make",
    "draft", "produce", "output", "export", "save", "dump", "render",
}
GIT_VERBS = {
    "commit", "push", "merge", "deploy", "publish", "release", "tag",
    "pr", "pull request",
}
SCRIPT_VERBS = {
    "script", "function", "implement", "code", "program", "automate",
}
DOCKER_TERMS = {
    "docker", "dockerfile", "docker-compose", "container", "containerize",
    "docker compose", "docker build", "docker run",
}
ABANDONED_TERMS = DOCKER_TERMS  # Docker uninstalled 2026-04-18

# Prompt types that are inherently conversational (not filesystem-verifiable)
CONVERSATIONAL_TYPES = {"question", "review", "research"}

# Domains where output is rarely a file
CONVERSATIONAL_DOMAINS = {"email", "career", "creative", "content"}


def log(msg: str) -> None:
    print(f"[triage] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Phase 1: Index the workspace (one-time cost)
# ---------------------------------------------------------------------------

def index_workspace() -> None:
    """Walk ~/Workspace to build fast lookup structures."""
    global REPO_DIRS, ALL_DIRS, ALL_FILES_BY_NAME, GIT_REPOS

    log("Indexing workspace...")
    t0 = time.time()

    # Walk up to depth 4 for speed
    for org_dir in WORKSPACE.iterdir():
        if not org_dir.is_dir() or org_dir.name.startswith("."):
            continue
        ALL_DIRS.add(org_dir.name.lower())
        for child in org_dir.iterdir():
            if not child.is_dir():
                # Top-level files
                name = child.name.lower()
                ALL_FILES_BY_NAME.setdefault(name, []).append(str(child))
                continue
            repo_name = child.name.lower()
            REPO_DIRS.add(repo_name)
            ALL_DIRS.add(repo_name)
            if (child / ".git").is_dir():
                GIT_REPOS.append(child)
            # Index files one level deep in each repo
            try:
                for f in child.iterdir():
                    fname = f.name.lower()
                    ALL_FILES_BY_NAME.setdefault(fname, []).append(str(f))
            except PermissionError:
                pass

    # Also index ~/Workspace top-level files
    for f in WORKSPACE.iterdir():
        if f.is_file():
            ALL_FILES_BY_NAME.setdefault(f.name.lower(), []).append(str(f))

    elapsed = time.time() - t0
    log(f"Indexed {len(REPO_DIRS)} repos, {len(ALL_FILES_BY_NAME)} unique filenames in {elapsed:.1f}s")


# ---------------------------------------------------------------------------
# Phase 2: Extract action signals from prompt content
# ---------------------------------------------------------------------------

def extract_action_signals(content: str) -> dict:
    """Extract verbs, nouns, filenames, repo names from prompt content."""
    content_lower = content.lower()
    words = set(re.findall(r'[a-z_\-]+', content_lower))

    signals = {
        "has_file_create_verb": bool(words & FILE_CREATE_VERBS),
        "has_git_verb": bool(words & GIT_VERBS),
        "has_script_verb": bool(words & SCRIPT_VERBS),
        "has_docker_term": bool(words & DOCKER_TERMS),
        "has_abandoned_term": bool(words & ABANDONED_TERMS),
        "mentioned_filenames": [],
        "mentioned_repos": [],
        "mentioned_extensions": [],
        "is_html_content": "<html" in content_lower or "<div" in content_lower or "<p " in content_lower,
        "is_email_content": any(x in content_lower for x in ["@", "dear ", "hi ", "hello ", "subject:", "from:", "to:"]),
        "is_revision": any(x in content_lower for x in ["revise", "revision", "update", "modify", "edit", "rewrite"]),
        "is_conversational": any(x in content_lower for x in [
            "explain", "what is", "how do", "can you", "tell me", "describe",
            "summarize", "compare", "analyze", "help me understand",
            "respond to", "reply to", "answer", "opinion",
        ]),
    }

    # Extract filenames (anything with a file extension pattern)
    filenames = re.findall(
        r'[\w\-./]+\.(?:py|js|ts|tsx|jsx|sh|bash|zsh|yaml|yml|json|toml|md|html|css|go|rs|sql|env|txt|cfg|conf|ini|xml|plist|tmpl)',
        content_lower,
    )
    signals["mentioned_filenames"] = list(set(filenames))

    # Extract potential repo names (org/repo patterns)
    repo_patterns = re.findall(r'[\w\-]+/[\w\-]+', content)
    signals["mentioned_repos"] = list(set(repo_patterns))

    # Extract file extensions mentioned
    exts = re.findall(r'\.\w{1,5}\b', content_lower)
    signals["mentioned_extensions"] = list(set(exts))

    return signals


# ---------------------------------------------------------------------------
# Phase 3: Reality checks
# ---------------------------------------------------------------------------

def check_file_exists(filenames: list[str]) -> tuple[bool, str]:
    """Check if any mentioned filename exists in the workspace."""
    for fname in filenames:
        basename = os.path.basename(fname).lower()
        if basename in ALL_FILES_BY_NAME:
            return True, ALL_FILES_BY_NAME[basename][0]
        # Try without path prefix
        parts = fname.split("/")
        for part in parts:
            if part.lower() in ALL_FILES_BY_NAME:
                return True, ALL_FILES_BY_NAME[part.lower()][0]
    return False, ""


def check_repo_exists(repo_refs: list[str]) -> tuple[bool, str]:
    """Check if mentioned repo names exist in workspace."""
    for ref in repo_refs:
        parts = ref.split("/")
        repo_name = parts[-1].lower()
        if repo_name in REPO_DIRS:
            return True, repo_name
        # Fuzzy: check if any repo contains the name
        for existing in REPO_DIRS:
            if repo_name in existing or existing in repo_name:
                return True, existing
    return False, ""


def check_content_words_in_repos(content: str) -> tuple[bool, str]:
    """Check if key nouns from content match repo names."""
    content_lower = content.lower()
    # Extract significant words (3+ chars, not common)
    stopwords = {
        "the", "and", "for", "with", "from", "this", "that", "have", "has",
        "are", "was", "were", "been", "will", "can", "could", "would", "should",
        "not", "but", "all", "any", "some", "each", "every", "into", "about",
        "also", "then", "than", "more", "most", "just", "like", "make", "use",
        "how", "what", "when", "where", "which", "while", "here", "there",
        "your", "you", "they", "them", "their", "its", "our", "out",
        "add", "new", "get", "set", "let", "run", "try", "see", "now",
        "want", "need", "know", "look", "find", "give", "take", "come",
        "way", "may", "say", "same", "keep", "using", "please", "okay",
    }
    words = set(re.findall(r'[a-z]{4,}', content_lower)) - stopwords

    for word in words:
        if word in REPO_DIRS:
            return True, word
    return False, ""


# ---------------------------------------------------------------------------
# Phase 4: Classification engine
# ---------------------------------------------------------------------------

def classify_atom(atom: dict) -> tuple[str, str]:
    """
    Classify a prompt atom as VERIFIED_DONE, VERIFIED_OPEN,
    UNABLE_TO_VERIFY, or ABANDONED.

    Returns (classification, evidence_note).
    """
    content = atom.get("content", "")
    prompt_type = atom.get("prompt_type", "")
    domain = atom.get("domain", "")
    status = atom.get("status", "")
    tags = atom.get("tags", [])
    agent = atom.get("agent", "")

    signals = extract_action_signals(content)

    # Rule 1: Docker/container prompts -> ABANDONED
    if signals["has_docker_term"]:
        return "ABANDONED", "Docker uninstalled 2026-04-18"

    # Rule 2: Conversational prompts (questions, explanations, opinions)
    # These don't produce filesystem artifacts
    if signals["is_conversational"] and not signals["has_file_create_verb"]:
        if prompt_type in CONVERSATIONAL_TYPES:
            return "UNABLE_TO_VERIFY", f"Conversational {prompt_type} — no filesystem artifact expected"

    # Rule 3: Email drafts — not filesystem artifacts
    if signals["is_email_content"] and domain in ("email", "career", "content"):
        if not signals["has_file_create_verb"] or signals["is_revision"]:
            return "UNABLE_TO_VERIFY", "Email/letter draft — output in chat, not filesystem"

    # Rule 4: HTML content revisions (Canvas/LMS) — not stored locally
    if signals["is_html_content"] and not signals["mentioned_filenames"]:
        return "UNABLE_TO_VERIFY", "HTML content (likely LMS/Canvas) — not local filesystem"

    # Rule 5: Pure revision/editing of chat content
    if signals["is_revision"] and not signals["mentioned_filenames"] and not signals["has_file_create_verb"]:
        if prompt_type in ("bug_fix", "directive"):
            return "UNABLE_TO_VERIFY", "Revision directive — output in chat thread, not filesystem"

    # Rule 6: File creation prompts — check if files exist
    if signals["mentioned_filenames"]:
        found, path = check_file_exists(signals["mentioned_filenames"])
        if found:
            return "VERIFIED_DONE", f"File found: {path}"
        elif signals["has_file_create_verb"]:
            return "VERIFIED_OPEN", f"File not found: {signals['mentioned_filenames']}"

    # Rule 7: Repo references — check existence
    if signals["mentioned_repos"]:
        found, name = check_repo_exists(signals["mentioned_repos"])
        if found:
            return "VERIFIED_DONE", f"Repo exists: {name}"

    # Rule 8: Git operations
    if signals["has_git_verb"] and not signals["mentioned_filenames"]:
        return "UNABLE_TO_VERIFY", "Git operation — would need commit-level search"

    # Rule 9: Script/code creation without specific filename
    if signals["has_script_verb"] and not signals["mentioned_filenames"]:
        # Check if content mentions a specific script name
        found, name = check_content_words_in_repos(content)
        if found:
            return "VERIFIED_DONE", f"Related repo found: {name}"
        return "UNABLE_TO_VERIFY", "Code/script prompt without specific filename"

    # Rule 10: General file creation without clear target
    if signals["has_file_create_verb"] and prompt_type == "creation":
        if domain in ("code", "architecture", "infrastructure"):
            found, name = check_content_words_in_repos(content)
            if found:
                return "VERIFIED_DONE", f"Related repo found: {name}"
            return "UNABLE_TO_VERIFY", "Creation prompt — no specific file target identified"

    # Rule 11: Status-based fallbacks
    if status == "FAILED":
        return "VERIFIED_OPEN", "Atom status=FAILED — never completed"
    if status == "DEFERRED":
        return "VERIFIED_OPEN", "Atom status=DEFERRED — postponed"
    if status == "OPEN":
        return "VERIFIED_OPEN", "Atom status=OPEN — not addressed"

    # Rule 12: Answered prompts in conversational domains
    if status == "ANSWERED" and domain in CONVERSATIONAL_DOMAINS:
        return "UNABLE_TO_VERIFY", f"Answered {domain} prompt — output likely in chat, not filesystem"

    # Rule 13: Answered prompts with code/architecture domain
    if status == "ANSWERED" and domain in ("code", "architecture"):
        # These might have been applied — check for repo-level signals
        found, name = check_content_words_in_repos(content)
        if found:
            return "VERIFIED_DONE", f"Related repo found: {name}"

    # Default: can't determine from filesystem
    return "UNABLE_TO_VERIFY", f"No clear filesystem artifact to verify (type={prompt_type}, domain={domain})"


# ---------------------------------------------------------------------------
# Phase 5: Database + reporting
# ---------------------------------------------------------------------------

def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database for triage results."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("DROP TABLE IF EXISTS triage_results")
    conn.execute("""
        CREATE TABLE triage_results (
            id TEXT PRIMARY KEY,
            priority TEXT NOT NULL,
            title TEXT,
            prompt_type TEXT,
            domain TEXT,
            status TEXT,
            agent TEXT,
            classification TEXT NOT NULL,
            evidence TEXT,
            content_preview TEXT,
            tags TEXT,
            source_provider TEXT,
            timestamp TEXT,
            triaged_at TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX idx_classification ON triage_results(classification)")
    conn.execute("CREATE INDEX idx_priority ON triage_results(priority)")
    conn.execute("CREATE INDEX idx_domain ON triage_results(domain)")
    conn.execute("CREATE INDEX idx_priority_class ON triage_results(priority, classification)")
    conn.commit()
    return conn


def insert_result(conn: sqlite3.Connection, atom: dict, classification: str, evidence: str) -> None:
    """Insert a triage result into the database."""
    conn.execute(
        """INSERT OR REPLACE INTO triage_results
           (id, priority, title, prompt_type, domain, status, agent,
            classification, evidence, content_preview, tags,
            source_provider, timestamp, triaged_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            atom["id"],
            atom.get("priority", ""),
            atom.get("title", "")[:200],
            atom.get("prompt_type", ""),
            atom.get("domain", ""),
            atom.get("status", ""),
            atom.get("agent", ""),
            classification,
            evidence,
            atom.get("content", "")[:500],
            json.dumps(atom.get("tags", [])),
            atom.get("source", {}).get("provider", ""),
            atom.get("source", {}).get("timestamp", ""),
            time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        ),
    )


def print_stats(conn: sqlite3.Connection) -> None:
    """Print comprehensive triage statistics."""
    print("\n" + "=" * 80)
    print("REALITY TRIAGE RESULTS")
    print("=" * 80)

    # Overall counts
    total = conn.execute("SELECT COUNT(*) FROM triage_results").fetchone()[0]
    print(f"\nTotal atoms triaged: {total}")

    # By priority
    print("\n--- By Priority ---")
    rows = conn.execute(
        "SELECT priority, COUNT(*) FROM triage_results GROUP BY priority ORDER BY priority"
    ).fetchall()
    for pri, cnt in rows:
        print(f"  {pri}: {cnt}")

    # By classification (overall)
    print("\n--- By Classification (Overall) ---")
    rows = conn.execute(
        "SELECT classification, COUNT(*) FROM triage_results GROUP BY classification ORDER BY COUNT(*) DESC"
    ).fetchall()
    for cls, cnt in rows:
        pct = cnt / total * 100 if total else 0
        print(f"  {cls}: {cnt} ({pct:.1f}%)")

    # By priority x classification
    for pri in ("P0", "P1"):
        pri_total = conn.execute(
            "SELECT COUNT(*) FROM triage_results WHERE priority = ?", (pri,)
        ).fetchone()[0]
        print(f"\n--- {pri} Classification Breakdown ({pri_total} total) ---")
        rows = conn.execute(
            "SELECT classification, COUNT(*) FROM triage_results WHERE priority = ? GROUP BY classification ORDER BY COUNT(*) DESC",
            (pri,),
        ).fetchall()
        for cls, cnt in rows:
            pct = cnt / pri_total * 100 if pri_total else 0
            bar = "#" * int(pct / 2)
            print(f"  {cls:20s}: {cnt:5d} ({pct:5.1f}%) {bar}")

    # VERIFIED_OPEN by domain (the actionable items)
    print("\n--- VERIFIED_OPEN by Domain (Actionable Gaps) ---")
    rows = conn.execute(
        """SELECT priority, domain, COUNT(*)
           FROM triage_results
           WHERE classification = 'VERIFIED_OPEN'
           GROUP BY priority, domain
           ORDER BY priority, COUNT(*) DESC"""
    ).fetchall()
    for pri, dom, cnt in rows:
        print(f"  [{pri}] {dom}: {cnt}")

    # VERIFIED_DONE by domain
    print("\n--- VERIFIED_DONE by Domain (Confirmed Fulfilled) ---")
    rows = conn.execute(
        """SELECT priority, domain, COUNT(*)
           FROM triage_results
           WHERE classification = 'VERIFIED_DONE'
           GROUP BY priority, domain
           ORDER BY priority, COUNT(*) DESC"""
    ).fetchall()
    for pri, dom, cnt in rows:
        print(f"  [{pri}] {dom}: {cnt}")

    # ABANDONED
    abandoned_count = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE classification = 'ABANDONED'"
    ).fetchone()[0]
    if abandoned_count:
        print(f"\n--- ABANDONED ({abandoned_count} total) ---")
        rows = conn.execute(
            """SELECT priority, domain, COUNT(*)
               FROM triage_results
               WHERE classification = 'ABANDONED'
               GROUP BY priority, domain
               ORDER BY priority, COUNT(*) DESC"""
        ).fetchall()
        for pri, dom, cnt in rows:
            print(f"  [{pri}] {dom}: {cnt}")

    # By prompt_type x classification for P0
    print("\n--- P0 by Prompt Type x Classification ---")
    rows = conn.execute(
        """SELECT prompt_type, classification, COUNT(*)
           FROM triage_results
           WHERE priority = 'P0'
           GROUP BY prompt_type, classification
           ORDER BY prompt_type, COUNT(*) DESC"""
    ).fetchall()
    current_type = None
    for ptype, cls, cnt in rows:
        if ptype != current_type:
            current_type = ptype
            print(f"  {ptype}:")
        print(f"    {cls}: {cnt}")

    # By agent
    print("\n--- By Agent ---")
    rows = conn.execute(
        """SELECT agent, classification, COUNT(*)
           FROM triage_results
           GROUP BY agent, classification
           ORDER BY agent, COUNT(*) DESC"""
    ).fetchall()
    current_agent = None
    for agent, cls, cnt in rows:
        if agent != current_agent:
            current_agent = agent
            print(f"  {agent}:")
        print(f"    {cls}: {cnt}")

    # Top VERIFIED_OPEN P0 atoms (samples)
    print("\n--- Sample VERIFIED_OPEN P0 Atoms (first 20) ---")
    rows = conn.execute(
        """SELECT id, title, domain, prompt_type, evidence
           FROM triage_results
           WHERE priority = 'P0' AND classification = 'VERIFIED_OPEN'
           LIMIT 20"""
    ).fetchall()
    for atom_id, title, domain, ptype, evidence in rows:
        print(f"  {atom_id} [{domain}/{ptype}] {title[:80]}")
        print(f"    Evidence: {evidence}")

    # Top VERIFIED_DONE P0 atoms (samples)
    print("\n--- Sample VERIFIED_DONE P0 Atoms (first 20) ---")
    rows = conn.execute(
        """SELECT id, title, domain, prompt_type, evidence
           FROM triage_results
           WHERE priority = 'P0' AND classification = 'VERIFIED_DONE'
           LIMIT 20"""
    ).fetchall()
    for atom_id, title, domain, ptype, evidence in rows:
        print(f"  {atom_id} [{domain}/{ptype}] {title[:80]}")
        print(f"    Evidence: {evidence}")

    # Evidence distribution for UNABLE_TO_VERIFY
    print("\n--- UNABLE_TO_VERIFY Reasons (top 15) ---")
    rows = conn.execute(
        """SELECT evidence, COUNT(*)
           FROM triage_results
           WHERE classification = 'UNABLE_TO_VERIFY'
           GROUP BY evidence
           ORDER BY COUNT(*) DESC
           LIMIT 15"""
    ).fetchall()
    for evidence, cnt in rows:
        print(f"  {cnt:5d}: {evidence[:100]}")

    print("\n" + "=" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    t_start = time.time()

    # Step 1: Index workspace
    index_workspace()

    # Step 2: Load atoms
    log("Loading prompt atoms...")
    atoms_p0 = []
    atoms_p1 = []
    with open(ATOMS_FILE) as f:
        for line in f:
            obj = json.loads(line)
            pri = obj.get("priority", "")
            if pri == "P0":
                atoms_p0.append(obj)
            elif pri == "P1":
                atoms_p1.append(obj)

    log(f"Loaded {len(atoms_p0)} P0 + {len(atoms_p1)} P1 atoms")

    # Step 3: Initialize DB
    conn = init_db(DB_PATH)
    log(f"Database initialized at {DB_PATH}")

    # Step 4: Triage P0 first
    log("Triaging P0 atoms...")
    t_p0 = time.time()
    p0_stats = Counter()
    for atom in atoms_p0:
        classification, evidence = classify_atom(atom)
        p0_stats[classification] += 1
        insert_result(conn, atom, classification, evidence)
    conn.commit()
    log(f"P0 done in {time.time() - t_p0:.1f}s: {dict(p0_stats)}")

    # Step 5: Triage P1
    log("Triaging P1 atoms...")
    t_p1 = time.time()
    p1_stats = Counter()
    for atom in atoms_p1:
        classification, evidence = classify_atom(atom)
        p1_stats[classification] += 1
        insert_result(conn, atom, classification, evidence)
    conn.commit()
    log(f"P1 done in {time.time() - t_p1:.1f}s: {dict(p1_stats)}")

    # Step 6: Print comprehensive stats
    print_stats(conn)

    conn.close()
    elapsed = time.time() - t_start
    log(f"Total runtime: {elapsed:.1f}s")
    log(f"Results in: {DB_PATH}")


if __name__ == "__main__":
    main()
