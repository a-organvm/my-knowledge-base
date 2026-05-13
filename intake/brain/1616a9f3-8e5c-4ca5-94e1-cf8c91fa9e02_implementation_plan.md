# System Clean-up Implementation Plan

## Goal Description
Move development folders, configuration files, and loose items from the local MacBook home directory to the external drive (`/Volumes/4444-iivii/ivi374forivi3ivi3`) to keep the local system light and organized.

## User Review Required
> [!IMPORTANT]
> **Deletion of `~/Development`**: This folder contains only hidden files (`.git`, `.vscode`, etc.) and appears to be a leftover from a previous migration. I plan to delete it.
> **Moving Configs**: `dot-files`, `tmux`, and `toolbox` will be moved. Ensure you update your paths/symlinks if these are currently active.
> **[NEW] Excluding Cache**: The `~/dot-files` move was slow due to a large `goose` cache (~400MB). I will exclude `.config/goose` from the move to speed it up.

## Proposed Changes

### Move to External Drive (`/Volumes/4444-iivii/ivi374forivi3ivi3`)

#### Toolchains
- [MOVE] `~/dot-files/` -> `toolchains/dot-files/` (Excluding `.config/goose`)
- [MOVE] `~/tmux/` -> `toolchains/tmux/`
- [MOVE] `~/toolbox` -> `toolchains/bin/toolbox` (Will create `bin` if missing)
- [MOVE] `~/tools.yaml` -> `toolchains/tools.yaml`
- [MOVE] `~/settings.json` -> `toolchains/settings.json`

#### Workspace/Scratch
- [MOVE] `~/temp-project/` -> `workspace/scratch/temp-project/`

#### Intake/Sort
- [MOVE] `~/tests/` -> `intake-toSORT/tests/`

### Clean up Local
- [DELETE] `~/Development/` (After verifying it contains no user data)

## Verification Plan

### Manual Verification
1.  **Verify Moves**: Check that files exist in the new locations on the external drive.
2.  **Verify Clean-up**: Check that `~/dot-files`, `~/tmux`, `~/Development`, etc. are gone from the home directory.
3.  **System Check**: Run `ls -la ~` to confirm a clean home directory.
