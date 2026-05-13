---
name: iCloud Desktop & Documents toggle broken — needs Apple Support
description: iCloud Drive has runaway conflict loop creating 300+ duplicate folders, Desktop & Documents toggle greyed out for months, requires Apple server-side reset
type: project
originSessionId: ba85591b-6c24-4fb2-931b-1f23acf5fdc3
---
iCloud Drive "Desktop & Documents Folders" toggle is broken and cannot be enabled. Has been this way for months.

**Diagnosis (2026-03-25):**
- Toggle in System Settings > iCloud > iCloud Drive is greyed out / non-functional
- iCloud server has a runaway conflict loop: Documents folder contains 300+ numbered conflict copies (e.g. `99_System_Backups 89`, `00_Inbox_Triage 66`)
- Conflict copies actively MULTIPLY on every sync cycle — deleting them locally causes bird to re-sync them AND create new higher-numbered copies
- Count went from 244 → 344 → still growing during troubleshooting
- Total estimated 70,000+ files across all conflict copies
- icloud.com web UI cannot handle this volume

**What was tried (all failed):**
1. Deleting conflict copies locally with bird stopped → bird respawns via launchd, re-downloads everything
2. Deleting with bird running → server creates new conflict copies faster than deletion
3. Resetting bird sync databases (`~/Library/Application Support/CloudDocs/session/db`) → clears local queue but server pushes everything back
4. Setting `com.apple.bird is-folder-sync-enabled = true` → bird accepts it but Finder overrides to false on launch
5. Writing `FXICloudDriveDesktop = true` directly to Finder plist → Finder queries iCloud subsystem on launch and resets to false
6. User previously signed out of iCloud and back in → did not fix the issue
7. `brctl evict` on Documents → removes local copies but server references persist

**Root cause:** iCloud server-side CloudDocs zone is corrupted with hundreds of conflict copies in a self-replicating loop. Cannot be fixed from client side.

**Fix required:** Apple Support server-side reset of the iCloud Drive CloudDocs zone.

**When calling Apple Support, say:**
- "My iCloud Drive has a runaway conflict loop creating hundreds of duplicate folders in the Documents directory"
- "The Desktop & Documents Folders toggle in System Settings is greyed out and has been for months"
- "I need a server-side reset of my iCloud Drive CloudDocs zone"
- Account: a.j.padavano@icloud.com
- macOS 26.4 (Tahoe) build 25E246

**Partial resolution (2026-04-18):** Three iCloud conflict snapshot copies in `~/Library/CloudStorage/` removed (8.1 GB total):
- `iCloudDrive-iCloudDrive (2-22-26 10:15 AM)` — 7.1 GB
- `iCloudDrive-iCloudDrive (2-19-26 6:46 PM)` — 967 MB
- `iCloudDrive-iCloudDrive (2-20-26 7:00 AM)` — 64 KB

These were frozen conflict snapshots, not the active replication loop. The underlying server-side corruption still requires Apple Support intervention.

**How to apply:** This blocks iCloud Desktop & Documents sync, which blocks using iCloud as a storage offload strategy for the internal SSD.
