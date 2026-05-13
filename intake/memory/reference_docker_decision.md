---
name: Docker decision framework
description: When to use Docker vs native processes — single-question heuristic for a non-programmer building multi-service apps
type: reference
originSessionId: 6f7b12a9-79f4-48db-b07c-b689e0400082
---
## Docker Governance — Decision Heuristic

One question: **"How many separate processes need to talk to each other?"**

- **One process** → run natively, LaunchAgent if persistent
- **Two+ coordinated processes** (API + database, app + cache + worker) → Docker Compose
- **Deploying to cloud** → Docker (the Dockerfile IS the deploy config)

### Agent signals to watch for

| Agent creates... | Decision |
|-----------------|----------|
| `docker-compose.yml` | Accept — it's wiring a multi-service stack |
| `docker run` for a CLI tool | Push back — install natively |
| Docker for an MCP server | Push back — single process, use npx or binary |
| `Dockerfile` only (no compose) | Question it — might be unnecessary packaging |

### Never use Docker for

- Single-process tools (CLI, MCP server, script)
- Static sites or frontend-only apps
- Prototyping (add Docker later when the shape stabilizes)

### Always use Docker for

- App needs database + API at minimum
- Project already has `docker-compose.yml`
- Targeting cloud container runtime (ECS, Cloud Run, Kubernetes)

**Why:** Docker Desktop costs ~15GB disk + ~1.5GB RAM on macOS (runs a Linux VM).
On a 16GB machine, that's a real tax for infrastructure that may not be needed.
Keep Docker quit by default; launch only when a project's shape requires it.
