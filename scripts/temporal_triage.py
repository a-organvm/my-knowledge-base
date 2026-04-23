#!/usr/bin/env python3
"""temporal_triage.py — Auto-classify prompt atoms as ABANDONED or SUPERSEDED
based on temporal obsolescence signals.

Reads:
  - prompt-atoms.jsonl (all prompt atoms)
  - intention-trajectories.jsonl (cluster membership for SUPERSEDED detection)

Writes:
  - review-results.db (upserts into existing reviews table)

Signals:
  ABANDONED — references to dead infrastructure, expired deadlines, completed semesters
  SUPERSEDED — older atom in a trajectory cluster replaced by newer within 30 days

stdlib only.
"""

import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ATOMS_PATH = Path.home() / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
TRAJECTORIES_PATH = Path.home() / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/intention-trajectories.jsonl"
DB_PATH = Path.home() / "Workspace/organvm/my-knowledge-base/db/review-results.db"

# ---------------------------------------------------------------------------
# Reference dates
# ---------------------------------------------------------------------------
TODAY = datetime(2026, 4, 23)
SIX_MONTHS_AGO = TODAY - timedelta(days=180)
NINETY_DAYS_AGO = TODAY - timedelta(days=90)
DOCKER_UNINSTALL_DATE = datetime(2026, 4, 18)
PROFESSOR_SEMESTER_CUTOFF = datetime(2025, 12, 1)

# ---------------------------------------------------------------------------
# Removed / dead tools — Docker uninstalled 2026-04-18, plus related stack
# ---------------------------------------------------------------------------
DEAD_TOOL_PATTERNS = [
    (re.compile(r"\bdocker\b", re.IGNORECASE), "docker"),
    (re.compile(r"\bdocker[-_]compose\b", re.IGNORECASE), "docker-compose"),
    (re.compile(r"\bdockerfile\b", re.IGNORECASE), "dockerfile"),
    (re.compile(r"\bkubernetes\b", re.IGNORECASE), "kubernetes"),
    (re.compile(r"\bk8s\b", re.IGNORECASE), "k8s"),
    (re.compile(r"\bminikube\b", re.IGNORECASE), "minikube"),
    (re.compile(r"\bvagrant\b", re.IGNORECASE), "vagrant"),
    (re.compile(r"\bvirtualbox\b", re.IGNORECASE), "virtualbox"),
]

# ---------------------------------------------------------------------------
# Teaching / professor patterns
# ---------------------------------------------------------------------------
PROFESSOR_PATTERNS = [
    re.compile(r"professor\s+padavano", re.IGNORECASE),
    re.compile(r"prof\.?\s+padavano", re.IGNORECASE),
]
TEACHING_PATTERNS = [
    re.compile(r"\bsyllabus\b", re.IGNORECASE),
    re.compile(r"\bgrading\s+rubric\b", re.IGNORECASE),
    re.compile(r"\bcourse\s+competenc", re.IGNORECASE),
    re.compile(r"\bassignment\s+(rubric|criteria|instructions|prompt)", re.IGNORECASE),
    re.compile(r"\bstudent\s+(submission|paper|essay|work)\b", re.IGNORECASE),
    re.compile(r"\bgrade\s+(this|the)\b", re.IGNORECASE),
    re.compile(r"\bfeedback\s+for\s+(student|this)\b", re.IGNORECASE),
    re.compile(r"\blumen\s*learning\b", re.IGNORECASE),
    re.compile(r"\benc\s*1101\b", re.IGNORECASE),
    re.compile(r"\bcourse\s+module\b", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Job application patterns (specific listings, not general career work)
# ---------------------------------------------------------------------------
JOB_APPLICATION_PATTERNS = [
    re.compile(r"\bcover\s+letter\b", re.IGNORECASE),
    re.compile(r"\bjob\s+(description|posting|listing|application)\b", re.IGNORECASE),
    re.compile(r"\bapply\s+(for|to)\s+(this|the)\b", re.IGNORECASE),
    re.compile(r"\bwrite\s+a\s+professional\s+summary\s+for\s+the\s+following\s+job\b", re.IGNORECASE),
    re.compile(r"\bresume\s+for\s+(this|the)\s+(job|position|role)\b", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Urgency / deadline patterns
# ---------------------------------------------------------------------------
URGENCY_PATTERNS = [
    re.compile(r"\burgent(ly)?\b", re.IGNORECASE),
    re.compile(r"\basap\b", re.IGNORECASE),
    re.compile(r"\bimmediately\b", re.IGNORECASE),
    re.compile(r"\btime[-\s]sensitive\b", re.IGNORECASE),
]

DEADLINE_PATTERNS = [
    re.compile(r"\bdeadline\b", re.IGNORECASE),
    re.compile(r"\bdue\s+(date|by|on|today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.IGNORECASE),
    re.compile(r"\bby\s+(tomorrow|tonight|monday|tuesday|wednesday|thursday|friday|end\s+of\s+(day|week))\b", re.IGNORECASE),
    re.compile(r"\bsubmit\s+by\b", re.IGNORECASE),
    re.compile(r"\bmust\s+be\s+(done|completed|finished|submitted)\s+by\b", re.IGNORECASE),
]

# Calendar date references — matches "January 15, 2024" or "2024-01-15" etc.
CALENDAR_DATE_RE = re.compile(
    r"(?:"
    r"(?:january|february|march|april|may|june|july|august|september|october|november|december)"
    r"\s+\d{1,2}(?:st|nd|rd|th)?,?\s*20\d{2}"
    r"|"
    r"20\d{2}[-/]\d{1,2}[-/]\d{1,2}"
    r"|"
    r"\d{1,2}[-/]\d{1,2}[-/]20\d{2}"
    r")",
    re.IGNORECASE,
)

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def parse_atom_date(timestamp_str: str) -> datetime | None:
    """Parse the source timestamp into a datetime, tolerating various formats."""
    if not timestamp_str:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(timestamp_str[:26], fmt)
            if dt.year < 2000:
                return None
            return dt
        except ValueError:
            continue
    return None


def parse_referenced_date(match_str: str) -> datetime | None:
    """Try to extract a datetime from a calendar date string found in content."""
    s = match_str.strip().lower().replace(",", "")
    # Try "Month DD YYYY"
    for month_name, month_num in MONTH_MAP.items():
        if month_name in s:
            parts = re.findall(r"\d+", s)
            if len(parts) >= 2:
                try:
                    day = int(parts[0])
                    year = int(parts[1])
                    return datetime(year, month_num, day)
                except (ValueError, OverflowError):
                    pass
    # Try ISO-like
    parts = re.findall(r"\d+", s)
    if len(parts) == 3:
        nums = [int(p) for p in parts]
        # YYYY-MM-DD
        if nums[0] > 2000:
            try:
                return datetime(nums[0], nums[1], nums[2])
            except ValueError:
                pass
        # MM/DD/YYYY
        if nums[2] > 2000:
            try:
                return datetime(nums[2], nums[0], nums[1])
            except ValueError:
                pass
    return None


def is_docker_conceptual(content: str) -> bool:
    """Distinguish conceptual Docker discussion from Docker-as-infrastructure.

    Prompts about Docker concepts (teaching, interviews) may still be valid.
    We only abandon prompts where Docker is the _operational_ tool.
    """
    conceptual_signals = [
        re.compile(r"\bexplain\s+(what\s+is\s+)?docker\b", re.IGNORECASE),
        re.compile(r"\bwhat\s+is\s+docker\b", re.IGNORECASE),
        re.compile(r"\binterview\s+question", re.IGNORECASE),
    ]
    return any(p.search(content) for p in conceptual_signals)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load_atoms() -> list[dict]:
    atoms = []
    with open(ATOMS_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                atoms.append(json.loads(line))
    return atoms


def load_trajectories() -> dict:
    """Returns:
      - member_to_trajectory: prompt_id -> trajectory_id
      - trajectory_members: trajectory_id -> list of (prompt_id, date_str) sorted by date
    """
    member_to_traj = {}
    traj_data = {}
    with open(TRAJECTORIES_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            t = json.loads(line)
            tid = t["trajectory_id"]
            members = t.get("member_ids", [])
            traj_data[tid] = {
                "label": t.get("intention_label", ""),
                "members": members,
                "span": t.get("span", {}),
            }
            for mid in members:
                member_to_traj[mid] = tid
    return member_to_traj, traj_data


# ---------------------------------------------------------------------------
# Classification engine
# ---------------------------------------------------------------------------
def classify_abandoned(atom: dict, atom_date: datetime | None, text: str) -> str | None:
    """Return a reason string if ABANDONED, else None."""

    # 1. Docker / removed tools (operational usage only)
    if not is_docker_conceptual(text):
        for pattern, tool_name in DEAD_TOOL_PATTERNS:
            if pattern.search(text):
                return f"references removed tool: {tool_name} (uninstalled {DOCKER_UNINSTALL_DATE.date()})"

    # 2. Professor Padavano / teaching — before semester cutoff
    if atom_date and atom_date < PROFESSOR_SEMESTER_CUTOFF:
        for p in PROFESSOR_PATTERNS:
            if p.search(text):
                return f"professor padavano prompt from completed semester ({atom_date.date()})"
        for p in TEACHING_PATTERNS:
            if p.search(text):
                return f"teaching/course prompt from completed semester ({atom_date.date()})"

    # 3. Specific job applications > 90 days old
    if atom_date and atom_date < NINETY_DAYS_AGO:
        for p in JOB_APPLICATION_PATTERNS:
            if p.search(text):
                return f"specific job application from {atom_date.date()} (>90 days old)"

    # 4. Urgency expired (> 6 months old)
    if atom_date and atom_date < SIX_MONTHS_AGO:
        for p in URGENCY_PATTERNS:
            if p.search(text):
                return f"urgent prompt from {atom_date.date()} (urgency expired, >6 months)"

    # 5. Calendar dates/deadlines that have passed
    if atom_date and atom_date < SIX_MONTHS_AGO:
        for p in DEADLINE_PATTERNS:
            if p.search(text):
                return f"deadline/due-date prompt from {atom_date.date()} (>6 months old)"

    # 6. Specific calendar date references in the past
    cal_matches = CALENDAR_DATE_RE.findall(text)
    for cal_str in cal_matches:
        ref_date = parse_referenced_date(cal_str)
        if ref_date and ref_date < SIX_MONTHS_AGO:
            return f"references past calendar date {ref_date.date()} (>6 months ago)"

    return None


def classify_superseded(
    atom_id: str,
    atom_date: datetime | None,
    member_to_traj: dict,
    traj_data: dict,
    atom_dates: dict[str, datetime],
) -> tuple[str | None, str | None]:
    """Return (reason, superseded_by_id) if SUPERSEDED, else (None, None)."""
    if not atom_date:
        return None, None

    tid = member_to_traj.get(atom_id)
    if not tid:
        return None, None

    traj = traj_data[tid]
    members = traj["members"]

    # Find all members with dates, sort by date
    dated_members = []
    for mid in members:
        md = atom_dates.get(mid)
        if md:
            dated_members.append((md, mid))
    dated_members.sort()

    # Find this atom's position
    my_pos = None
    for i, (d, mid) in enumerate(dated_members):
        if mid == atom_id:
            my_pos = i
            break

    if my_pos is None:
        return None, None

    # Check if a newer member exists within 30 days
    for j in range(my_pos + 1, len(dated_members)):
        newer_date, newer_id = dated_members[j]
        delta = (newer_date - atom_date).days
        if 0 < delta <= 30:
            label = traj["label"]
            return (
                f"superseded in trajectory '{label}' by {newer_id} ({delta}d later)",
                newer_id,
            )
        if delta > 30:
            break

    return None, None


# ---------------------------------------------------------------------------
# Database writer
# ---------------------------------------------------------------------------
def write_results(results: list[dict]):
    """Upsert results into review-results.db.

    Only writes new classifications. Does NOT overwrite existing reviews
    (respects prior manual triage).
    """
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # Ensure table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            prompt_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            notes TEXT DEFAULT '',
            reviewed_at TEXT NOT NULL
        )
    """)

    # Get existing prompt_ids to avoid overwriting manual reviews
    cur.execute("SELECT prompt_id FROM reviews")
    existing = {row[0] for row in cur.fetchall()}

    inserted = 0
    skipped = 0
    now_str = TODAY.strftime("%Y-%m-%dT%H:%M:%S")

    for r in results:
        pid = r["prompt_id"]
        if pid in existing:
            skipped += 1
            continue
        cur.execute(
            "INSERT INTO reviews (prompt_id, status, notes, reviewed_at) VALUES (?, ?, ?, ?)",
            (pid, r["status"], r["notes"], now_str),
        )
        inserted += 1

    conn.commit()
    conn.close()
    return inserted, skipped


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 72)
    print("TEMPORAL TRIAGE — Auto-classifying prompt atoms")
    print("=" * 72)
    print()

    # Load data
    print("[1/5] Loading prompt atoms...")
    atoms = load_atoms()
    print(f"      Loaded {len(atoms):,} atoms")

    print("[2/5] Loading trajectories...")
    member_to_traj, traj_data = load_trajectories()
    total_members = sum(len(t["members"]) for t in traj_data.values())
    print(f"      Loaded {len(traj_data)} trajectories covering {total_members:,} memberships")

    # Pre-compute dates for all atoms (needed for superseded detection)
    print("[3/5] Parsing dates...")
    atom_dates: dict[str, datetime] = {}
    for a in atoms:
        ts = a["source"].get("timestamp", "")
        d = parse_atom_date(ts)
        if d:
            atom_dates[a["id"]] = d

    print(f"      {len(atom_dates):,} atoms with valid dates")
    print(f"      Date range: {min(atom_dates.values()).date()} to {max(atom_dates.values()).date()}")

    # Classify
    print("[4/5] Classifying...")
    results = []
    stats = {
        "abandoned": defaultdict(int),
        "superseded": 0,
        "total_abandoned": 0,
        "total_superseded": 0,
    }

    # --- ABANDONED pass ---
    for a in atoms:
        pid = a["id"]
        ts = a["source"].get("timestamp", "")
        atom_date = atom_dates.get(pid)
        text = (a.get("content", "") + " " + a.get("title", "")).strip()

        reason = classify_abandoned(a, atom_date, text)
        if reason:
            results.append({
                "prompt_id": pid,
                "status": "ABANDONED",
                "notes": f"auto-temporal: {reason}",
            })
            # Categorize reason for stats
            if "removed tool" in reason:
                tool = reason.split("removed tool: ")[1].split(" (")[0]
                stats["abandoned"][f"removed tool: {tool}"] += 1
            elif "professor padavano" in reason:
                stats["abandoned"]["professor padavano (completed semester)"] += 1
            elif "teaching/course" in reason:
                stats["abandoned"]["teaching/course (completed semester)"] += 1
            elif "job application" in reason:
                stats["abandoned"]["specific job application (>90 days)"] += 1
            elif "urgency expired" in reason:
                stats["abandoned"]["urgency expired (>6 months)"] += 1
            elif "deadline/due-date" in reason:
                stats["abandoned"]["deadline/due-date (>6 months)"] += 1
            elif "past calendar date" in reason:
                stats["abandoned"]["past calendar date reference"] += 1
            else:
                stats["abandoned"]["other"] += 1
            stats["total_abandoned"] += 1

    # Collect already-classified IDs to avoid double-classifying
    abandoned_ids = {r["prompt_id"] for r in results}

    # --- SUPERSEDED pass ---
    for a in atoms:
        pid = a["id"]
        if pid in abandoned_ids:
            continue
        atom_date = atom_dates.get(pid)
        reason, superseded_by = classify_superseded(
            pid, atom_date, member_to_traj, traj_data, atom_dates
        )
        if reason:
            results.append({
                "prompt_id": pid,
                "status": "SUPERSEDED",
                "notes": f"auto-temporal: {reason}",
            })
            stats["total_superseded"] += 1

    # Write results
    print(f"[5/5] Writing {len(results):,} classifications to {DB_PATH.name}...")
    inserted, skipped = write_results(results)
    print(f"      Inserted: {inserted:,} | Skipped (already reviewed): {skipped:,}")

    # Print stats
    print()
    print("=" * 72)
    print("RESULTS")
    print("=" * 72)
    print()
    print(f"Total atoms scanned:     {len(atoms):,}")
    print(f"Total classified:        {len(results):,}")
    print()

    print(f"ABANDONED:               {stats['total_abandoned']:,}")
    print("-" * 48)
    for reason, count in sorted(stats["abandoned"].items(), key=lambda x: -x[1]):
        print(f"  {reason:<42} {count:>5}")

    print()
    print(f"SUPERSEDED:              {stats['total_superseded']:,}")
    print()

    # Breakdown of abandoned + superseded as % of total
    total_classified = stats["total_abandoned"] + stats["total_superseded"]
    pct = (total_classified / len(atoms) * 100) if atoms else 0
    print(f"Total temporal obsolescence: {total_classified:,} / {len(atoms):,} ({pct:.1f}%)")
    print()

    # Show what's in the DB now
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) FROM reviews GROUP BY status ORDER BY COUNT(*) DESC")
    print("Review DB state after triage:")
    for row in cur.fetchall():
        print(f"  {row[0]:<20} {row[1]:>6}")
    cur.execute("SELECT COUNT(*) FROM reviews")
    print(f"  {'TOTAL':<20} {cur.fetchone()[0]:>6}")
    conn.close()


if __name__ == "__main__":
    main()
