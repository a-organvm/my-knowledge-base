# System Clean-up Walkthrough

## Changes Made

### Moved to External Drive (`/Volumes/4444-iivii/ivi374forivi3ivi3`)

| Item | Source | Destination | Notes |
|------|--------|-------------|-------|
| **Toolbox** | `~/toolbox` | `toolchains/bin/toolbox` | |
| **Tools Config** | `~/tools.yaml` | `toolchains/tools.yaml` | |
| **Settings** | `~/settings.json` | `toolchains/settings.json` | |
| **Tmux** | `~/tmux/` | `toolchains/tmux/` | |
| **Extension Backups** | `~/extension-backups/` | `toolchains/extension-backups/` | |
| **Dotfiles** | `~/dot-files/` | `toolchains/dot-files/` | Excluded `.config/goose` cache |
| **Go** | `~/go/` | `toolchains/go/` | |
| **Temp Project** | `~/temp-project/` | `workspace/scratch/temp-project/` | |
| **Tests** | `~/tests/` | `intake-toSORT/tests/` | |

### Deleted from Local (`~`)

- `~/Development/` (Empty/Redundant)
- `~/go/` (After move)
- `~/dot-files/` (After move, except one root-owned log file)
- `~/tmux/`
- `~/toolbox`
- `~/tools.yaml`
- `~/settings.json`
- `~/extension-backups/`
- `~/temp-project/`
- `~/tests/`

## Verification Results

### System Check
- **Home Directory**: Cleaned of dev folders.
- **Remaining Items**: `dot-files` folder remains due to a single root-owned file (`.newrelic/newrelic-cli.log`) which requires `sudo` to delete.
- **External Drive**: All items verified in their new locations.

### Manual Verification
Run `ls -F ~` to see the clean home directory.
