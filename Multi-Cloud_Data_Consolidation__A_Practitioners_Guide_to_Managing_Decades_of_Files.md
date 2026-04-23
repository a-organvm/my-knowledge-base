# Multi-Cloud Data Consolidation: A Practitioner's Guide to Managing Decades of Files

**Atom ID:** multi-cloud-data-consolidation
**Status:** ACTIVE
**References:** 3 cross-references in knowledge base corpus

---

## Abstract

This guide documents the operational reality of consolidating personal data scattered across multiple cloud platforms, external drives, and local filesystems accumulated over 15+ years. It is not a theoretical framework -- it is a practitioner's account of what works, what fails, and what the knowledge base system reveals about data lifecycle management when applied to one's own digital corpus.

## The Problem of Accumulated Data

### Scale

A typical power user accumulates data across:

| Platform | Typical Volume | Export Difficulty | Format |
|----------|---------------|-------------------|--------|
| Google Drive | 50-200 GB | Medium (Takeout) | Mixed |
| Dropbox | 20-100 GB | Easy (local sync) | Mixed |
| iCloud Drive | 10-50 GB | Hard (no bulk export) | Mixed |
| External HDDs | 200-2000 GB | Easy (mount + copy) | Mixed |
| Email archives | 5-20 GB | Medium (MBOX/EML) | Structured |
| AI conversations | 1-5 GB | Hard (platform-specific) | Unstructured |

### The Three Failures of Multi-Cloud Storage

1. **Duplication without deduplication.** The same file exists in Dropbox, Google Drive, and an external backup. No platform knows about the others. Storage cost scales linearly with redundancy.

2. **Organization drift.** A folder structure that made sense in 2015 is incomprehensible in 2026. Category boundaries shift, naming conventions evolve, and abandoned projects leave orphaned directories.

3. **Format obsolescence.** Files in proprietary formats (.pages, .sketch, .key) become inaccessible as software subscriptions lapse. Open formats survive; proprietary formats decay.

## Consolidation Strategy

### Phase 1: Inventory

Before moving any files, build a complete inventory:

```bash
# Generate file manifest with checksums for deduplication
find /Volumes/backup-drive -type f -exec sha256sum {} \; > manifest-backup.txt
find ~/Dropbox -type f -exec sha256sum {} \; > manifest-dropbox.txt
find ~/Library/Mobile\ Documents -type f -exec sha256sum {} \; > manifest-icloud.txt
```

### Phase 2: Deduplication

Identify duplicates by checksum:

```bash
# Find duplicates across manifests
cat manifest-*.txt | sort | uniq -d -w 64
```

### Phase 3: Classification

Apply the knowledge base's atomization categories to file classification:

| Category | File Types | Action |
|----------|-----------|--------|
| Active projects | Source code, current docs | Consolidate to ~/Workspace/ |
| Reference material | PDFs, bookmarks, notes | Ingest into knowledge base |
| Media archives | Photos, video, audio | Consolidate to external SSD |
| Legacy data | Old projects, archives | Archive to cold storage |
| Disposable | Caches, temp files, duplicates | Delete |

### Phase 4: Ingestion

Feed classified reference material into the knowledge base:

```bash
# Ingest local markdown and text files
npm run ingest:local -- --path ~/consolidated/reference/

# Process PDFs
npm run ingest:local -- --path ~/consolidated/pdfs/ --format pdf
```

### Phase 5: Ongoing Maintenance

- **Dropbox recovery:** Document and track recovery of files lost during sync conflicts (see `TODO_dropbox_recovery.md`)
- **iCloud sync monitoring:** iCloud folder sync has known issues with runaway conflict loops requiring Apple server-side reset
- **Automated sorting:** Use `domus sort` for ongoing file organization based on naming conventions

## Tools and Infrastructure

| Tool | Purpose | Status |
|------|---------|--------|
| My Knowledge Base | Atomize reference material | Active |
| chezmoi | Manage dotfiles and tool config | Active |
| Backblaze | Continuous backup | Active |
| Time Machine | Local versioned backup | Active (needs SSD conversion) |
| Dropbox | Cloud sync | Active (recovery ongoing) |

## Lessons Learned

1. **Export everything immediately.** Cloud platforms can change export APIs, shut down, or lock accounts at any time. Export is not a future task -- it is a present emergency.

2. **Checksums over filenames.** Two files with the same name may differ. Two files with different names may be identical. Only checksums tell the truth.

3. **Local-first, cloud-synced.** The authoritative copy lives on your machine. Cloud platforms are replicas, not sources of truth.

4. **Automate the sort, not the decision.** Automated classification handles 80% of files correctly. The remaining 20% requires human judgment. Design the system to surface the 20%, not to force-classify them.

## Related Documents

- `TODO_dropbox_recovery.md` -- Dropbox file recovery tracking
- `HARDWARE.md` -- Storage requirements for consolidated corpus
- `07_DEPLOYMENT_GUIDE.md` -- Deployment configuration for the knowledge base
