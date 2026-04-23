# Hardware Requirements and Compatibility

**Atom ID:** hardware-compatibility
**Status:** ACTIVE
**References:** 5 cross-references in knowledge base corpus

---

## Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| CPU | 2 cores | 4+ cores | Embedding generation is CPU-bound during batch ops |
| RAM | 4 GB | 8+ GB | SQLite + ChromaDB in-memory indices |
| Storage | 2 GB | 10+ GB | Database grows with corpus size |
| Node.js | v18 LTS | v20+ LTS | ESM module support required |

## Tested Platforms

| Platform | Architecture | Status | Notes |
|----------|-------------|--------|-------|
| macOS 15 (Sequoia) | ARM64 (Apple Silicon M1/M2/M3) | Verified | Primary development platform |
| macOS 26 (Tahoe) Beta | ARM64 (Apple Silicon M3) | Verified | Current development environment |
| macOS 14 (Sonoma) | Intel x86_64 | Compatible | Tested via CI |
| Ubuntu 22.04 LTS | x86_64 | Verified | Docker and Fly.io deployment target |
| Ubuntu 24.04 LTS | x86_64 | Compatible | CI runner environment |
| Debian 12 | x86_64 | Compatible | Docker base image |

## Architecture-Specific Notes

### Apple Silicon (ARM64)

- Native performance for all operations
- Homebrew installs to `/opt/homebrew/`
- Python via Anaconda at `/opt/anaconda3/`
- No Rosetta translation needed for any dependency

### Intel x86_64

- Full compatibility
- Homebrew installs to `/usr/local/`
- Slightly slower embedding generation vs. equivalent ARM64

## Storage Considerations

### Database Growth

| Corpus Size | SQLite DB | ChromaDB Vectors | Total |
|-------------|-----------|------------------|-------|
| 100 conversations | ~50 MB | ~100 MB | ~150 MB |
| 1,000 conversations | ~500 MB | ~1 GB | ~1.5 GB |
| 10,000 conversations | ~5 GB | ~10 GB | ~15 GB |

### Disk I/O

SQLite benefits from SSD storage. Mechanical drives introduce latency during:
- Full-text search queries (FTS5 index scans)
- Batch embedding generation (checkpoint writes)
- Database backup operations

## Memory Constraints

On memory-constrained systems (16 GB or less):

1. Limit parallel embedding generation: `--parallel 2` instead of default
2. Close unnecessary background processes during batch operations
3. Monitor with `npm run stats` to track database size

## Docker Resource Allocation

```yaml
# docker-compose.yml resource limits
services:
  knowledge-base:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

## Network Requirements

| Service | Direction | Port | Required |
|---------|-----------|------|----------|
| Web UI | Inbound | 3000 | Yes |
| OpenAI API | Outbound | 443 | For embeddings |
| Anthropic API | Outbound | 443 | For Phase 3 intelligence |
| ChromaDB | Outbound | 8000 | If external vector DB |

## GPU Acceleration

Not required. All embedding calls use the OpenAI API (remote compute). Local operations (atomization, FTS5 search, relationship detection) are CPU-only and do not benefit from GPU acceleration.

## Related Documents

- `docs/DEPLOYMENT.md` -- Deployment configuration
- `docker-compose.yml` -- Docker resource configuration
- `fly.toml` -- Fly.io machine sizing
