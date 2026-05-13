# UI Redesign Walkthrough — ORGANVM Ask Page

## What Changed

A comprehensive CSS design-system override was injected at the top of `ORGANVM_ Omniscience-Gauntlet_v2.html`. The HTML structure is **100% unchanged** — only the visual layer was reworked.

---

## Design Decisions

| Area | Before | After |
|---|---|---|
| **Font** | `system-ui` at flat `text-sm` everywhere | **Inter** (variable, 300–800) + **JetBrains Mono** for code/cites |
| **Color depth** | `#0a0a0a` / `#141414` flat surfaces | `#080c12` → `#0e1420` → `#1a2436` three-level surface hierarchy |
| **User bubble** | Harsh electric `#3b82f6` pill | Indigo→blue gradient `#2563eb → #4338ca`, softer shadow |
| **Assistant card** | Flat surface, tight padding | Glass card, `24px` horizontal / `20px` vertical padding, rounded asymmetrically |
| **Prose** | All flat `text-sm`, no heading styles | `h3` with bottom border, `h4` in uppercase small-caps, `1.75` line-height |
| **Tables** | Pipe-delimited raw text (CSS cannot fix static save) | CSS table styles ready; applies where real `<table>` elements exist |
| **Cite pills** | Monospace text inline | Pill chip with blue-tinted background + border |
| **FRESH badge** | Green text inline | Emerald pill badge, uppercase, letter-spaced |
| **Sources panel** | Dense, all same visual weight | Tiered hierarchy: panel → source card → cite + freshness row |
| **Feedback buttons** | Inline, low contrast | Pill buttons with hover fill; separated from answer by a divider |
| **Input** | Basic border box | Rounded pill input, focus glow ring, gradient Send button with lift-on-hover |
| **Nav** | Plain text links | Gradient wordmark (white→blue), active-state underline on "Ask", sticky + blur |
| **Provider errors** | Dumped inside answer prose | Visually dimmed via `:has(code):last-of-type` selector |

---

## Screenshots

````carousel
![Top viewport — nav and first Q&A pair](/Users/4jp/.gemini/antigravity/brain/9b4dbf29-9315-4110-82a9-eb6ae71e27a5/top_viewport_1772765017464.png)
<!-- slide -->
![Mid-chat — spacing, headings, citations panel](/Users/4jp/.gemini/antigravity/brain/9b4dbf29-9315-4110-82a9-eb6ae71e27a5/middle_chat_1772765028635.png)
<!-- slide -->
![Bottom — snapshot response and input bar](/Users/4jp/.gemini/antigravity/brain/9b4dbf29-9315-4110-82a9-eb6ae71e27a5/bottom_input_1772765037724.png)
````

---

## Known Limitation

Markdown **pipe tables** (e.g. `| Repo | Organ | ...`) in the saved HTML are stored as **raw text inside `<p>` tags**, not as actual `<table>` elements. This is because the file was saved via SingleFile from a Next.js app that renders markdown client-side. CSS table styles are defined and ready — they'll apply correctly in the **live Next.js app** where ReactMarkdown renders real `<table>` elements.

---

## Files Modified

- [`ORGANVM_ Omniscience-Gauntlet_v2.html`](file:///Users/4jp/Workspace/meta-organvm/stakeholder-portal/ORGANVM_%20Omniscience-Gauntlet_v2.html) — CSS override block injected (~590 lines)
