---
name: Email triage system — FAILED (LaunchAgent disabled)
description: FAILED 2026-04-21 — LaunchAgent froze machine every 30min, disabled at runtime. Classifier not affecting inbox. Gmail-side filter specs exist at /tmp/gmail-filters.gs. Needs Gmail Apps Script redesign.
type: project
originSessionId: caa53287-9125-4617-ae4f-43e9056d902d
---
**Status:** FAILED as of 2026-04-21. LaunchAgent `com.4jp.mail-triage` disabled via `launchctl bootout` (was freezing machine every 30min). Plist source unchanged in chezmoi.

**Architecture:** Python script (`~/.local/bin/mail-triage`) reads Mail.app via osascript, classifies by inline sender/subject/body heuristics, moves messages to **existing Gmail labels** (not Triage/*). Pure osascript — no IMAP, no app passwords.

**Routing (merged into existing taxonomy 2026-04-21):**
- NOISE/newsletter → `Marketing/Newsletter`
- NOISE/bulk-email → `Marketing`
- NOISE/github → `Notification` (Dev/GitHub has IMAP resolution issues)
- NOISE/ci → `Dev/Infrastructure`
- NOISE/social → `Social`
- NOISE/finance → `Finance/Banking`
- NOISE/commerce/shipping → `Shopping`
- NOISE/service → `Notification`
- NOISE/ats → `Professional/Jobs`
- ACTION/Today → `To Do`
- ACTION/This-Week → `To Respond`
- ACTION/Someday → `Daily Review`
- SPAM → `Marketing`
- HUMAN → stays in INBOX

**Test results:** 138 messages processed on 30-day backlog, 0 errors, 0 false HUMAN. 18 sender patterns added during session to close classification gaps.

**Location:** `domus-semper-palingenesis/dot_local/bin/executable_mail-triage` + `private_Library/LaunchAgents/com.4jp.mail-triage.plist.tmpl`

**Prerequisite:** Mail.app must be running. Script exits 1 cleanly if not accessible.

**Known tuning items:**
- OpenAI security updates misclassify as NOISE (sender pattern overrides subject "Action Required")
- Disney+ login alerts misclassify as ACTION (body keyword hits)
- Triage/* labels still exist in Gmail (empty, need manual deletion via Gmail web UI)

**Why:** Inbox shows only real people. Noise auto-routed to category labels, action items to workflow labels.

**How to apply:** Running. Tune sender patterns in `executable_mail-triage` as edge cases surface. BACKLOG-001 (burned Gmail app password) is independent — not needed by this implementation.
