# TODO: Dropbox Recovery

**Atom ID:** dropbox-recovery-todo
**Status:** IN PROGRESS
**References:** 3 cross-references in knowledge base corpus
**Source:** LINKEDIN_001_20251229_060752

---

## Overview

Dropbox sync has experienced data loss and conflict loops requiring systematic recovery. This document tracks the recovery effort, prioritizing files by irreplaceability.

## Recovery Status

| Category | Estimated Files | Recovered | Remaining | Priority |
|----------|----------------|-----------|-----------|----------|
| Documents (unique) | ~500 | TBD | TBD | P0 |
| Source code (backed up elsewhere) | ~2,000 | N/A | N/A | P2 (skip -- git is source) |
| Media (photos, video) | ~5,000 | TBD | TBD | P1 |
| Configuration files | ~200 | N/A | N/A | P2 (skip -- chezmoi is source) |

## Recovery Procedures

### Step 1: Identify Missing Files

Compare local Dropbox directory against Dropbox web interface:

```bash
# List local files
find ~/Dropbox -type f | sort > dropbox-local.txt

# Compare against web listing (manual or API)
# Identify files present on web but missing locally
```

### Step 2: Check Version History

Dropbox retains version history for 30-180 days depending on plan:

1. Log into dropbox.com
2. Navigate to affected directories
3. Click "Version history" on each file
4. Restore previous versions where available

### Step 3: Check Conflicted Copies

Dropbox creates "conflicted copy" files during sync failures:

```bash
# Find all conflicted copies
find ~/Dropbox -name "*conflicted*" -type f
```

Decision for each conflicted copy:
- If original exists and is current: delete conflicted copy
- If original is missing: rename conflicted copy to replace original
- If both differ: diff and merge manually

### Step 4: Cross-Reference with Backblaze

Backblaze continuous backup retains file history. For files missing from both local and Dropbox web:

1. Log into backblaze.com/b2
2. Search for filename
3. Restore from backup if available

### Step 5: Cross-Reference with Time Machine

For files that predate Backblaze setup:

```bash
# Browse Time Machine backups
tmutil listbackups
# Mount specific backup and search
```

## Known Issues

1. **iCloud folder sync conflict loop:** Separate from Dropbox, but related. iCloud has a runaway conflict loop that requires Apple server-side reset. Do not attempt to fix locally.

2. **Dropbox selective sync gaps:** Some folders may have been deselected from sync in the past, causing them to exist only on the web or only on a previous machine.

3. **Dropbox-to-chezmoi migration:** Configuration files previously stored in Dropbox have been migrated to chezmoi. These are not recovery targets -- chezmoi is the authoritative source.

## Acceptance Criteria

Recovery is complete when:
- [ ] All unique documents accounted for (recovered or confirmed lost)
- [ ] All recoverable media files restored
- [ ] All conflicted copies resolved
- [ ] Dropbox sync confirmed healthy (no ongoing conflicts)
- [ ] Recovery manifest committed to this repo

## Related Documents

- `Multi-Cloud_Data_Consolidation__A_Practitioners_Guide_to_Managing_Decades_of_Files.md` -- Broader consolidation strategy
- `HARDWARE.md` -- Storage requirements
