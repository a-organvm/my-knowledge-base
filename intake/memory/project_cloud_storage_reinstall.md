---
name: cloud-storage-reinstall-s35
description: S35 (2026-03-24) — Dropbox and Google Drive nuke-and-pave via Homebrew casks, replacing broken manual installs
type: project
---

Dropbox and Google Drive clean reinstall completed 2026-03-24 (S35).

**Why:** Dropbox had been broken for extended period — crashed app (`app_crashed.dbx`), empty File Provider mount, 760MB stale data across 8 locations, 3 orphaned LaunchAgent updaters. Google Drive worked but was manually installed with no upgrade path.

**How to apply:**
- Both now installed via Homebrew casks (`brew install --cask dropbox google-drive`) — `brew upgrade` manages updates
- Old Dropbox XDG relocation (`~/.dropbox → ~/.local/share/dropbox`) is gone; fresh install uses `~/.dropbox` directly
- rclone remotes (`dbx:`, `gdrive:`, `onedrive:`) remain as backup access paths, independent of desktop apps
- 3 stale iCloud snapshots in `~/Library/CloudStorage/` need reboot to clear (read-only File Provider mounts)
- **Critical gap discovered:** domus has NO Brewfile — new machine bootstrap won't get these casks. IRF-DOM-010 (P1), GH#4
- IRF-DOM-009 through 012 created for follow-up work
- Dropbox CLI wrapper at `~/.local/bin/dropbox` may need path update (IRF-DOM-012)
- **Deep vacuum audit** found 6 more items (IRF-DOM-013 through 018):
  - CLAUDE.md falsely claims Brewfile trigger (actually inline `brew install`)
  - install-packages.sh omits 30+ formulae vs actual installed set
  - seed.yaml missing external deps (Dropbox, GDrive, rclone, Backblaze)
  - Omega #17 evidence gap — Dropbox failure was unreported autonomous ops incident
  - No infrastructure resilience research commission in inquiry log
  - Testament fossil record has no INFRA_INCIDENT event type
- Total: 10 new IRF-DOM items (009-018) from this session
- **TODO (2026-03-25):** Dropbox wants to upload ~1TB after fresh install. Two issues:
  1. **Why 1TB?** Check sync mode (may have defaulted to mirror instead of stream/online-only), check what folder scope it's pointed at, check if it's indexing paths it shouldn't
  2. **Exclude node/npm junk** — Dropbox has no native .gitignore support. Options: (a) Selective Sync in Preferences to exclude dirs with node_modules, (b) Dropbox CLI `exclude add` for specific paths, (c) `.dropboxignore` via third-party tool (`maestral` or `dropboxignore`), (d) move dev workspace out of Dropbox sync root entirely. Key patterns to exclude: `node_modules/`, `.npm/`, `package-lock.json` (debatable), `.next/`, `.nuxt/`, `dist/`, `.cache/`, `.turbo/`, `.venv/`, `__pycache__/`, `.git/` objects. The 1TB is almost certainly node_modules — a workspace with 100+ repos each with a node_modules could easily hit that.
