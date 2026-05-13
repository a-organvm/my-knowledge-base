---
name: Time Machine SSD conversion plan
description: Deferred plan to reformat 4TB external SSD (4444-iivii) from exFAT to APFS for Time Machine + data volumes
type: project
---

Reformat 4TB external SSD (4444-iivii) from exFAT to dual APFS volumes.

**Current state (2026-03-25):**
- Drive: 4TB, exFAT, 1.1 TB used (31%), 2.5 TB free
- Clean organized structure: single `Data/` directory with 7 subdirectories
- iCloud-Recovery (214 GB), Development-Archive (174 GB), Rescued-From-Chaos (126 GB), Macbook-Offloads (39 GB), System-Backups (33 GB), Screen-Recordings (23 GB), Agents (256 MB)

**Target:**
- APFS container with two volumes sharing the 4 TB pool:
  - Volume 1: Time Machine backup
  - Volume 2: Data (moved back from staging)

**Blockers:**
- exFAT → APFS requires full erase (no in-place conversion)
- 1.1 TB of data needs staging (internal SSD only has ~128 GB free)
- Need either: a second external drive, or cloud upload/download cycle

**Steps when ready:**
1. Copy Data/ to staging location (second drive or cloud)
2. `diskutil eraseDisk APFS "4444-iivii" /dev/disk6`
3. `diskutil apfs addVolume disk6s1 APFS "TimeMachine"`
4. `diskutil apfs addVolume disk6s1 APFS "Data"`
5. Enable Time Machine: `sudo tmutil setdestination /Volumes/TimeMachine`
6. Copy Data/ back to /Volumes/Data/
7. Verify, then delete staging copy

**Why:** Time Machine requires APFS. APFS volumes share space dynamically — no fixed partition sizes needed.

**How to apply:** Execute when a staging drive is available or during a window where cloud upload of 1.1 TB is feasible.
