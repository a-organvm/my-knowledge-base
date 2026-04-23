#!/usr/bin/env python3
"""Filesystem triage: cross-reference prompt atoms against ~/Workspace/.

For each prompt atom that references file creation, checks whether the
referenced files actually exist on disk. Builds a filename index of
~/Workspace/ once, then matches extracted file references against it.

Results written to review-results.db in a filesystem_triage table.

Usage: python3 scripts/filesystem_triage.py
"""

import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WORKSPACE = Path.home() / "Workspace"
PROJECT_ROOT = Path.home() / "Workspace/organvm/my-knowledge-base"
ATOMS_DIR = PROJECT_ROOT / "atomized" / "json" / "units"
JSONL_DIR = PROJECT_ROOT / "atomized" / "jsonl"
DB_PATH = PROJECT_ROOT / "db" / "review-results.db"

# Directories to skip when building the filename index
SKIP_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".eggs",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".cache",
    ".turbo",
    ".parcel-cache",
    "coverage",
    ".DS_Store",
    ".Trash",
    "vendor",
}

# File extensions we care about for file-reference matching
CODE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".md", ".yaml", ".yml", ".json", ".toml",
    ".sh", ".bash", ".zsh",
    ".rs", ".go", ".rb",
    ".css", ".scss", ".html", ".svelte", ".vue",
    ".sql", ".graphql", ".gql",
    ".tf", ".hcl",
    ".lua", ".vim",
    ".dockerfile", ".conf", ".cfg", ".ini", ".env",
    ".plist", ".tmpl",
}

# ---------------------------------------------------------------------------
# Regex patterns for extracting file references from prompt content
# ---------------------------------------------------------------------------

# Quoted paths: "src/foo.ts", 'config.yaml'
RE_QUOTED_PATH = re.compile(
    r"""(?:["'`])"""                        # opening quote/backtick
    r"""((?:[\w.~\-/\\]+/)*"""              # optional directory segments
    r"""[\w.\-]+"""                          # filename stem
    r"""\.(?:py|ts|tsx|js|jsx|mjs|cjs|md|yaml|yml|json|toml|sh|bash|zsh"""
    r"""|rs|go|rb|css|scss|html|svelte|vue|sql|graphql|gql|tf|hcl"""
    r"""|lua|vim|dockerfile|conf|cfg|ini|env|plist|tmpl))"""  # extension
    r"""(?:["'`])""",                       # closing quote/backtick
    re.IGNORECASE,
)

# Backtick paths: `config.yaml`, `src/utils.ts`
RE_BACKTICK_PATH = re.compile(
    r"""`((?:[\w.~\-/\\]+/)*[\w.\-]+"""
    r"""\.(?:py|ts|tsx|js|jsx|mjs|cjs|md|yaml|yml|json|toml|sh|bash|zsh"""
    r"""|rs|go|rb|css|scss|html|svelte|vue|sql|graphql|gql|tf|hcl"""
    r"""|lua|vim|dockerfile|conf|cfg|ini|env|plist|tmpl))`""",
    re.IGNORECASE,
)

# Explicit creation language: "create a file called X", "write X", "add X"
RE_CREATE_FILE = re.compile(
    r"""(?:create|write|add|make|generate|build|set\s+up|scaffold)\s+"""
    r"""(?:a\s+)?(?:new\s+)?(?:file\s+)?(?:called|named|at)?\s*"""
    r"""["`']?((?:[\w.~\-/\\]+/)*[\w.\-]+"""
    r"""\.(?:py|ts|tsx|js|jsx|mjs|cjs|md|yaml|yml|json|toml|sh|bash|zsh"""
    r"""|rs|go|rb|css|scss|html|svelte|vue|sql|graphql|gql|tf|hcl"""
    r"""|lua|vim|dockerfile|conf|cfg|ini|env|plist|tmpl))["`']?""",
    re.IGNORECASE,
)

# Directory creation: "mkdir X", "create a directory", "folder structure"
RE_CREATE_DIR = re.compile(
    r"""(?:mkdir\s+(?:-p\s+)?|create\s+(?:a\s+)?(?:new\s+)?(?:directory|folder|dir)\s+"""
    r"""|set\s+up\s+(?:a\s+)?(?:directory|folder)\s+)"""
    r"""["`']?([\w.~\-/\\]+/?)["`']?""",
    re.IGNORECASE,
)

# Bare file patterns in content (relaxed: just extension-bearing tokens)
RE_BARE_FILE = re.compile(
    r"""\b((?:[\w\-]+/)*[\w\-]+"""
    r"""\.(?:py|ts|tsx|js|jsx|md|yaml|yml|json|toml|sh|rs|go|css|html|vue|svelte|sql))\b""",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Creation-intent signals (prompt must contain one of these to be "about creation")
# ---------------------------------------------------------------------------

CREATION_SIGNALS = [
    "create", "write", "generate", "build", "scaffold", "set up", "setup",
    "make a", "add a", "implement", "deploy", "initialize", "init",
    "mkdir", "touch", "new file", "new script", "new config",
    "template", "boilerplate", "starter",
]

# Well-known library/framework names that look like filenames but are not.
# These are false positives from bare_file regex matching "Name.js" etc.
FALSE_POSITIVE_BASENAMES = {
    "node.js", "next.js", "three.js", "tone.js", "p5.js", "d3.js",
    "vue.js", "react.js", "angular.js", "ember.js", "backbone.js",
    "express.js", "nest.js", "nuxt.js", "deno.js", "bun.js",
    "electron.js", "svelte.js", "remix.js", "astro.js",
    "chart.js", "anime.js", "gsap.js", "howler.js", "paper.js",
    "fabric.js", "matter.js", "cannon.js", "pixi.js", "phaser.js",
    "socket.io", "webpack.js", "vite.js", "rollup.js", "esbuild.js",
    "jquery.js", "lodash.js", "moment.js", "dayjs.js", "rxjs.js",
    "supabase.js", "firebase.js", "prisma.js",
    "tailwind.css", "bootstrap.css", "normalize.css",
    # Common non-file patterns
    "package.json", "tsconfig.json", "readme.md", "license.md",
    "changelog.md", "contributing.md",
}


def has_creation_intent(content: str) -> bool:
    """Return True if the prompt content signals file/artifact creation."""
    lower = content.lower()
    return any(signal in lower for signal in CREATION_SIGNALS)


# ---------------------------------------------------------------------------
# Build filename index
# ---------------------------------------------------------------------------

def build_filename_index(root: Path) -> dict[str, list[str]]:
    """Walk root, build basename -> [full_paths] mapping. Skip noise dirs."""
    print(f"Building filename index from {root} ...")
    t0 = time.time()
    index: dict[str, list[str]] = defaultdict(list)
    file_count = 0
    dir_count = 0

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Prune skip directories in-place
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith(".")
        ]
        dir_count += 1

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in CODE_EXTENSIONS or fname in (
                "Dockerfile", "Makefile", "Brewfile", "Justfile",
                "justfile", "Procfile", "Gemfile", "Rakefile",
            ):
                full = os.path.join(dirpath, fname)
                index[fname.lower()].append(full)
                file_count += 1

    elapsed = time.time() - t0
    print(f"  Indexed {file_count:,} files across {dir_count:,} directories in {elapsed:.1f}s")
    return dict(index)


# ---------------------------------------------------------------------------
# Extract file references from a prompt atom
# ---------------------------------------------------------------------------

def extract_file_refs(content: str) -> list[dict]:
    """Extract file references from prompt content. Returns list of dicts with
    'ref' (the matched string), 'basename' (just the filename), 'ref_type'
    (quoted_path | backtick | create_file | create_dir | bare_file).
    """
    refs = []
    seen = set()

    def _add(ref: str, ref_type: str):
        basename = os.path.basename(ref.rstrip("/"))
        key = basename.lower()
        if key and key not in seen and len(basename) > 2:
            # Skip false positives: library names, URLs, version strings
            if key in FALSE_POSITIVE_BASENAMES:
                return
            # Skip anything that looks like a URL fragment
            if "http" in ref.lower() or "www." in ref.lower():
                return
            # Skip version-like patterns (e.g., "v1.2.js")
            if re.match(r"^v?\d+\.\d+", basename):
                return
            # Skip refs that look like web URL paths (domain TLD segments)
            tld_segments = {"com", "org", "net", "io", "gov", "edu", "dev",
                            "co", "app", "mnt", "www", "http", "https"}
            parts = ref.split("/")
            if len(parts) > 1 and parts[0].lower() in tld_segments:
                return
            # Also skip .html refs with domain-like parent directories
            if ".html" in key:
                if any("." in p and not p.endswith(".html") for p in parts[:-1]):
                    return
            seen.add(key)
            refs.append({
                "ref": ref,
                "basename": basename,
                "ref_type": ref_type,
            })

    for m in RE_QUOTED_PATH.finditer(content):
        _add(m.group(1), "quoted_path")

    for m in RE_BACKTICK_PATH.finditer(content):
        _add(m.group(1), "backtick")

    for m in RE_CREATE_FILE.finditer(content):
        _add(m.group(1), "create_file")

    for m in RE_CREATE_DIR.finditer(content):
        _add(m.group(1), "create_dir")

    for m in RE_BARE_FILE.finditer(content):
        _add(m.group(1), "bare_file")

    return refs


# ---------------------------------------------------------------------------
# Load all prompt atoms
# ---------------------------------------------------------------------------

def load_atoms_json(directory: Path) -> list[dict]:
    """Load atoms from individual JSON files."""
    atoms = []
    if not directory.exists():
        return atoms
    files = sorted(directory.glob("*.json"))
    print(f"Loading {len(files):,} JSON atom files ...")
    for fp in files:
        try:
            with open(fp) as f:
                atom = json.load(f)
                atoms.append(atom)
        except (json.JSONDecodeError, OSError):
            continue
    return atoms


def load_atoms_jsonl(directory: Path) -> list[dict]:
    """Load atoms from JSONL files."""
    atoms = []
    if not directory.exists():
        return atoms
    files = sorted(directory.glob("*.jsonl"))
    print(f"Loading {len(files)} JSONL files ...")
    for fp in files:
        try:
            with open(fp) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            atoms.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except OSError:
            continue
    return atoms


def deduplicate_atoms(atoms: list[dict]) -> list[dict]:
    """Deduplicate by atom ID, preferring the first occurrence."""
    seen_ids = set()
    unique = []
    for atom in atoms:
        aid = atom.get("id", "")
        if aid and aid not in seen_ids:
            seen_ids.add(aid)
            unique.append(atom)
        elif not aid:
            unique.append(atom)
    return unique


# ---------------------------------------------------------------------------
# Triage logic
# ---------------------------------------------------------------------------

def triage_atom(atom: dict, file_index: dict[str, list[str]]) -> list[dict]:
    """For a single atom, extract file refs and check against index.

    Returns a list of triage result dicts, one per file reference found.
    """
    content = atom.get("content", "") or ""
    context = atom.get("context", "") or ""
    title = atom.get("title", "") or ""
    full_text = f"{title}\n{content}\n{context}"

    refs = extract_file_refs(full_text)
    if not refs:
        return []

    creation_intent = has_creation_intent(full_text)
    results = []

    for ref_info in refs:
        basename = ref_info["basename"].lower()
        matches = file_index.get(basename, [])

        if matches:
            status = "VERIFIED_DONE"
            match_paths = matches[:5]  # cap stored paths
        elif creation_intent:
            status = "VERIFIED_OPEN"
            match_paths = []
        else:
            # Reference exists but no creation intent -- might just be
            # discussing a file. Mark as REFERENCE_ONLY.
            status = "REFERENCE_ONLY"
            match_paths = []

        results.append({
            "atom_id": atom.get("id", "unknown"),
            "atom_type": atom.get("type", "unknown"),
            "atom_title": (title[:120] if title else ""),
            "file_ref": ref_info["ref"],
            "file_basename": ref_info["basename"],
            "ref_type": ref_info["ref_type"],
            "status": status,
            "match_paths": json.dumps(match_paths),
            "creation_intent": creation_intent,
        })

    return results


# ---------------------------------------------------------------------------
# Database output
# ---------------------------------------------------------------------------

def init_db(db_path: Path) -> sqlite3.Connection:
    """Initialize the filesystem_triage table in review-results.db."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS filesystem_triage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atom_id TEXT NOT NULL,
            atom_type TEXT,
            atom_title TEXT,
            file_ref TEXT NOT NULL,
            file_basename TEXT NOT NULL,
            ref_type TEXT,
            status TEXT NOT NULL,
            match_paths TEXT,
            creation_intent BOOLEAN,
            triaged_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_fs_triage_status
        ON filesystem_triage(status)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_fs_triage_atom
        ON filesystem_triage(atom_id)
    """)
    # Clear previous triage results (this is a full re-scan)
    conn.execute("DELETE FROM filesystem_triage")
    conn.commit()
    return conn


def write_results(conn: sqlite3.Connection, results: list[dict]):
    """Batch-insert triage results."""
    conn.executemany("""
        INSERT INTO filesystem_triage
            (atom_id, atom_type, atom_title, file_ref, file_basename,
             ref_type, status, match_paths, creation_intent)
        VALUES
            (:atom_id, :atom_type, :atom_title, :file_ref, :file_basename,
             :ref_type, :status, :match_paths, :creation_intent)
    """, results)
    conn.commit()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t_start = time.time()

    # 1. Build filename index of ~/Workspace/ (one scan)
    file_index = build_filename_index(WORKSPACE)

    # 2. Load all prompt atoms (JSON units + JSONL)
    atoms_json = load_atoms_json(ATOMS_DIR)
    atoms_jsonl = load_atoms_jsonl(JSONL_DIR)
    all_atoms = atoms_json + atoms_jsonl
    all_atoms = deduplicate_atoms(all_atoms)
    print(f"Total unique atoms loaded: {len(all_atoms):,}")

    # 3. Triage each atom
    print("Triaging atoms against filesystem index ...")
    all_results = []
    atoms_with_refs = 0
    t_triage = time.time()

    for i, atom in enumerate(all_atoms):
        results = triage_atom(atom, file_index)
        if results:
            atoms_with_refs += 1
            all_results.extend(results)

        if (i + 1) % 5000 == 0:
            print(f"  Processed {i + 1:,}/{len(all_atoms):,} atoms ...")

    elapsed_triage = time.time() - t_triage
    print(f"  Triage complete in {elapsed_triage:.1f}s")

    # 4. Write to DB
    print(f"Writing {len(all_results):,} results to {DB_PATH} ...")
    conn = init_db(DB_PATH)
    write_results(conn, all_results)

    # 5. Summary statistics
    cursor = conn.cursor()

    cursor.execute("SELECT status, COUNT(*) FROM filesystem_triage GROUP BY status ORDER BY COUNT(*) DESC")
    status_counts = cursor.fetchall()

    cursor.execute("SELECT COUNT(DISTINCT atom_id) FROM filesystem_triage")
    unique_atoms_with_refs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT file_basename) FROM filesystem_triage WHERE status = 'VERIFIED_DONE'")
    unique_files_found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT file_basename) FROM filesystem_triage WHERE status = 'VERIFIED_OPEN'")
    unique_files_missing = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT atom_id) FROM filesystem_triage
        WHERE status = 'VERIFIED_DONE'
        AND atom_id NOT IN (SELECT atom_id FROM filesystem_triage WHERE status = 'VERIFIED_OPEN')
    """)
    fully_resolved_atoms = cursor.fetchone()[0]

    cursor.execute("""
        SELECT ref_type, COUNT(*) FROM filesystem_triage
        GROUP BY ref_type ORDER BY COUNT(*) DESC
    """)
    ref_type_counts = cursor.fetchall()

    # Top missing files (VERIFIED_OPEN)
    cursor.execute("""
        SELECT file_basename, file_ref, COUNT(*) as cnt
        FROM filesystem_triage WHERE status = 'VERIFIED_OPEN'
        GROUP BY file_basename ORDER BY cnt DESC LIMIT 20
    """)
    top_missing = cursor.fetchall()

    conn.close()

    elapsed_total = time.time() - t_start

    # Print report
    print("\n" + "=" * 70)
    print("FILESYSTEM TRIAGE REPORT")
    print("=" * 70)
    print(f"\nTotal atoms loaded:           {len(all_atoms):,}")
    print(f"Atoms with file references:   {atoms_with_refs:,}")
    print(f"Unique atoms in results:      {unique_atoms_with_refs:,}")
    print(f"Total file references found:  {len(all_results):,}")
    print(f"\n--- Status Breakdown ---")
    for status, count in status_counts:
        print(f"  {status:<20s} {count:>6,}")
    print(f"\n--- Reference Type Breakdown ---")
    for ref_type, count in ref_type_counts:
        print(f"  {ref_type:<20s} {count:>6,}")
    print(f"\nUnique files FOUND on disk:   {unique_files_found:,}")
    print(f"Unique files NOT FOUND:       {unique_files_missing:,}")
    print(f"Atoms fully resolved:         {fully_resolved_atoms:,}")
    print(f"  (all refs found, none missing)")

    if top_missing:
        print(f"\n--- Top 20 Missing Files (VERIFIED_OPEN) ---")
        for basename, ref, cnt in top_missing:
            print(f"  {cnt:>3}x  {ref}")

    print(f"\nResults written to: {DB_PATH}")
    print(f"Total elapsed: {elapsed_total:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
