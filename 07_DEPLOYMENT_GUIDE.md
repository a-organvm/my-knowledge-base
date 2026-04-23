# 07: Deployment Guide

**Atom ID:** prompt-deployment-guide
**Status:** ACTIVE
**References:** 5 cross-references in knowledge base corpus

---

## Purpose

This guide governs the end-to-end deployment of the My Knowledge Base system, from local development through staging to production. It complements `docs/DEPLOYMENT.md` (which covers environment variables and Docker configuration) by addressing the operational sequence, verification gates, and rollback procedures.

## Deployment Targets

| Target | Stack | URL Pattern | Database |
|--------|-------|-------------|----------|
| Local dev | Node.js + tsx | `localhost:3000` | SQLite (file) |
| Docker (self-hosted) | Docker Compose | `localhost:3000` | SQLite (volume-mounted) |
| Fly.io (production) | Fly.io + Dockerfile | `*.fly.dev` | SQLite (persistent volume) |

## Pre-Deployment Checklist

1. All tests passing: `npm test`
2. TypeScript compiles cleanly: `npm run build`
3. Database migrations current: `npm run migrate`
4. Environment variables set (see `docs/DEPLOYMENT.md` for full list):
   - `OPENAI_API_KEY` (required for embeddings)
   - `ANTHROPIC_API_KEY` (required for Phase 3 intelligence)
   - `DATABASE_PATH` (production path)
   - `NODE_ENV=production`
5. No uncommitted changes in working tree

## Deployment Sequence

### Local Development

```bash
npm install
npm run prepare-db
npm run dev          # tsx with hot reload
```

### Docker (Self-Hosted)

```bash
docker compose build
docker compose up -d
docker compose logs -f knowledge-base
```

Verify health:
```bash
curl http://localhost:3000/api/health
```

### Fly.io (Production)

```bash
fly deploy --strategy rolling
fly status
fly logs
```

#### Persistent Volume

The SQLite database requires a persistent volume:
```bash
fly volumes create knowledge_data --region ewr --size 1
```

Mount in `fly.toml`:
```toml
[mounts]
  source = "knowledge_data"
  destination = "/data"
```

## Post-Deployment Verification

1. **Health endpoint:** `GET /api/health` returns `200`
2. **Search functionality:** `GET /api/search?q=test` returns results
3. **Database connectivity:** `GET /api/stats` returns unit counts
4. **Embedding service:** Verify ChromaDB connection if using external vector DB

## Rollback Procedure

### Fly.io
```bash
fly releases
fly deploy --image <previous-image-ref>
```

### Docker
```bash
docker compose down
docker compose up -d --build  # with previous commit checked out
```

## Database Backup Before Deploy

Always back up before production deploys:
```bash
npm run backup
# Creates timestamped backup in ./backups/
```

## Monitoring

- Fly.io metrics: `fly dashboard`
- Application logs: `fly logs --app my-knowledge-base`
- Database size: `GET /api/stats` includes storage metrics

## Related Documents

- `docs/DEPLOYMENT.md` -- Environment variables and Docker configuration
- `docs/ARCHITECTURE.md` -- System design and data flow
- `fly.toml` -- Fly.io deployment configuration
- `docker-compose.yml` -- Docker Compose service definitions
- `Dockerfile` -- Container build specification
