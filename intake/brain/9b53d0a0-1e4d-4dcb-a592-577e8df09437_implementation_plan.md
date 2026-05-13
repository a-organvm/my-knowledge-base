# Agentic Python Install Matrix — Implementation Plan

Fill the gap identified in both research documents: multi-agent orchestration frameworks and agentic CLI tools are Python packages that belong in `uv`/`pipx`, not Homebrew. This plan integrates every actionable recommendation from *both* source documents into the existing `domus-packages` tracking infrastructure.

---

## User Review Required

> [!CAUTION]
> **XDG Override Conflict**: Doc 2 proposes overriding `XDG_CACHE_HOME`, `XDG_STATE_HOME`, and `XDG_CONFIG_HOME` to point into `_agents/`. This would **break** chezmoi, nvim, starship, atuin, git, and every other tool that depends on the current XDG paths set in `dot_zshenv`. **Recommendation: reject this.** Instead, we scope agent state under `_agents/` using dedicated vars (`AGENTS_CACHE`, `AGENTS_STATE`, etc.) without touching the system-wide XDG vars.

> [!IMPORTANT]
> **PIPX_HOME / PIPX_BIN_DIR relocation**: Doc 2 relocates pipx entirely under `_agents/pipx` with binaries in `_agents/bin`. This means existing pipx installs (pywal, pplx-cli, jupyter-mcp-server) would need to be reinstalled. Alternatively, we can keep pipx at its defaults (`~/.local/pipx`, `~/.local/bin`) since `~/.local/bin` is already on PATH. **Which do you prefer?**

> [!IMPORTANT]
> **`ollama` installation**: Doc 1 strongly recommends `brew install ollama` for local-first Goose workflows. Adding it to the manifest will make `domus packages apply` install it. Ollama runs a background service and downloads large model files. **Confirm you want this in the manifest.**

> [!IMPORTANT]
> **Package selection**: The full matrix from both docs includes far more packages than my initial plan. Review the complete lists below.

---

## Proposed Changes

### Phase 1: Manifest & Package Declarations

#### [MODIFY] [manifest.yaml](file:///Users/4jp/domus-semper-palingenesis/dot_config/domus/manifest.yaml)

**1a. Add `ollama` to homebrew formulae** (Doc 1, lines 63–83):
```diff
       # AI tools
       - block-goose-cli
       - gemini-cli
       - huggingface-cli
       - kimi-cli
+      # Local inference backend (Goose integration)
+      - ollama
```

**1b. Expand `pipx:` with Lane A agentic CLIs** (Doc 2, lines 229–256):
```yaml
  pipx:
    - pywal
    - pplx-cli
    - jupyter-mcp-server
    # Lane A: Agent CLIs (isolated executables)
    - aider-chat          # Git-integrated coding agent
    - open-interpreter    # Agent + tool runner for local scripting
    # Quality gates (agents iterate against these)
    - ruff
    - mypy
    - pytest
```

**1c. Add new `uv_tools:` section** (Doc 2, lines 229–256):
```yaml
  uv_tools:
    # MCP ecosystem tooling
    - "mcp[cli]"
    # Multi-agent framework CLIs
    - crewai
    - smolagents
```

---

### Phase 2: Package Tracking Infrastructure

#### [MODIFY] [executable_domus-packages](file:///Users/4jp/domus-semper-palingenesis/dot_local/bin/executable_domus-packages)

Add `uv_tools` as a sixth package manager:

**New functions:**
```bash
# Get installed uv tool packages
get_installed_uv_tools() {
  if command -v uv &>/dev/null; then
    uv tool list 2>/dev/null | grep -v '^ ' | awk '{print $1}' | sort
  fi
}

get_manifest_uv_tools() {
  yq -r '.packages.uv_tools[]? ' "${MANIFEST}" 2>/dev/null |
    sed 's/\[.*\]//g' | sort  # Strip extras brackets for comparison
}
```

**Wiring:** Add `"uv_tools"` case to `cmd_status`, `cmd_diff`, `cmd_apply` (with `uv tool install`), and `cmd_snapshot`.

---

### Phase 3: Agent State Directory & Environment

#### [NEW] [`.chezmoiscripts/run_after_create-agents-dirs.sh`](file:///Users/4jp/domus-semper-palingenesis/.chezmoiscripts/run_after_create-agents-dirs.sh)

Chezmoi run_after script to ensure the `_agents/` skeleton exists:
```bash
#!/usr/bin/env bash
set -euo pipefail
DOMUS_ROOT="${HOME}/domus-semper-palingenesis"
mkdir -p \
  "$DOMUS_ROOT/_agents/bin" \
  "$DOMUS_ROOT/_agents/cache" \
  "$DOMUS_ROOT/_agents/state" \
  "$DOMUS_ROOT/_agents/log" \
  "$DOMUS_ROOT/_agents/config" \
  "$DOMUS_ROOT/_agents/lab" \
  "$DOMUS_ROOT/projects" \
  "$DOMUS_ROOT/_registry"
```

#### [MODIFY] [15-env.zsh](file:///Users/4jp/domus-semper-palingenesis/dot_config/zsh/15-env.zsh)

Add agent workspace & Python toolchain env block (Doc 2, lines 173–189, 484–491):

```zsh
# ── Agent workspace hierarchy ──
# Root anchored to dotfiles repo per convention
export DOMUS_ROOT="$HOME/domus-semper-palingenesis"
export AGENTS_ROOT="$DOMUS_ROOT/_agents"
export AGENTS_BIN="$AGENTS_ROOT/bin"
export AGENTS_CACHE="$AGENTS_ROOT/cache"
export AGENTS_STATE="$AGENTS_ROOT/state"
export AGENTS_LOG="$AGENTS_ROOT/log"
export WORKSPACE_ROOT="$DOMUS_ROOT/projects"

# Python tooling (uv / pipx)
export UV_PYTHON_PREFERENCE="only-managed"
export UV_CACHE_DIR="$AGENTS_CACHE/uv"
export UV_PYTHON="python3.11"
export PIPX_DEFAULT_PYTHON="python3.11"

# Aider (agent model selection)
export AIDER_MODEL="${AIDER_MODEL:-}"
```

> Note: We do **NOT** override `XDG_CACHE_HOME`/`XDG_STATE_HOME`/`XDG_CONFIG_HOME` — those stay at their system-wide defaults. Agent caches go into `$AGENTS_CACHE` via tool-specific vars like `UV_CACHE_DIR`.

#### [MODIFY] [10-path.zsh.tmpl](file:///Users/4jp/domus-semper-palingenesis/dot_config/zsh/10-path.zsh.tmpl)

```diff
 # pipx local bin
 export PATH="$HOME/.local/bin:$PATH"
+
+# Agent tools bin (scripts under _agents/bin)
+export PATH="$HOME/domus-semper-palingenesis/_agents/bin:$PATH"
```

#### Provider API keys

Doc 2 prescribes `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `HUGGINGFACE_TOKEN`. These are secrets and should NOT be in plaintext shell init. Your existing infra uses 1password-cli. These should go in `99-local.zsh.tmpl` or a secrets template. **No code change needed** — just a note that they're expected to be set via 1Password or `.env` files per project.

---

### Phase 4: Agent Run Harness

#### [NEW] [agent-run](file:///Users/4jp/domus-semper-palingenesis/dot_local/bin/executable_agent-run)

Shell script (Doc 2, lines 537–543) that:
1. Creates timestamped `$AGENT_RUN_DIR`
2. Snapshots `git status`, `git diff --stat`
3. Captures prompt to `prompt.md`
4. Runs the chosen agent CLI
5. Runs quality gates (`ruff check .`, `pytest -q`, `pre-commit run --all-files`)
6. Writes a run report (`report.md` + `report.json`)

#### [NEW] [agent-tmux](file:///Users/4jp/domus-semper-palingenesis/dot_local/bin/executable_agent-tmux)

4-pane tmux "swarm" layout (Doc 2, lines 333–380):
- Pane 1: Agent CLI placeholder
- Pane 2: `while true; do uv run pytest -q || true; sleep 2; done`
- Pane 3: `watch -n 2 "git status --porcelain=v1 && echo '---' && git diff --stat"`
- Pane 4: `tail -f "$AGENT_RUN_DIR"/tool_*.json 2>/dev/null | jq .`

---

### Phase 5: Agent Lab Project Scaffold (Lane B)

#### [NEW] [`_agents/lab/pyproject.toml`](file:///Users/4jp/domus-semper-palingenesis/_agents/lab/pyproject.toml)

Per-project uv venv for multi-agent DAG experiments (Doc 2, lines 266–303):
```toml
[project]
name = "agent-lab"
version = "0.1.0"
requires-python = ">=3.11,<3.12"
dependencies = [
    "langgraph",
    "autogen-agentchat",
    "crewai",
    "smolagents",
    "rich",
    "pydantic",
    "httpx",
]
```

#### [NEW] [`_agents/lab/.python-version`](file:///Users/4jp/domus-semper-palingenesis/_agents/lab/.python-version)
```
3.11
```

---

### Phase 6: .chezmoiignore update

#### [MODIFY] [.chezmoiignore](file:///Users/4jp/domus-semper-palingenesis/.chezmoiignore)

Add `_agents/` and `projects/` to ignore list so chezmoi doesn't try to manage agent runtime state:
```diff
+_agents/cache/**
+_agents/state/**
+_agents/log/**
+_agents/lab/.venv/**
+projects/**
```

---

## Verification Plan

### Automated Tests
```bash
cd /Users/4jp/domus-semper-palingenesis && just test
cd /Users/4jp/domus-semper-palingenesis && just lint
yq '.' dot_config/domus/manifest.yaml > /dev/null && echo "valid"
```

### Manual Verification
```bash
# Dry-run to see all new packages
bash dot_local/bin/executable_domus-packages apply --dry-run

# Status includes uv_tools
bash dot_local/bin/executable_domus-packages status --json

# Diff shows new packages as missing
bash dot_local/bin/executable_domus-packages diff

# Snapshot captures uv_tools
bash dot_local/bin/executable_domus-packages snapshot
cat ~/.local/state/domus/snapshots/snapshot-*.json | jq '.packages.uv_tools'

# Agent-run script is executable and shows help
bash dot_local/bin/executable_agent-run --help

# Agent-tmux launches correctly
bash dot_local/bin/executable_agent-tmux --dry-run
```

### Plan File Discipline
Save the final plan to `.gemini/plans/2026-03-05-agentic-python-matrix.md`.
