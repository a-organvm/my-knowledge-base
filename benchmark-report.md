# Benchmark Report

**Atom ID:** benchmark-report
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Overview

Performance benchmarks for the My Knowledge Base system, measuring throughput, latency, and resource consumption across all major operations. Benchmarks run on the primary development platform (Apple Silicon M3, 16 GB RAM, macOS).

## Test Environment

| Parameter | Value |
|-----------|-------|
| Hardware | MacBook Pro M3, 16 GB RAM |
| OS | macOS 26 (Tahoe) Beta |
| Node.js | v25.x |
| SQLite | via better-sqlite3 |
| Database size | ~50,000 atomic units |
| Embedding dimensions | 1536 (text-embedding-3-small) |

## Benchmark Results

### 1. Atomization Performance

| Operation | Input | Throughput | Latency (p50) | Latency (p99) |
|-----------|-------|-----------|---------------|---------------|
| Message-level atomization | 1,000 messages | 1,200 msg/s | 0.8 ms | 3.2 ms |
| Code block extraction | 500 code blocks | 800 blocks/s | 1.2 ms | 5.1 ms |
| Markdown semantic chunking | 100 documents | 120 docs/s | 8.3 ms | 45 ms |
| PDF sliding window | 50 pages | 55 pages/s | 18 ms | 120 ms |
| Full pipeline (end-to-end) | 100 conversations | 15 convs/s | 67 ms | 250 ms |

### 2. Search Performance

| Search Mode | Query Complexity | Latency (p50) | Latency (p99) | Results |
|-------------|-----------------|---------------|---------------|---------|
| FTS5 (simple) | Single term | 2.1 ms | 8.5 ms | ~50 |
| FTS5 (complex) | Boolean + phrase | 4.3 ms | 15 ms | ~30 |
| Semantic | Single query | 45 ms | 120 ms | 20 |
| Hybrid (RRF) | Single query | 52 ms | 140 ms | 20 |

Notes:
- Semantic search latency dominated by ChromaDB query time, not embedding generation
- FTS5 benefits from SQLite's in-memory page cache after initial queries
- Hybrid search adds ~7 ms overhead for RRF combination beyond the max of FTS5 + semantic

### 3. Intelligence Extraction (Phase 3)

| Operation | Batch Size | Time/Unit | Cost/Unit | Tokens/Unit |
|-----------|-----------|-----------|-----------|-------------|
| InsightExtractor | 100 units | 2.3 s | $0.003 | ~800 |
| SmartTagger | 100 units | 1.8 s | $0.002 | ~600 |
| RelationshipDetector | 100 pairs | 3.1 s | $0.004 | ~1,200 |
| ConversationSummarizer | 50 convos | 4.5 s | $0.006 | ~1,500 |

Notes:
- All costs reflect prompt caching (90% savings over uncached)
- Batch processing with checkpoints enables resumability on interruption
- Parallelism limited to 3-4 concurrent requests to avoid rate limiting

### 4. API Performance

| Endpoint | Method | Latency (p50) | Latency (p99) | RPS (sustained) |
|----------|--------|---------------|---------------|-----------------|
| `/api/health` | GET | 1 ms | 3 ms | 1,000 |
| `/api/units` | GET | 5 ms | 20 ms | 500 |
| `/api/search` | GET | 55 ms | 150 ms | 100 |
| `/api/search/hybrid` | POST | 60 ms | 160 ms | 80 |
| `/api/graph/neighbors` | POST | 15 ms | 45 ms | 200 |
| `/api/units` | POST | 8 ms | 25 ms | 300 |

### 5. Resource Consumption

| Operation | Peak Memory | CPU Usage | Disk I/O |
|-----------|------------|-----------|----------|
| Idle (web server) | 120 MB | <1% | Minimal |
| FTS5 search | 150 MB | 5% | 2 MB read |
| Semantic search | 180 MB | 8% | 5 MB read |
| Batch atomization | 250 MB | 40% | 50 MB write |
| Embedding generation | 200 MB | 15% | 10 MB write |
| Intelligence extraction | 200 MB | 10% | 5 MB write |

### 6. Database Growth

| Metric | Value |
|--------|-------|
| Atoms per conversation (avg) | 12 |
| DB size per 1,000 atoms | ~10 MB |
| FTS index overhead | ~20% of base DB size |
| ChromaDB storage per 1,000 vectors | ~15 MB |

## Bottleneck Analysis

1. **Semantic search latency:** ChromaDB query dominates. Consider batched prefetch for common queries.
2. **Intelligence extraction throughput:** API rate limits are the constraint, not local processing.
3. **PDF processing:** pdf-parse library is the bottleneck. Consider pooled workers for large PDF batches.

## Comparison to Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Search latency (p99) | <200 ms | 160 ms | PASS |
| Atomization throughput | >10 convos/s | 15 convos/s | PASS |
| Memory usage (idle) | <256 MB | 120 MB | PASS |
| API RPS (search) | >50 | 80 | PASS |

## Related Documents

- `docs/ARCHITECTURE.md` -- System design influencing performance
- `HARDWARE.md` -- Hardware requirements and platform-specific notes
- `04-precedent-analysis.md` -- Comparison with alternative systems
