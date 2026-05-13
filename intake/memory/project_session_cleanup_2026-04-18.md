---
name: Session S-cleanup-2026-04-18 — Docker uninstall, 1Password recovery, memory pipeline
description: Full session atomization — 22 events, Docker uninstalled (17GB), 1Password recovered, memory persistence pipeline built, 4 IRF items, omega evidence updated
type: project
originSessionId: 6f7b12a9-79f4-48db-b07c-b689e0400082
---
## Session: S-cleanup-2026-04-18

**Scope:** System cleanup, Docker governance, infrastructure recovery, memory persistence automation
**Repos touched:** `domus-semper-palingenesis` (master), `organvm-corpvs-testamentvm` (main)
**Free space:** 92Gi → 109Gi (+17GB)

## Atomized Event Log

| ID | Action | Result | Cross-ref |
|----|--------|--------|-----------|
| EVT-001 | Analyzed `mo` cleanup output | Identified Docker (15.4GB), CoreSim (1.6GB), caches, downloads | — |
| EVT-002 | `docker system df -v` analysis | 14 unused images (~4.2GB), 10 dangling volumes, 1.4GB anon vol | — |
| EVT-003 | `docker rmi` × 14 images | Stale MCP server images removed (desktop-commander, fetch, git, filesystem, etc.) | — |
| EVT-004 | `docker volume rm` × 10 | Dangling volumes removed (peer-audited, minio, postgres, claude-memory, etc.) | — |
| EVT-005 | `xcrun simctl delete unavailable` | CoreSimulator 1.6GB→1.1GB, 2 devices remaining | — |
| EVT-006 | Apple cache cleanup | ~611MB freed (textunderstandingd, python, Music) | — |
| EVT-007 | Downloads cleanup | ~155MB freed (Backblaze DMG, drive-download zip) | — |
| EVT-008 | Docker education | Explained via chezmoi analogy; shape determines Docker need | — |
| EVT-009 | Docker decision framework | Single-question heuristic: "how many processes talk to each other?" | — |
| EVT-010 | Memory: reference_docker_decision.md | Created + indexed in MEMORY.md | `dfd6a1a` |
| EVT-011 | AGENTS.md.tmpl updated | Docker Governance section added | `dfd6a1a` |
| EVT-012 | Docker Desktop uninstalled | App, VM, helpers, daemons, caches — 17GB freed | — |
| EVT-013 | MCP breakage discovered | `MCP_DOCKER` + `github` servers depend on Docker | IRF-DOM-033, GH#27 |
| EVT-014 | 1Password failure discovered | Binary missing since Apr 17 03:41 AM (Squirrel auto-update failure) | IRF-DOM-035 |
| EVT-015 | 1Password reinstalled | `brew install --cask 1password` → op-ssh-sign restored | — |
| EVT-016 | Session audit — 6 gaps found | Uncommitted work, untracked files, stale memory, missing IRF | All fixed |
| EVT-017 | Memory: project_docker_storage_design.md | Updated: Docker capped → Docker uninstalled | `dfd6a1a` |
| EVT-018 | IRF DOM-033–036 created | 4 new items in PERSONAL domain | `0013012` |
| EVT-019 | GH Issue #27 created | P0: broken Docker-dependent MCP servers | IRF-DOM-033 |
| EVT-020 | Omega evidence updated | #1 soak: incident 0→1; #17: propagation gap documented | `37ee084` |
| EVT-021 | N/A vacuum audit | 10-index: 3 SKIPs→DONE, 7 genuinely N/A with reasons | — |
| EVT-022 | Feedback: never overwrite plans | Universal rule #3 conflict with plan mode caught | feedback_never_overwrite_plans.md |

## Artifacts Created

| Artifact | Path | Commit |
|----------|------|--------|
| Docker decision memory | `reference_docker_decision.md` | `dfd6a1a` |
| Docker storage memory (updated) | `project_docker_storage_design.md` | `dfd6a1a` |
| AGENTS.md Docker governance | `AGENTS.md.tmpl` | `dfd6a1a` |
| Plan file (additive) | `starry-foraging-wigderson.md` | `dfd6a1a` |
| IRF DOM-033–036 | `INST-INDEX-RERUM-FACIENDARUM.md` | `0013012`, `f1c1191` |
| Omega evidence (#1, #17) | `omega-evidence-map.md` | `37ee084` |
| GH Issue | 4444J99/domus-semper-palingenesis#27 | — |
| Overwrite feedback | `feedback_never_overwrite_plans.md` | this commit |
| This session record | `project_session_cleanup_2026-04-18.md` | this commit |
| Memory sync script | `executable_domus-memory-sync` | this commit |
| Memory sync hook | `settings.json.tmpl` PostToolUse | this commit |
| Memory sync LaunchAgent | `com.4jp.memory-sync.plist.tmpl` | this commit |

## Decisions Made

1. Docker uninstalled — 17GB dead weight, no active project needs it, `brew install --cask docker` to reinstall
2. Docker governance: single-question heuristic added to AGENTS.md for all agents
3. 1Password reinstalled via Homebrew cask (was corrupted by Squirrel auto-updater on macOS beta)
4. Memory persistence pipeline designed and built: PostToolUse hook + LaunchAgent + sync script
5. Signing fallback: unsigned commits allowed when 1Password unavailable — [(local):(remote)={1:1}] outranks signing
