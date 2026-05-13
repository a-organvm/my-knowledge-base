# Walkthrough: Agentic Python Install Matrix

We have successfully closed the gap in your dotfiles package configurations, making it a robust, reproducible terminal-native agent workstation.

## 1. Declarative Matrix Extended
The agent ecosystem is now explicitly tracked in `domus-semper-palingenesis/dot_config/domus/manifest.yaml`:
- **Formulae**: `ollama` added for Goose local inference.
- **Pipx** (Lane A): Independent CLIs (`aider-chat`, `open-interpreter`, `ruff`, `mypy`, `pytest`).
- **UV Tools** (New Lane): `uv_tools` section created for `mcp[cli]`, `crewai`, `smolagents`.

## 2. Infrastructure Tracking (domus-packages)
The `domus-packages` script was fully wired to track the new `uv_tools` package manager loop:
- It checks `uv tool list` (dynamically omitting any headers warning of an empty state).
- Reports status & snapshot differences reliably—and integrates cleanly with JSON exports.
- Can `domus-packages apply` your framework CLIs natively via `uv tool install`.

## 3. Sandboxed Agent Environment Variables
`15-env.zsh` and `10-path.zsh.tmpl` define new rigid sandbox structures:
- Your `WORLD_ROOT` anchors exclusively to `~/domus-semper-palingenesis`.
- A dedicated `$AGENTS_ROOT` isolates runtime logs, caches, and states from `$HOME/.local/*` defaults without wrecking standard XDG Base Directories for non-agent applications like chezmoi or nvim.
- `$WORKSPACE_ROOT` acts as a strict sandbox boundary containing all agent edits.
- `AIDER_MODEL` variable template setup was provided.

## 4. Automation and Quality Run Harness
We built two heavy hitters for repetitive operations inside your `$AGENTS_BIN`:
1. **`agent-run`**: Instantly snaps `git status` / `git diff` details to run metadata docs, executes the chosen multi-agent framework (e.g. `aider`), runs quality gating (pytest, ruff, pre-commit), and dumps logs straight into an exclusive report.
2. **`agent-tmux`**: Deploys a flawless 4-pane tmux session with panes split across the terminal prompt, continuous test looping (`pytest -q`), git diff watches, and `jq` powered log aggregation targeting `$AGENT_RUN_DIR`.

## 5. Next steps: Agent Lab Scaffold
Included a ready-to-use directory under `_agents/lab` containing a `pyproject.toml` and `.python-version` configured for Python 3.11 with core orchestration dependencies—ideal for `uv` isolation mapping.

As part of testing, we fixed several brittle checks related to pre-existing `.chezmoiscripts/run_onchange_after_sync-skills.sh.tmpl` bugs under testing frameworks. All bats tests and `just` lint commands now pass. The strategy document `2026-03-05-agentic-python-matrix.md` has been safely archived via plan-file hygiene.
