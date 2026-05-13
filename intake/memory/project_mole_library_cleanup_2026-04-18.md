---
name: Mole optimize fix + ~/Library/ deep clean
description: Patched mole periodic maintenance for Tahoe, cleaned 37 GB from ~/Library/ (dead apps, Messages tmp, iCloud conflicts)
type: project
originSessionId: ba85591b-6c24-4fb2-931b-1f23acf5fdc3
---
Session S-mole-optimize-2026-04-18.

**Mole periodic fix:** Apple removed `periodic` binary from macOS Tahoe (26.x). Patched `~/.config/mole/lib/optimize/tasks.sh` `opt_periodic_maintenance()` — added `command -v periodic` guard; fallback runs `newsyslog`, `locate.updatedb`, `makewhatis` directly.

**Why:** `mo optimize` showed permanent `◎ Failed to run periodic maintenance` on every run.

**VACUUM:** `~/.config/mole/` is LOCAL ONLY — not tracked by chezmoi or git. Machine death = total loss. IRF-DOM-042.

**~/Library/ cleanup — 37 GB reclaimed (82 GB → 46 GB):**
- Android SDK 15 GB (Android Studio not installed)
- Docker installer 2.3 GB (Docker uninstalled 2026-04-18)
- Microsoft Edge 460 MB (not installed)
- Unity Hub 331 MB (not installed)
- OneDrive data 1.6 GB (not installed; mount point persists — needs manual System Settings removal)
- Messages tmp 17 GB (cached attachments)
- iCloud conflict copies 8.1 GB (from known sync bug, IRF project_icloud_folder_sync_broken)
- CloudKit cache 1 GB
- CoreSimulator 1.1 GB

**GeminiAppLauncher:** Mole reported broken login item — actually running fine (PID active, exit 0). False positive from Mole's SMAppService heuristic. Resolved itself in subsequent run.

**How to apply:** When cleaning ~/Library/ in future, cross-reference `~/Library/Application Support/` and `~/Library/Group Containers/` against `/Applications/` to detect orphans. Mole's built-in check misses most of these.
