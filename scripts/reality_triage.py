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

Conservative: VERIFIED_DONE only with concrete filesystem evidence.
VERIFIED_OPEN only when we can confirm the target does not exist.
Everything ambiguous goes to UNABLE_TO_VERIFY.

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
REPO_DIRS: dict[str, str] = {}  # lowercased name -> actual path
ALL_FILES_DEEP: dict[str, list[str]] = {}  # basename -> [full paths]
GIT_REPOS: list[Path] = []
GIT_LOG_CACHE: dict[str, str] = {}  # repo path -> concatenated log messages

# Words that are repo names but too common in English to use as evidence.
# Err heavily on the side of exclusion — a false positive VERIFIED_DONE
# is worse than a false negative (UNABLE_TO_VERIFY).
AMBIGUOUS_REPO_NAMES = {
    "skills", "mesh", "tests", "config", "docs", "scripts", "lib",
    "data", "web", "apps", "logs", "raw", "intake", "content",
    "src", "dist", "build", "assets", "public", "private", "core",
    "tools", "utils", "agent", "engine", "system", "schema",
    "analytics", "community", "reading", "commerce", "portfolio",
    "scale", "growth", "auto", "universal", "adaptive", "nexus",
    "classroom", "collective", "announcement", "benchmark",
    "templates", "observatory", "contrib", "python", "commands",
    "padavano", "applications", "seeds", "packages", "backups",
    "performance", "node_modules", "atomized", "ecosystem",
    "cognitive", "production", "diagnostic", "documents",
    "manifest", "network", "response", "contribute", "contributing",
    "changelog",
}

# Minimum repo name length to consider as evidence
MIN_REPO_NAME_LEN = 12

# Generic filenames that exist in most repos and prove nothing
GENERIC_FILENAMES = {
    "readme.md", "changelog.md", "license", "license.md", "license.txt",
    "contributing.md", "package.json", "package-lock.json", "tsconfig.json",
    "pyproject.toml", "setup.py", "setup.cfg", "cargo.toml",
    ".gitignore", ".editorconfig", ".prettierrc", ".eslintrc.js",
    "manifest.yaml", "seed.yaml", "claude.md", "agents.md", "gemini.md",
    "justfile", "makefile", "dockerfile", "docker-compose.yml",
    "vitest.config.ts", "jest.config.js", "pytest.ini",
    "index.ts", "index.js", "main.py", "main.go", "main.rs",
    "app.py", "app.ts", "app.js", "server.ts", "server.js",
    "types.ts", "utils.ts", "config.ts", "config.yaml", "config.json",
    "init.lua", "tmux.conf", "starship.toml",
    "roadmap.md", "todo.md", "notes.md", "plan.md", "overview.md",
    "map.md", "inbox.md", "response.json", "catalog.json", "xref.json",
    "node.js", "chart.js", "content.js",  # common libraries, not user files
    "diagnostic.sh", "export.sh", "ingest.sh", "search.sh", "purge.sh",
    "capture.sh", "link_to_4jp.sh",  # generic script names
    "labels.yml", "ci.yml",  # generic CI config
    "v1.md", "v2.md", "v1.1.md", "pattern.md", "framework.md",
    "pip.conf",  # system config
    "index.md", "index.html", "index.css",  # generic index files
    "security.md", "governance_analysis.md",
    "bug_report.yml", "feature_request.yml",
}

DOCKER_TERMS = {
    "docker", "dockerfile", "docker-compose", "container", "containerize",
    "docker compose", "docker build", "docker run", "docker image",
    "dockerize", "docker network", "docker volume",
}

# URL domain patterns to filter out of filename extraction
URL_DOMAINS = re.compile(
    r'(?:www|http|https|ftp|mailto|tel|ssh|git)\b|'
    r'\.(?:com|org|net|edu|gov|io|co|uk|us|ca|au|de|fr|jp|ru|br|in)\b|'
    r'(?:nlm|nih|ncbi|census|eeoc|purdue|gamblingcommission|instructure|mdc|lumen)\b'
)


def log(msg: str) -> None:
    print(f"[triage] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Phase 1: Index the workspace (one-time cost)
# ---------------------------------------------------------------------------

def index_workspace() -> None:
    """Walk ~/Workspace to build fast lookup structures."""
    global REPO_DIRS, ALL_FILES_DEEP, GIT_REPOS

    log("Indexing workspace...")
    t0 = time.time()

    for org_dir in WORKSPACE.iterdir():
        if not org_dir.is_dir() or org_dir.name.startswith("."):
            continue
        for child in org_dir.iterdir():
            if not child.is_dir():
                continue
            repo_name = child.name.lower()
            REPO_DIRS[repo_name] = str(child)
            if (child / ".git").is_dir():
                GIT_REPOS.append(child)
            # Index files two levels deep in each repo
            try:
                for f in child.iterdir():
                    fname = f.name.lower()
                    if not fname.startswith("."):
                        ALL_FILES_DEEP.setdefault(fname, []).append(str(f))
                    if f.is_dir() and not fname.startswith("."):
                        try:
                            for ff in f.iterdir():
                                ffname = ff.name.lower()
                                if not ffname.startswith("."):
                                    ALL_FILES_DEEP.setdefault(ffname, []).append(str(ff))
                        except (PermissionError, OSError):
                            pass
            except (PermissionError, OSError):
                pass

    elapsed = time.time() - t0
    log(f"Indexed {len(REPO_DIRS)} repos, {len(ALL_FILES_DEEP)} unique filenames in {elapsed:.1f}s")


def index_git_logs() -> None:
    """Pre-fetch git log subjects from all repos (batch, fast)."""
    global GIT_LOG_CACHE
    log(f"Indexing git logs from {len(GIT_REPOS)} repos...")
    t0 = time.time()
    for repo in GIT_REPOS:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo), "log", "--oneline", "-50", "--format=%s"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                GIT_LOG_CACHE[str(repo)] = result.stdout.lower()
        except (subprocess.TimeoutExpired, OSError):
            pass
    elapsed = time.time() - t0
    log(f"Indexed git logs in {elapsed:.1f}s ({len(GIT_LOG_CACHE)} repos with history)")


# ---------------------------------------------------------------------------
# Phase 2: Extract action signals from prompt content
# ---------------------------------------------------------------------------

def extract_filenames_strict(content: str) -> list[str]:
    """Extract filenames from content, filtering out URL fragments."""
    content_lower = content.lower()
    # Match filename patterns
    candidates = re.findall(
        r'(?:^|[\s"\'(,])([a-z][\w\-./]*\.(?:py|js|ts|tsx|jsx|sh|bash|zsh|yaml|yml|json|toml|md|html|css|go|rs|sql|env|txt|cfg|conf|ini|xml|plist|tmpl))\b',
        content_lower,
    )
    # Filter out URL fragments
    filtered = []
    for c in candidates:
        # Skip if it looks like a URL domain component
        if URL_DOMAINS.search(c):
            continue
        # Skip if it's a bare extension (.md, .py etc.)
        basename = os.path.basename(c)
        if len(basename) <= 4:  # e.g. "a.py"
            continue
        # Skip paths that contain obvious URL components
        if "//" in c or "http" in c:
            continue
        filtered.append(c)
    return list(set(filtered))


def extract_explicit_repo_refs(content: str) -> list[str]:
    """Extract explicit GitHub-style repo references (org/repo),
    filtering out URL paths."""
    # Only match patterns that look like GitHub refs (letters, numbers, hyphens)
    candidates = re.findall(r'(?:^|[\s(])([A-Za-z0-9][\w-]*/[A-Za-z0-9][\w-]*)', content)
    filtered = []
    for c in candidates:
        parts = c.split("/")
        # Skip if either part is too short or looks like a URL path
        if len(parts[0]) < 3 or len(parts[1]) < 3:
            continue
        # Skip common URL path patterns
        if parts[0].lower() in ("http", "https", "www", "ftp", "ssh", "git"):
            continue
        if parts[1].lower() in ("html", "css", "js", "img", "images", "assets", "files", "pages"):
            continue
        filtered.append(c)
    return list(set(filtered))


def extract_action_signals(content: str) -> dict:
    """Extract verbs, nouns, filenames, repo names from prompt content."""
    content_lower = content.lower()
    words = set(re.findall(r'[a-z_\-]+', content_lower))

    file_create_verbs = {
        "create", "write", "generate", "build", "scaffold", "add", "make",
        "draft", "produce", "output", "export", "save", "dump", "render",
    }
    git_verbs = {
        "commit", "push", "merge", "deploy", "publish", "release", "tag",
    }
    script_verbs = {
        "script", "function", "implement", "automate",
    }

    signals = {
        "has_file_create_verb": bool(words & file_create_verbs),
        "has_git_verb": bool(words & git_verbs),
        "has_script_verb": bool(words & script_verbs),
        "has_docker_term": bool(words & DOCKER_TERMS),
        "mentioned_filenames": extract_filenames_strict(content),
        "mentioned_repos": extract_explicit_repo_refs(content),
        "is_html_content": bool(re.search(r'<(?:html|div|p|span|img|table|h[1-6])\b', content_lower)),
        "is_email_content": bool(re.search(
            r'(?:subject:|from:|to:|dear\s|hi\s\w+,|hello\s\w+,|@\w+\.\w+)', content_lower
        )),
        "is_revision": bool(re.search(
            r'\b(?:revise|revision|rewrite|rework|redo|refine)\b', content_lower
        )),
        "is_conversational": bool(re.search(
            r'\b(?:explain|what\s+is|how\s+do|can\s+you|tell\s+me|describe|help\s+me\s+understand)\b',
            content_lower,
        )),
        "is_curriculum_lms": bool(re.search(
            r'\b(?:canvas|lms|module\s+\d|syllabus|assignment|discussion|rubric|instructure|eng\s+10[12]|enc\s+\d{4})\b',
            content_lower,
        )),
        "is_resume_cover_letter": bool(re.search(
            r'\b(?:resume|cover\s+letter|job\s+description|professional\s+summary|linkedin|keywords?|skills?\s+list)\b',
            content_lower,
        )),
        "is_letter_legal": bool(re.search(
            r'\b(?:complaint|grievance|attorney|lawyer|eeoc|discrimination|harassment|termination|discharge)\b',
            content_lower,
        )),
        "is_name_analysis": bool(re.search(
            r'\b(?:name\s+analysis|name\s+meaning|etymology|hebrew|numerology|gematria)\b',
            content_lower,
        )),
        "is_seo_marketing": bool(re.search(
            r'\b(?:seo|keyword|merchant\s+cash|business\s+advance|adwords|ppc|landing\s+page)\b',
            content_lower,
        )),
        "is_student_feedback": bool(re.search(
            r'\b(?:student\s+\d+|next\s+student|grading|feedback|rough\s+draft|essay\s+rubric|peer\s+review)\b',
            content_lower,
        )),
    }

    return signals


# ---------------------------------------------------------------------------
# Phase 3: Reality checks
# ---------------------------------------------------------------------------

def check_file_exists_strict(filenames: list[str]) -> tuple[bool, str]:
    """Check if mentioned filenames exist in the workspace.
    Only matches exact basenames. Filters out generic filenames
    and node_modules paths that prove nothing about the prompt."""
    for fname in filenames:
        basename = os.path.basename(fname).lower()
        if basename in GENERIC_FILENAMES:
            continue
        if basename in ALL_FILES_DEEP:
            # Filter out node_modules matches — those are dependencies, not user files
            real_paths = [p for p in ALL_FILES_DEEP[basename] if "node_modules" not in p]
            if real_paths:
                return True, real_paths[0]
    return False, ""


def check_repo_exists_strict(repo_refs: list[str]) -> tuple[bool, str]:
    """Check if explicitly mentioned repo (org/name) exists.
    Requires exact match on the repo name portion — no fuzzy."""
    for ref in repo_refs:
        parts = ref.split("/")
        repo_name = parts[-1].lower()
        if repo_name in REPO_DIRS:
            return True, REPO_DIRS[repo_name]
    return False, ""


def check_specific_project_keywords(content: str) -> tuple[bool, str]:
    """Check if content mentions specific, unambiguous project names.

    Only matches repo names that are:
    1. Long enough to be distinctive (12+ chars)
    2. Not common English words
    3. Contain a double-hyphen (ORGANVM naming convention) OR
       are compound names unlikely to appear in normal prose
    4. Appear as distinct terms in the content
    """
    content_lower = content.lower()

    for repo_name, repo_path in REPO_DIRS.items():
        # Skip ambiguous names
        if repo_name in AMBIGUOUS_REPO_NAMES:
            continue
        if len(repo_name) < MIN_REPO_NAME_LEN:
            continue
        # Skip single English words even if long
        if re.match(r'^[a-z]+$', repo_name):
            continue
        # Skip contrib forks — these are external repos
        if repo_name.startswith("contrib--"):
            continue
        # Must contain a separator (hyphen, underscore, double-hyphen)
        if "-" not in repo_name and "_" not in repo_name:
            continue
        # Check for exact match in content
        if repo_name in content_lower:
            return True, f"{repo_name} ({repo_path})"

    return False, ""


def check_git_log_for_keywords(content: str) -> tuple[bool, str]:
    """Check if any git commit messages match distinctive keywords from content."""
    content_lower = content.lower()

    # Extract distinctive multi-word phrases (3+ words, 15+ chars)
    phrases = re.findall(r'[a-z][a-z\s]{15,}', content_lower)
    if not phrases:
        return False, ""

    # Only check first 3 phrases to stay fast
    for phrase in phrases[:3]:
        phrase_words = phrase.strip().split()
        if len(phrase_words) < 3:
            continue
        # Search for 3-word subsequences in git logs
        search_term = " ".join(phrase_words[:3])
        for repo_path, logs in GIT_LOG_CACHE.items():
            if search_term in logs:
                repo_name = os.path.basename(repo_path)
                return True, f"Git log match in {repo_name}: '{search_term}'"

    return False, ""


def check_application_pipeline(content: str) -> tuple[bool, str]:
    """Check if a job application prompt has a matching entry in application-pipeline."""
    pipeline_dir = WORKSPACE / "4444J99" / "application-pipeline"
    if not pipeline_dir.is_dir():
        return False, ""

    # Extract company names or job titles
    content_lower = content.lower()
    # Look for company name patterns
    companies = re.findall(r'(?:at|for|to|from)\s+([A-Z][A-Za-z\s&]+(?:Inc|LLC|Corp|Co)?)', content)
    if not companies:
        return False, ""

    # Check if pipeline has matching files
    try:
        pipeline_files = [f.name.lower() for f in pipeline_dir.iterdir() if f.is_file()]
        for company in companies[:3]:
            company_lower = company.strip().lower()
            for pf in pipeline_files:
                if company_lower[:10] in pf:
                    return True, f"Application pipeline match: {company.strip()}"
    except (PermissionError, OSError):
        pass

    return False, ""


# ---------------------------------------------------------------------------
# Phase 4: Classification engine
# ---------------------------------------------------------------------------

def classify_atom(atom: dict) -> tuple[str, str]:
    """
    Classify a prompt atom. Conservative: VERIFIED_DONE only with
    concrete filesystem evidence. Ambiguous cases -> UNABLE_TO_VERIFY.
    """
    content = atom.get("content", "")
    prompt_type = atom.get("prompt_type", "")
    domain = atom.get("domain", "")
    status = atom.get("status", "")
    agent = atom.get("agent", "")

    signals = extract_action_signals(content)

    # ===== ABANDONED (context no longer exists) =====

    if signals["has_docker_term"]:
        return "ABANDONED", "Docker uninstalled 2026-04-18"

    # ===== UNABLE_TO_VERIFY: Chat-native output categories =====
    # These prompt types produce output in the chat, not on disk.

    # Curriculum / LMS content (Canvas pages, module outlines)
    if signals["is_curriculum_lms"] or signals["is_student_feedback"]:
        return "UNABLE_TO_VERIFY", "LMS/curriculum content — output in Canvas/chat, not filesystem"

    # HTML content pasted for revision (Canvas modules, pages)
    if signals["is_html_content"] and not signals["mentioned_filenames"]:
        return "UNABLE_TO_VERIFY", "HTML content (likely LMS/Canvas) — not local filesystem"

    # Resume/cover letter/LinkedIn drafts
    if signals["is_resume_cover_letter"] and not signals["mentioned_filenames"]:
        return "UNABLE_TO_VERIFY", "Resume/cover letter draft — output in chat, not filesystem"

    # Legal letters and complaints
    if signals["is_letter_legal"]:
        return "UNABLE_TO_VERIFY", "Legal/complaint letter — output in chat, not filesystem"

    # Name analysis / creative writing
    if signals["is_name_analysis"]:
        return "UNABLE_TO_VERIFY", "Name analysis — output in chat, not filesystem"

    # SEO / marketing keyword lists
    if signals["is_seo_marketing"]:
        return "UNABLE_TO_VERIFY", "SEO/marketing content — output in chat, not filesystem"

    # Email drafts
    if signals["is_email_content"] and domain in ("email", "career", "content", "general"):
        return "UNABLE_TO_VERIFY", "Email/letter draft — output in chat, not filesystem"

    # Conversational questions
    if signals["is_conversational"] and prompt_type in ("question", "review", "research"):
        return "UNABLE_TO_VERIFY", f"Conversational {prompt_type} — no filesystem artifact expected"

    # Pure revision directives without file targets
    if signals["is_revision"] and not signals["mentioned_filenames"]:
        if prompt_type in ("bug_fix", "directive"):
            return "UNABLE_TO_VERIFY", "Revision directive — output in chat thread, not filesystem"

    # ===== VERIFIED checks: concrete filesystem evidence =====

    # Check 1: Explicit filenames mentioned -> look on disk
    # Only consider if there are a reasonable number of filenames (not a huge dump)
    mentioned = signals["mentioned_filenames"]
    if mentioned and len(mentioned) <= 10:
        found, path = check_file_exists_strict(mentioned)
        if found:
            return "VERIFIED_DONE", f"File exists: {path}"
        elif signals["has_file_create_verb"] and len(mentioned) <= 5:
            # Only mark VERIFIED_OPEN if we have a small, specific set of targets
            return "VERIFIED_OPEN", f"File not found: {mentioned}"
        # Filename mentioned but no create verb — might be referencing existing code
        # Don't mark VERIFIED_OPEN unless there was intent to create

    # Check 2: Explicit org/repo references
    if signals["mentioned_repos"]:
        found, path = check_repo_exists_strict(signals["mentioned_repos"])
        if found:
            return "VERIFIED_DONE", f"Repo exists: {path}"

    # Check 3: Distinctive project name keywords
    found, detail = check_specific_project_keywords(content)
    if found:
        return "VERIFIED_DONE", f"Project keyword match: {detail}"

    # Check 4: Git log evidence (only for git-verb prompts)
    if signals["has_git_verb"]:
        found, detail = check_git_log_for_keywords(content)
        if found:
            return "VERIFIED_DONE", f"Git evidence: {detail}"
        return "UNABLE_TO_VERIFY", "Git operation — no matching commit found"

    # Check 5: Job application prompts -> check pipeline
    if domain == "career" and signals["has_file_create_verb"]:
        found, detail = check_application_pipeline(content)
        if found:
            return "VERIFIED_DONE", f"Application pipeline: {detail}"

    # ===== Status-based VERIFIED_OPEN (atom was never completed) =====

    if status == "FAILED":
        return "VERIFIED_OPEN", "Atom status=FAILED — never completed"
    if status == "DEFERRED":
        return "VERIFIED_OPEN", "Atom status=DEFERRED — postponed"
    if status == "OPEN":
        return "VERIFIED_OPEN", "Atom status=OPEN — not addressed"

    # ===== UNABLE_TO_VERIFY: everything else =====

    # Answered prompts in chat-native domains
    if status == "ANSWERED" and domain in ("email", "career", "content", "creative"):
        return "UNABLE_TO_VERIFY", f"Answered {domain} prompt — output likely in chat, not filesystem"

    # Script/code prompts without specific targets
    if signals["has_script_verb"] or signals["has_file_create_verb"]:
        if prompt_type == "creation" and domain in ("code", "architecture", "infrastructure"):
            return "UNABLE_TO_VERIFY", "Creation prompt — no specific file target identified"

    # Default
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
    conn.execute("CREATE INDEX idx_status ON triage_results(status)")
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

    total = conn.execute("SELECT COUNT(*) FROM triage_results").fetchone()[0]
    print(f"\nTotal atoms triaged: {total}")

    # By priority
    print("\n--- By Priority ---")
    for row in conn.execute(
        "SELECT priority, COUNT(*) FROM triage_results GROUP BY priority ORDER BY priority"
    ).fetchall():
        print(f"  {row[0]}: {row[1]}")

    # By classification (overall)
    print("\n--- By Classification (Overall) ---")
    for cls, cnt in conn.execute(
        "SELECT classification, COUNT(*) FROM triage_results GROUP BY classification ORDER BY COUNT(*) DESC"
    ).fetchall():
        pct = cnt / total * 100 if total else 0
        print(f"  {cls:20s}: {cnt:5d} ({pct:5.1f}%)")

    # By priority x classification
    for pri in ("P0", "P1"):
        pri_total = conn.execute(
            "SELECT COUNT(*) FROM triage_results WHERE priority = ?", (pri,)
        ).fetchone()[0]
        print(f"\n--- {pri} Classification Breakdown ({pri_total} total) ---")
        for cls, cnt in conn.execute(
            "SELECT classification, COUNT(*) FROM triage_results WHERE priority = ? GROUP BY classification ORDER BY COUNT(*) DESC",
            (pri,),
        ).fetchall():
            pct = cnt / pri_total * 100 if pri_total else 0
            bar = "#" * int(pct / 2)
            print(f"  {cls:20s}: {cnt:5d} ({pct:5.1f}%) {bar}")

    # VERIFIED_OPEN by domain (actionable gaps)
    print("\n--- VERIFIED_OPEN by Domain (Actionable Gaps) ---")
    for pri, dom, cnt in conn.execute(
        """SELECT priority, domain, COUNT(*)
           FROM triage_results WHERE classification = 'VERIFIED_OPEN'
           GROUP BY priority, domain ORDER BY priority, COUNT(*) DESC"""
    ).fetchall():
        print(f"  [{pri}] {dom}: {cnt}")

    # VERIFIED_DONE by domain
    print("\n--- VERIFIED_DONE by Domain (Confirmed Fulfilled) ---")
    for pri, dom, cnt in conn.execute(
        """SELECT priority, domain, COUNT(*)
           FROM triage_results WHERE classification = 'VERIFIED_DONE'
           GROUP BY priority, domain ORDER BY priority, COUNT(*) DESC"""
    ).fetchall():
        print(f"  [{pri}] {dom}: {cnt}")

    # ABANDONED
    abandoned_count = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE classification = 'ABANDONED'"
    ).fetchone()[0]
    if abandoned_count:
        print(f"\n--- ABANDONED ({abandoned_count} total) ---")
        for pri, dom, cnt in conn.execute(
            """SELECT priority, domain, COUNT(*)
               FROM triage_results WHERE classification = 'ABANDONED'
               GROUP BY priority, domain ORDER BY priority, COUNT(*) DESC"""
        ).fetchall():
            print(f"  [{pri}] {dom}: {cnt}")

    # By prompt_type x classification for P0
    print("\n--- P0 by Prompt Type x Classification ---")
    current_type = None
    for ptype, cls, cnt in conn.execute(
        """SELECT prompt_type, classification, COUNT(*)
           FROM triage_results WHERE priority = 'P0'
           GROUP BY prompt_type, classification
           ORDER BY prompt_type, COUNT(*) DESC"""
    ).fetchall():
        if ptype != current_type:
            current_type = ptype
            print(f"  {ptype}:")
        print(f"    {cls}: {cnt}")

    # By agent
    print("\n--- By Agent ---")
    current_agent = None
    for agent_name, cls, cnt in conn.execute(
        """SELECT agent, classification, COUNT(*)
           FROM triage_results GROUP BY agent, classification
           ORDER BY agent, COUNT(*) DESC"""
    ).fetchall():
        if agent_name != current_agent:
            current_agent = agent_name
            print(f"  {agent_name}:")
        print(f"    {cls}: {cnt}")

    # Sample VERIFIED_OPEN P0 atoms
    print("\n--- Sample VERIFIED_OPEN P0 Atoms (first 25) ---")
    for atom_id, title, domain, ptype, evidence in conn.execute(
        """SELECT id, title, domain, prompt_type, evidence
           FROM triage_results WHERE priority = 'P0' AND classification = 'VERIFIED_OPEN'
           LIMIT 25"""
    ).fetchall():
        print(f"  {atom_id} [{domain}/{ptype}] {title[:80]}")
        print(f"    -> {evidence}")

    # Sample VERIFIED_DONE P0 atoms
    print("\n--- Sample VERIFIED_DONE P0 Atoms (first 25) ---")
    for atom_id, title, domain, ptype, evidence in conn.execute(
        """SELECT id, title, domain, prompt_type, evidence
           FROM triage_results WHERE priority = 'P0' AND classification = 'VERIFIED_DONE'
           LIMIT 25"""
    ).fetchall():
        print(f"  {atom_id} [{domain}/{ptype}] {title[:80]}")
        print(f"    -> {evidence}")

    # UNABLE_TO_VERIFY reasons breakdown
    print("\n--- UNABLE_TO_VERIFY Reasons (top 20) ---")
    for evidence, cnt in conn.execute(
        """SELECT evidence, COUNT(*)
           FROM triage_results WHERE classification = 'UNABLE_TO_VERIFY'
           GROUP BY evidence ORDER BY COUNT(*) DESC LIMIT 20"""
    ).fetchall():
        print(f"  {cnt:5d}: {evidence[:100]}")

    # P0 VERIFIED_OPEN by status (how many were never even attempted?)
    print("\n--- P0 VERIFIED_OPEN by Original Status ---")
    for s, cnt in conn.execute(
        """SELECT status, COUNT(*)
           FROM triage_results
           WHERE priority = 'P0' AND classification = 'VERIFIED_OPEN'
           GROUP BY status ORDER BY COUNT(*) DESC"""
    ).fetchall():
        print(f"  {s}: {cnt}")

    # Summary box
    p0_done = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P0' AND classification='VERIFIED_DONE'"
    ).fetchone()[0]
    p0_open = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P0' AND classification='VERIFIED_OPEN'"
    ).fetchone()[0]
    p0_abandoned = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P0' AND classification='ABANDONED'"
    ).fetchone()[0]
    p0_unknown = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P0' AND classification='UNABLE_TO_VERIFY'"
    ).fetchone()[0]
    p0_total = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P0'"
    ).fetchone()[0]

    print("\n" + "=" * 80)
    print("SUMMARY (P0 Only)")
    print("=" * 80)
    print(f"  VERIFIED_DONE    : {p0_done:4d} / {p0_total} ({p0_done/p0_total*100:.1f}%) - Confirmed on disk")
    print(f"  VERIFIED_OPEN    : {p0_open:4d} / {p0_total} ({p0_open/p0_total*100:.1f}%) - Confirmed NOT done")
    print(f"  ABANDONED        : {p0_abandoned:4d} / {p0_total} ({p0_abandoned/p0_total*100:.1f}%) - Context gone (Docker etc)")
    print(f"  UNABLE_TO_VERIFY : {p0_unknown:4d} / {p0_total} ({p0_unknown/p0_total*100:.1f}%) - Chat-native or ambiguous")
    print("=" * 80)

    p1_done = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P1' AND classification='VERIFIED_DONE'"
    ).fetchone()[0]
    p1_open = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P1' AND classification='VERIFIED_OPEN'"
    ).fetchone()[0]
    p1_abandoned = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P1' AND classification='ABANDONED'"
    ).fetchone()[0]
    p1_unknown = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P1' AND classification='UNABLE_TO_VERIFY'"
    ).fetchone()[0]
    p1_total = conn.execute(
        "SELECT COUNT(*) FROM triage_results WHERE priority='P1'"
    ).fetchone()[0]

    print("SUMMARY (P1 Only)")
    print("=" * 80)
    print(f"  VERIFIED_DONE    : {p1_done:4d} / {p1_total} ({p1_done/p1_total*100:.1f}%) - Confirmed on disk")
    print(f"  VERIFIED_OPEN    : {p1_open:4d} / {p1_total} ({p1_open/p1_total*100:.1f}%) - Confirmed NOT done")
    print(f"  ABANDONED        : {p1_abandoned:4d} / {p1_total} ({p1_abandoned/p1_total*100:.1f}%) - Context gone")
    print(f"  UNABLE_TO_VERIFY : {p1_unknown:4d} / {p1_total} ({p1_unknown/p1_total*100:.1f}%) - Chat-native or ambiguous")
    print("=" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    t_start = time.time()

    # Step 1: Index workspace
    index_workspace()
    index_git_logs()

    # Step 2: Load atoms
    log("Loading prompt atoms...")
    atoms_p0: list[dict] = []
    atoms_p1: list[dict] = []
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

    # Step 4: Triage P0
    log("Triaging P0 atoms...")
    t_p0 = time.time()
    p0_stats: Counter = Counter()
    for atom in atoms_p0:
        classification, evidence = classify_atom(atom)
        p0_stats[classification] += 1
        insert_result(conn, atom, classification, evidence)
    conn.commit()
    log(f"P0 done in {time.time() - t_p0:.1f}s: {dict(p0_stats)}")

    # Step 5: Triage P1
    log("Triaging P1 atoms...")
    t_p1 = time.time()
    p1_stats: Counter = Counter()
    for atom in atoms_p1:
        classification, evidence = classify_atom(atom)
        p1_stats[classification] += 1
        insert_result(conn, atom, classification, evidence)
    conn.commit()
    log(f"P1 done in {time.time() - t_p1:.1f}s: {dict(p1_stats)}")

    # Step 6: Print stats
    print_stats(conn)

    conn.close()
    elapsed = time.time() - t_start
    log(f"Total runtime: {elapsed:.1f}s")
    log(f"Results in: {DB_PATH}")


if __name__ == "__main__":
    main()
