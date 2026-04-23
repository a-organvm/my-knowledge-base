#!/usr/bin/env python3
"""Dropbox remote file operations for the knowledge base.

List, download, and sync files from Dropbox using the API.
Requires DROPBOX_ACCESS_TOKEN environment variable.

Usage:
    python tools/dropbox_remote.py list /path/in/dropbox
    python tools/dropbox_remote.py download /path/in/dropbox/file.txt --output ./local/
    python tools/dropbox_remote.py sync /remote/path --local ./raw/dropbox/
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("dropbox.remote")

DROPBOX_API_BASE = "https://api.dropboxapi.com/2"
DROPBOX_CONTENT_BASE = "https://content.dropboxapi.com/2"


def get_token() -> str:
    """Retrieve Dropbox access token from environment."""
    token = os.environ.get("DROPBOX_ACCESS_TOKEN", "")  # allow-secret
    if not token:
        logger.error("DROPBOX_ACCESS_TOKEN environment variable not set")
        logger.info("Set it via: export DROPBOX_ACCESS_TOKEN='your-token'")
        sys.exit(1)
    return token


def api_request(endpoint: str, data: dict[str, Any], token: str) -> dict[str, Any]:  # allow-secret
    """Make an authenticated Dropbox API request."""
    url = f"{DROPBOX_API_BASE}/{endpoint}"
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        logger.error("API error %d: %s", e.code, error_body)
        raise


def list_folder(path: str, token: str, recursive: bool = False) -> list[dict[str, Any]]:  # allow-secret
    """List files in a Dropbox folder."""
    entries: list[dict[str, Any]] = []
    result = api_request("files/list_folder", {
        "path": path if path != "/" else "",
        "recursive": recursive,
        "limit": 2000,
    }, token)

    entries.extend(result.get("entries", []))

    # Handle pagination
    while result.get("has_more"):
        result = api_request("files/list_folder/continue", {
            "cursor": result["cursor"],
        }, token)
        entries.extend(result.get("entries", []))

    return entries


def download_file(remote_path: str, local_path: Path, token: str) -> bool:  # allow-secret
    """Download a single file from Dropbox."""
    url = f"{DROPBOX_CONTENT_BASE}/files/download"
    api_arg = json.dumps({"path": remote_path})

    req = Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Dropbox-API-Arg", api_arg)
    req.add_header("Content-Type", "application/octet-stream")

    try:
        with urlopen(req, timeout=120) as resp:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                while chunk := resp.read(8192):
                    f.write(chunk)
        logger.info("Downloaded: %s -> %s", remote_path, local_path)
        return True
    except HTTPError as e:
        logger.error("Download failed for %s: %d", remote_path, e.code)
        return False


def cmd_list(args: argparse.Namespace) -> int:
    """List command handler."""
    token = get_token()  # allow-secret
    entries = list_folder(args.path, token, recursive=args.recursive)

    for entry in entries:
        tag = entry.get(".tag", "unknown")
        name = entry.get("path_display", entry.get("name", "?"))
        size = entry.get("size", "")
        modified = entry.get("server_modified", "")

        if tag == "file":
            size_str = f" ({size:,} bytes)" if size else ""
            mod_str = f" [{modified}]" if modified else ""
            print(f"  {name}{size_str}{mod_str}")
        elif tag == "folder":
            print(f"  {name}/")

    logger.info("Total entries: %d", len(entries))
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    """Download command handler."""
    token = get_token()  # allow-secret
    output = Path(args.output) if args.output else Path(".")
    local_path = output / Path(args.path).name

    success = download_file(args.path, local_path, token)
    return 0 if success else 1


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync command handler."""
    token = get_token()  # allow-secret
    local_dir = Path(args.local)

    entries = list_folder(args.path, token, recursive=True)
    files = [e for e in entries if e.get(".tag") == "file"]

    logger.info("Found %d files to sync from %s", len(files), args.path)

    success = 0
    skipped = 0
    failed = 0

    for entry in files:
        remote_path = entry["path_display"]
        # Preserve directory structure relative to sync root
        relative = remote_path[len(args.path):].lstrip("/")
        local_path = local_dir / relative

        # Skip if local file exists and is same size
        if local_path.exists():
            local_size = local_path.stat().st_size
            remote_size = entry.get("size", -1)
            if local_size == remote_size:
                skipped += 1
                continue

        if download_file(remote_path, local_path, token):
            success += 1
        else:
            failed += 1

    logger.info("Sync complete: %d downloaded, %d skipped, %d failed", success, skipped, failed)
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Dropbox remote file operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("list", help="List folder contents")
    p_list.add_argument("path", help="Dropbox path (e.g., /Documents)")
    p_list.add_argument("--recursive", action="store_true")

    # download
    p_dl = subparsers.add_parser("download", help="Download a file")
    p_dl.add_argument("path", help="Remote file path")
    p_dl.add_argument("--output", help="Local output directory")

    # sync
    p_sync = subparsers.add_parser("sync", help="Sync a folder")
    p_sync.add_argument("path", help="Remote folder path")
    p_sync.add_argument("--local", required=True, help="Local directory")

    args = parser.parse_args()

    handlers = {
        "list": cmd_list,
        "download": cmd_download,
        "sync": cmd_sync,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
