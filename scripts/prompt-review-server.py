#!/usr/bin/env python3
"""Prompt Review Server — human triage of 11,980 intention atoms.

Every prompt needs human review. The question: does this thing exist in
the world, or did you just talk about it?

Usage: python3 scripts/prompt-review-server.py [--port 8080]
"""

import json
import os
import sqlite3
import sys
import urllib.parse
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR.parent
ATOMS_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms.jsonl"
)
SHORT_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/prompt-atoms-short.jsonl"
)
TRAJECTORIES_PATH = (
    Path.home()
    / "Workspace/organvm/organvm-corpvs-testamentvm/data/atoms/intention-trajectories.jsonl"
)
KNOWLEDGE_DB = KB_DIR / "db" / "knowledge.db"
REVIEW_DB = KB_DIR / "db" / "review-results.db"

# Priority sort order
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


class ReviewServer:
    def __init__(self):
        self.atoms = []
        self.atoms_by_id = {}
        self.trajectory_members = set()
        self.review_order = []
        self.load_atoms()
        self.load_trajectories()
        self.init_review_db()
        self.build_review_order()

    def load_atoms(self):
        for path in [ATOMS_PATH, SHORT_PATH]:
            if path.exists():
                with open(path) as f:
                    for line in f:
                        if line.strip():
                            atom = json.loads(line)
                            self.atoms.append(atom)
                            self.atoms_by_id[atom["id"]] = atom
        print(f"Loaded {len(self.atoms)} prompt atoms")

    def load_trajectories(self):
        if TRAJECTORIES_PATH.exists():
            with open(TRAJECTORIES_PATH) as f:
                for line in f:
                    if line.strip():
                        traj = json.loads(line)
                        for mid in traj.get("member_ids", []):
                            self.trajectory_members.add(mid)
        print(f"Loaded {len(self.trajectory_members)} trajectory-linked atoms")

    def init_review_db(self):
        conn = sqlite3.connect(str(REVIEW_DB))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                prompt_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                notes TEXT DEFAULT '',
                reviewed_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS undo_stack (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_id TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                undone_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        reviewed = self.get_reviewed_ids()
        print(f"Review DB: {len(reviewed)} already reviewed")

    def get_reviewed_ids(self):
        conn = sqlite3.connect(str(REVIEW_DB))
        cursor = conn.execute("SELECT prompt_id FROM reviews")
        ids = {row[0] for row in cursor}
        conn.close()
        return ids

    def build_review_order(self):
        reviewed = self.get_reviewed_ids()
        unreviewed = [a for a in self.atoms if a["id"] not in reviewed]

        # Sort: P0 first, then P1, then trajectory members, then rest by recency
        def sort_key(a):
            p = PRIORITY_ORDER.get(a.get("priority", "P3"), 3)
            is_traj = 0 if a["id"] in self.trajectory_members else 1
            ts = a.get("source", {}).get("timestamp", "") or "0000"
            return (p, is_traj, ts)  # lower = earlier in queue

        unreviewed.sort(key=sort_key)
        # Reverse within priority bands so newest first
        self.review_order = []
        by_priority = {}
        for a in unreviewed:
            p = a.get("priority", "P3")
            by_priority.setdefault(p, []).append(a)
        for p in ["P0", "P1", "P2", "P3"]:
            group = by_priority.get(p, [])
            # Within each priority: trajectory members first, then by date desc
            traj = [a for a in group if a["id"] in self.trajectory_members]
            non_traj = [a for a in group if a["id"] not in self.trajectory_members]
            traj.sort(key=lambda a: a.get("source", {}).get("timestamp", "") or "", reverse=True)
            non_traj.sort(key=lambda a: a.get("source", {}).get("timestamp", "") or "", reverse=True)
            self.review_order.extend(traj)
            self.review_order.extend(non_traj)

    def get_next_unreviewed(self):
        reviewed = self.get_reviewed_ids()
        for atom in self.review_order:
            if atom["id"] not in reviewed:
                return atom
        return None

    def get_assistant_response(self, thread_id, turn_index):
        if not KNOWLEDGE_DB.exists():
            return None
        try:
            conn = sqlite3.connect(str(KNOWLEDGE_DB))
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT content FROM chat_turns
                WHERE thread_id = ? AND turn_index > ? AND role = 'assistant'
                ORDER BY turn_index ASC LIMIT 1
            """, (thread_id, turn_index))
            row = cursor.fetchone()
            conn.close()
            return row["content"] if row else None
        except Exception:
            return None

    def save_review(self, prompt_id, status, notes=""):
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(str(REVIEW_DB))
        # Check if already reviewed (for undo tracking)
        cursor = conn.execute("SELECT status FROM reviews WHERE prompt_id = ?", (prompt_id,))
        old = cursor.fetchone()
        old_status = old[0] if old else None

        conn.execute("""
            INSERT OR REPLACE INTO reviews (prompt_id, status, notes, reviewed_at)
            VALUES (?, ?, ?, ?)
        """, (prompt_id, status, notes, now))
        conn.execute("""
            INSERT INTO undo_stack (prompt_id, old_status, new_status)
            VALUES (?, ?, ?)
        """, (prompt_id, old_status, status))
        conn.commit()
        conn.close()

    def undo_last(self):
        conn = sqlite3.connect(str(REVIEW_DB))
        cursor = conn.execute("SELECT id, prompt_id, old_status FROM undo_stack ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        undo_id, prompt_id, old_status = row
        if old_status:
            conn.execute("UPDATE reviews SET status = ? WHERE prompt_id = ?", (old_status, prompt_id))
        else:
            conn.execute("DELETE FROM reviews WHERE prompt_id = ?", (prompt_id,))
        conn.execute("DELETE FROM undo_stack WHERE id = ?", (undo_id,))
        conn.commit()
        conn.close()
        return prompt_id

    def get_stats(self):
        conn = sqlite3.connect(str(REVIEW_DB))
        total = len(self.atoms)
        cursor = conn.execute("SELECT COUNT(*) FROM reviews")
        reviewed = cursor.fetchone()[0]
        cursor = conn.execute("SELECT status, COUNT(*) FROM reviews GROUP BY status")
        by_status = {row[0]: row[1] for row in cursor}
        conn.close()
        return {
            "total": total,
            "reviewed": reviewed,
            "remaining": total - reviewed,
            "percent": round(100 * reviewed / max(total, 1), 1),
            "by_status": by_status,
        }


server = ReviewServer()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress access logs

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, path):
        try:
            with open(path, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_error(404)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_html(SCRIPT_DIR / "prompt-review.html")

        elif path == "/api/next":
            atom = server.get_next_unreviewed()
            if not atom:
                self.send_json({"done": True, "stats": server.get_stats()})
                return
            # Fetch assistant response
            thread_id = atom.get("source", {}).get("thread_id", "")
            turn_index = atom.get("source", {}).get("turn_index", -1)
            response = server.get_assistant_response(thread_id, turn_index)
            self.send_json({
                "atom": atom,
                "assistant_response": response[:3000] if response else None,
                "stats": server.get_stats(),
            })

        elif path == "/api/stats":
            self.send_json(server.get_stats())

        elif path.startswith("/api/prompt/"):
            prompt_id = path.split("/api/prompt/")[1]
            atom = server.atoms_by_id.get(prompt_id)
            if atom:
                thread_id = atom.get("source", {}).get("thread_id", "")
                turn_index = atom.get("source", {}).get("turn_index", -1)
                response = server.get_assistant_response(thread_id, turn_index)
                self.send_json({"atom": atom, "assistant_response": response})
            else:
                self.send_json({"error": "not found"}, 404)
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_len = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_len)) if content_len else {}

        if path.startswith("/api/review/"):
            prompt_id = path.split("/api/review/")[1]
            status = body.get("status", "")
            notes = body.get("notes", "")
            if status not in ("ACTUALLY_DONE", "STILL_OPEN", "ABANDONED", "SUPERSEDED", "NEEDS_DECOMPOSITION"):
                self.send_json({"error": "invalid status"}, 400)
                return
            server.save_review(prompt_id, status, notes)
            # Return next prompt immediately
            atom = server.get_next_unreviewed()
            if atom:
                thread_id = atom.get("source", {}).get("thread_id", "")
                turn_index = atom.get("source", {}).get("turn_index", -1)
                response = server.get_assistant_response(thread_id, turn_index)
                self.send_json({
                    "saved": True,
                    "atom": atom,
                    "assistant_response": response[:3000] if response else None,
                    "stats": server.get_stats(),
                })
            else:
                self.send_json({"saved": True, "done": True, "stats": server.get_stats()})

        elif path == "/api/undo":
            undone_id = server.undo_last()
            if undone_id:
                atom = server.atoms_by_id.get(undone_id)
                response = None
                if atom:
                    thread_id = atom.get("source", {}).get("thread_id", "")
                    turn_index = atom.get("source", {}).get("turn_index", -1)
                    response = server.get_assistant_response(thread_id, turn_index)
                self.send_json({
                    "undone": True,
                    "atom": atom,
                    "assistant_response": response[:3000] if response else None,
                    "stats": server.get_stats(),
                })
            else:
                self.send_json({"undone": False, "error": "nothing to undo"})
        else:
            self.send_error(404)


def main():
    port = 8080
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        port = int(sys.argv[idx + 1])

    httpd = HTTPServer(("127.0.0.1", port), Handler)
    print(f"\n  Prompt Review Server")
    print(f"  http://localhost:{port}")
    print(f"  {len(server.atoms)} prompts loaded")
    stats = server.get_stats()
    print(f"  {stats['reviewed']} reviewed, {stats['remaining']} remaining")
    print(f"  Press Ctrl+C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.server_close()


if __name__ == "__main__":
    main()
