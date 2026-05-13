---
name: System storage cleanup — executed + Docker uninstalled
description: Storage cleanup history — S35 (2026-03-25) initial pass, S-cleanup-2026-04-18 Docker fully uninstalled (17GB reclaimed, 92Gi→109Gi)
type: project
originSessionId: 6f7b12a9-79f4-48db-b07c-b689e0400082
---
## S35 Storage cleanup (2026-03-25)

**Internal SSD (494 GB):**
- Before: 402 GB used (81.3%) → After: 367 GB used (74.2%)
- Freed ~35 GB: caches, Anaconda, Chrome Canary, Claude vm_bundles, Ollama→SSD, Logic Pro→SSD
- iCloud Optimize Mac Storage enabled
- Google Drive already in streaming mode (0 bytes local)

**External SSD (4 TB, "4444-iivii"):**
- Before: 2.7 TB used (68.7%) → After: 1.1 TB used (31%), freed ~1.6 TB
- iCloud-Recovery (214 GB) is IRREPLACEABLE — user lost iCloud backup
- Rescued-From-Chaos has 2,155 photos (possibly only copy)
- `input-keys-log` and `jvpiter-inquiry-labors` repos NOT on GitHub — only copies on SSD

## S-cleanup-2026-04-18 — Docker uninstalled + deep clean

**Docker Desktop fully uninstalled:**
- Removed: app (2.2GB), VM disk (14GB), privileged helpers (14.3MB), launch daemons, all caches/prefs
- Free space: 92Gi → 109Gi (+17GB)
- Reinstall if needed: `brew install --cask docker`
- Decision framework saved in AGENTS.md and Claude memory

**Also cleaned:**
- 14 stale Docker images (~4.2GB MCP servers), 10 dangling volumes (~119MB)
- CoreSimulator unavailable devices (~500MB)
- Apple caches: textunderstandingd, python, Music (~611MB)
- Chrome old versions (694MB)
- Downloads: Backblaze installer, duplicate archive (~155MB)

**BROKEN by uninstall — needs fix:**
- `MCP_DOCKER` server in .claude.json → `docker mcp gateway run` (remove)
- `github` MCP server in .claude.json → `docker run ghcr.io/github/github-mcp-server` (convert to native npx)
- See IRF-DOM-033

**Still TODO (from S35):**
- System Settings: add ~/Library/CloudStorage/ to Spotlight Privacy
- Google Drive: delete dev garbage from "Other computers/My Mac"
- Time Machine: see project_timemachine_ssd_conversion.md
- Dropbox: configure Smart Sync online-only defaults
