---
name: Conductor MCP server
description: Conductor OS now live as MCP server — session lifecycle, fleet dispatch, oracle diagnostics, workflow orchestration
type: reference
---

The Conductor MCP server is live as of 2026-04-14. Tools available as `mcp__conductor__*` in the deferred tool list.

**Location:** `~/Workspace/organvm-iv-taxis/tool-interaction-design/`
**Venv:** `.venv/bin/python3` (Python 3.11, mcp 1.27.0 installed 2026-04-14)
**Entry point:** `mcp_server.py` → `main()` → `asyncio.run(run_server())`
**Config:** Injected via `modify_dot_claude.json.tmpl` in domus (chezmoi modify mode)

**Key tool groups:**
- `conductor_session_start/transition/phase` — FRAME→SHAPE→BUILD→PROVE lifecycle
- `conductor_fleet_*` — multi-agent dispatch, status, recommendations
- `conductor_oracle_*` — diagnostics, calibration, trends, gate checks
- `conductor_guardian_*` — corpus, counsel, mastery, teaching
- `conductor_patch` — system state snapshot (fallback when MCP unavailable)

**When to use:** The Workspace CLAUDE.md prescribes: call `conductor_session_start` before beginning work, follow the FRAME→SHAPE→BUILD→PROVE lifecycle with hard gates. If conductor is unavailable, fall back to `python3 -m conductor patch --json`.

**Fix history:** Conductor venv was missing the `mcp` package (optional dependency not installed). Fixed 2026-04-14 by bootstrapping pip (`ensurepip`) then `pip install "mcp>=0.1"`.
