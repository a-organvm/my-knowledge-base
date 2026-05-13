---
title: Lexicon and Style Guide
document_id: speech-score-engine_lexicon-and-style-guide_20260327
doc_type: architecture
doc_path: docs/architecture/lexicon-and-style-guide.md
status: canonical
authority_level: repo-wide
system_id: $SPEECH_SCORE_ENGINE
category: terminology-governance
updated_at: 2026-03-27
owners:
  - architecture
  - product
  - engineering
summary: >-
  Canonical lexicon, naming policy, and writing rules for the Speech-Score
  Composition System, covering ontology, UI aliases, forbidden drift terms,
  repository naming conventions, and documentation style.
---

# Lexicon and Style Guide

## 1. Purpose

This document defines the canonical language of the repository.

Its function is to keep the system legible as a **Speech-Score Composition System** rather than allowing it to drift into weaker or misleading categories such as script reader, voice utility, generic text-to-speech wrapper, podcast tool, or theatrical novelty app.

This document is normative.

Where terminology conflicts arise across product copy, schema, API contracts, UI labels, repository structure, implementation notes, or future design documents, this guide is the default source of resolution unless a higher-authority document explicitly supersedes it.

## 2. Governing Sentence

**The system treats language as a dual-aspect object: semantic content and timed performance.**

Every naming decision must preserve both sides of that claim.

If a proposed term obscures semantic content, reject it.
If a proposed term obscures temporal performance, reject it.
If a proposed term collapses the system into commodity voice infrastructure, reject it.

## 3. Scope

This guide applies to:

- `docs/architecture/`
- `docs/product/`
- ADRs and implementation handoff documents
- database schema names and migration commentary
- API route naming and contract descriptions
- internal domain types and service interfaces
- UI labels and product-copy decisions
- repository, folder, and file naming where domain meaning is implicated

This guide does **not** force user-facing UI language to become academic or overtechnical. It distinguishes between:

- **canonical internal terminology**, which must remain stable
- **user-surface aliases**, which may simplify the language for usability

## 4. Order of Authority

When terms conflict, use the following authority order:

1. This document’s **Governing Sentence**
2. Canonical system identity terms
3. Approved ontology terms
4. Alias mappings
5. Local UI simplifications

A local convenience term may exist in UI copy, but it must not silently replace canonical terminology in architecture, schema, API contracts, or deep implementation documents.

## 5. Canonical System Identity

| Layer | Canonical term | Status | Usage rule |
|---|---|---:|---|
| Master system name | Speech-Score Composition System | Approved | Use in external prose, architecture summaries, and category definition |
| Internal system identifier | `$SPEECH_SCORE_ENGINE` | Approved | Use in specifications, ontological discussions, and formal repo artifacts |
| Product-surface descriptor | Dramaturgical-Audio Workbench | Approved | Use for the commercially legible surface layer |
| Deep-system descriptor | Polyvocal Speech-Composition Engine | Approved | Use when distinguishing deeper compositional architecture from MVP surface |
| Secondary designation | Post-Script Theatrical Composition Environment | Permitted | Use in theoretical, manifesto, or research contexts |
| Compact category shorthand | speech-score system | Approved | Use when brevity is needed without ontological loss |

## 6. Canonical Lexicon

### 6.1 Primary Ontology Terms

| Canonical term | Definition | Usage domain |
|---|---|---|
| `$PHRASE_EVENT` | Primary compositional unit; a bounded utterance or fragment with semantic, temporal, and relational properties | domain model, architecture, notation, analysis |
| `$VOICE_CHANNEL` | Speaking carrier independent from literary character identity | rendering, analysis, execution, data model |
| `$TEMPORAL_RELATION` | Primary organizing principle governing cue order, overlap, delay, silence, recurrence, and entry logic | theory, architecture, diagnostics |
| `$TIMING_SUBSTRATE` | Temporal kernel supporting clock time, beat time, cue-relative time, and elastic time | architecture, implementation, services |
| `$COMPOSITION_LAYER` | Authoring layer for phrase-events, distribution rules, recurrence, transformation, and timing behavior | architecture, product design |
| `$PHRASE_EVENT_MODEL` | Canonical structured representation of utterance-level objects | storage, schema, parsing, contracts |
| `$ANALYSIS_ENGINE` | Diagnostic layer for timing, pacing, repetition, turn structure, interruption logic, and speaker differentiation | product diagnostics, analysis services |
| `$NOTATION_RENDERER` | Rendering layer that produces readable script, rhythmic score, spatial score, and performer part outputs | output architecture |
| `$REHEARSAL_KERNEL` | Bridge from composition objects to rehearsal artifacts such as cue sheets, stems, loop drills, and count structures | rehearsal tooling |
| `$LIVE_EXECUTION_LAYER` | Real-time performance coordination layer including control views, timing control, and override behavior | live infrastructure |

### 6.2 Output Terms

| Canonical term | Definition |
|---|---|
| `$READABLE_SCRIPT` | Literary-readable representation of the work |
| `$RHYTHMIC_SCORE` | Beat- or measure-oriented score representation |
| `$SPATIAL_TEXT_SCORE` | Layout-driven score where typography and spatial arrangement carry instruction |
| `$TABLE_READ_AUDIO` | Rapid auditory draft used for dramaturgical listening and revision |
| `$REHEARSAL_PACK` | Export bundle for rehearsal use |
| `$CONDUCTOR_VIEW` | Live control-oriented view |
| `$LIVE_PROMPT_VIEW` | Monitor-safe live prompt display |
| `$MACHINE_SCORE_OBJECT` | Structured machine-readable representation of the work |
| `$KINETIC_TEXT_RENDER` | Projection or motion-based visible text output |

### 6.3 Structural Scale Terms

| Canonical term | Definition |
|---|---|
| `$PHRASE_EVENT` | Smallest meaningful compositional unit |
| `$PASSAGE` | Grouping of phrase-events |
| `$MOVEMENT` | Grouping of passages |
| `$WORK` | Highest-level composed object |

## 7. Forbidden Terms

The following terms are rejected for canonical use because they misclassify, trivialize, or ontologically weaken the system.

| Forbidden term | Why it is rejected | Replacement |
|---|---|---|
| text-to-speech software | Collapses the system into commodity infrastructure | Speech-Score Composition System |
| TTS tool | Same collapse, weaker strategic framing | Dramaturgical-Audio Workbench |
| voice generator | Centers the wrong substrate | render service, voice profile layer, or `$TABLE_READ_AUDIO` |
| script reader | Treats the work as inert text | listening-first revision environment |
| podcast engine | Narrows the medium and excludes score/rehearsal/live layers | speech-score system |
| playwriting app | Too literary and too narrow | Dramaturgical-Audio Workbench |
| screenplay reader | Misframes the domain | dialogue revision environment |
| theatre chatbot | Category error | `$ANALYSIS_ENGINE` or dramaturgical diagnostics |
| audio toy | Trivializing, unserious, strategically weak | use canonical system or product term |
| playback settings | Too vague for core temporal architecture | `$TIMING_SUBSTRATE` |
| formatted script | Too weak for output architecture | `$NOTATION_RENDERER` output |
| practice mode | Understates the formal rehearsal function | `$REHEARSAL_KERNEL` |
| presentation mode | Understates live coordination logic | `$LIVE_EXECUTION_LAYER` |
| AI critique | Overclaims and weakens seriousness | `$ANALYSIS_ENGINE` |
| dialogue chunk | Loose, under-specified object language | `$PHRASE_EVENT` |
| clip | Imports DAW/video assumptions that distort ontology | `$PHRASE_EVENT` |
| thing / piece / block / snippet | Semantically weak and unstable | use exact canonical object term |

## 8. Alias Mappings

These aliases are allowed at the product surface for usability, but they must map back to canonical terms internally.

| User-surface term | Canonical internal term | Rule |
|---|---|---|
| scene | `$SCENE` as container, but ontologically subordinate to `$PHRASE_EVENT` and `$TEMPORAL_RELATION` | acceptable in UI and workflow docs |
| speaker | `$VOICE_CHANNEL` | acceptable in UI and onboarding |
| character | character-to-channel mapping or `$VOICE_CHANNEL` | use only when referring to literary source identity |
| line | `$PHRASE_EVENT` | acceptable for imported scripts and simple editing views |
| readback | `$TABLE_READ_AUDIO` or playback render | acceptable in product copy |
| dialogue playback | `$TABLE_READ_AUDIO` on surface, render flow over `$TIMING_SUBSTRATE` underneath | acceptable in product copy |
| script view | `$READABLE_SCRIPT` | prefer canonical term in architecture docs |
| score view | `$RHYTHMIC_SCORE` or `$SPATIAL_TEXT_SCORE` | use precise output name when known |
| voice | voice profile or `$VOICE_CHANNEL`, depending context | distinguish carrier from rendered voice |
| rehearsal export | `$REHEARSAL_PACK` | prefer canonical term in docs |
| live mode | `$LIVE_EXECUTION_LAYER` | UI shorthand only |
| diagnostics | `$ANALYSIS_ENGINE` output | UI-safe shorthand |

## 9. Approved Pattern Families

These naming families are preferred because they preserve the hybrid ontology of the project.

| Pattern family | Status | Notes |
|---|---:|---|
| speech-score | Approved | best high-level hybrid descriptor |
| polyvocal | Approved | best descriptor for distributed voice architecture |
| post-script | Approved | strong theoretical framing |
| dramaturgical-audio | Approved | best product-surface framing |
| performance-writing | Approved | good bridge term for general audiences |
| temporal writing intelligence | Approved | strong strategic positioning term |

## 10. Rejected Pattern Families

| Pattern family | Status | Notes |
|---|---:|---|
| AI voice | Rejected | centers commodity infrastructure |
| script reader | Rejected | literature-bound reduction |
| podcast engine | Rejected | medium narrowing |
| theatre chatbot | Rejected | category confusion |
| audio toy | Rejected | trivializing and unserious |

## 11. Naming Conventions by Layer

### 11.1 Repository and Document Layer

- Human-readable repo documents use **kebab-case** file names.
- Formal architecture and product documents should begin with a clear title and stable frontmatter.
- Use machine-sortable `document_id` values in the form:

```text
<domain-subject>_<artifact-class>_<YYYYMMDD>
```

Examples:

```text
speech-score-engine_lexicon-and-style-guide_20260327
audio-dramaturgical-studio_mvp-system-design-package_20260327
audio-dramaturgical-studio_repository-blueprint-and-handoff_20260327
```

### 11.2 System and Ontology Layer

- External category names use **Title Case**.
- Canonical internal entities use **`$UPPER_SNAKE_CASE`**.
- Avoid inventing parallel synonyms for core ontological objects.

Examples:

```text
Speech-Score Composition System
Dramaturgical-Audio Workbench
Polyvocal Speech-Composition Engine

$SPEECH_SCORE_ENGINE
$PHRASE_EVENT
$VOICE_CHANNEL
$TIMING_SUBSTRATE
$ANALYSIS_ENGINE
```

### 11.3 Database Layer

- Tables, columns, indexes, and SQL artifacts use **lowercase snake_case**.
- Do not prefix database identifiers with `$`.
- Prefer concrete relational nouns over abstract labels.

Examples:

```sql
app_user
scene
scene_version
version_line
playback_render
diagnostic_report
share_link
created_at
estimated_duration_ms
```

### 11.4 TypeScript and Application Layer

- Exported types, interfaces, classes, services, and React components use **PascalCase**.
- Internal fields and variables use **camelCase**.
- Service names should reflect domain behavior, not technical vagueness.

Examples:

```ts
ParseSceneResult
CreateSceneVersionInput
RenderDispatchService
VoiceProviderAdapter

sceneId
versionId
renderScope
estimatedDurationMs
```

### 11.5 API Layer

- Public routes use lowercase, plural resource nouns.
- Prefix routes with explicit versioning.
- Avoid leaking deep theoretical vocabulary into operational API paths unless the concept is public-facing.

Examples:

```text
/api/v1/projects
/api/v1/scenes/{scene_id}
/api/v1/versions/{version_id}/renders
/api/v1/versions/{version_id}/diagnostics/latest
```

### 11.6 Event Layer

- Domain events use **noun.action.state** in lowercase dot notation.
- Use stable names. Avoid renaming events casually after instrumentation begins.

Examples:

```text
scene.parse.requested
scene.parse.committed
version.created
render.completed
playback.started
diagnostic.viewed
share.revoked
```

### 11.7 Environment Configuration Layer

- Environment variables remain **`$UPPER_SNAKE_CASE`**.
- Environment-first configuration is mandatory.
- All required variables must be validated at process start.

Examples:

```bash
$DATABASE_URL
$REDIS_URL
$VOICE_PROVIDER_API_KEY
$APP_BASE_URL
$PUBLIC_SHARE_BASE_URL
$LOG_LEVEL
```

## 12. Writing Style by Artifact Type

### 12.1 Architecture Documents

Architecture documents must be:

- precise
- system-first
- non-promotional
- explicit about boundaries and invariants
- written in declarative language

Prefer:

- “The system shall…”
- “The canonical term is…”
- “This layer owns…”
- “Outside the system boundary…”

Avoid:

- hype language
- startup slogans inside technical docs
- anthropomorphic claims about system intelligence
- vague abstractions such as “magic,” “smart,” or “seamless” unless explicitly operationalized

### 12.2 Product Documents

Product documents should preserve strategic clarity without losing rigor.

Prefer:

- “listening-first revision environment”
- “dialogue as performed time”
- “diagnostic surface”
- “revision loop”

Avoid:

- “AI voices for writers” as the primary frame
- “instant script reader” as category language
- any copy that makes the voice layer sound like the moat

### 12.3 UI Copy

UI copy should be plain, calm, and operational.

Prefer:

- “New Scene”
- “Assign Speakers”
- “Playback”
- “Diagnostics”
- “Save Version”
- “Share Review Link”

Avoid:

- excessive theatrical metaphor in core workflows
- pseudo-poetic labels that obscure action
- overclaiming diagnostic labels such as “This scene fails”

Good diagnostic style:

- “Possible long monologue stretch”
- “Low speaker alternation in this section”
- “Repeated phrasing cluster detected”

### 12.4 Code Comments and Service Descriptions

Comments should describe:

- responsibility boundaries
- invariants
- failure conditions
- why a rule exists when non-obvious

Avoid comments that merely paraphrase the code.

## 13. Semantic Boundary Rules

The system must always be named from the inside out.

When referring to ontology, use composition language.
When referring to the commercial wedge, use listening-and-revision language.
When referring to infrastructure, use provider, render, storage, queue, and contract language.

Do not let infrastructure language replace ontology.

Therefore the following distinction must remain stable:

- The system is a **Speech-Score Composition System**.
- The product surface is a **Dramaturgical-Audio Workbench**.
- The voice layer is infrastructure.

## 14. Naming Tests

A proposed term is acceptable only if it passes all four tests.

| Test | Question | Pass condition |
|---|---|---|
| Dual-aspect test | Does the term preserve both meaning and timed performance? | must preserve both |
| Depth test | Does the term fit the deeper system, not only the MVP surface? | must scale upward |
| Non-commodification test | Does the term avoid collapsing the system into commodity voice tooling? | must avoid TTS-first framing |
| Translation test | Does the term remain valid across page, audio, rehearsal, and live execution? | must remain cross-medium valid |

## 15. Canonical Examples

### 15.1 Good System Summary

> `$SPEECH_SCORE_ENGINE` is a speech-score composition system for authoring, analyzing, rehearsing, rendering, and performing polyvocal works in which language functions simultaneously as meaning and as timed score.

### 15.2 Good Product Summary

> The product surface is a dramaturgical-audio workbench for hearing, inspecting, and revising dialogue before rehearsal.

### 15.3 Bad System Summary

> A TTS script tool for playwrights.

Reason: collapses ontology and moat into commodity infrastructure.

### 15.4 Bad Product Summary

> An AI voice generator for theatre people.

Reason: trivializes the product and centers the wrong layer.

## 16. Pull Request Review Checklist

A documentation, API, naming, or schema PR that touches domain language should be reviewed against the following checklist.

- Does the change preserve the governing sentence?
- Does it use an approved canonical term where one already exists?
- Does it avoid forbidden category drift terms?
- If it introduces a UI simplification, is the canonical mapping still clear internally?
- Does it preserve the distinction between ontology, product wedge, and infrastructure?
- Does it keep the system legible across page, audio, rehearsal, and live execution?

If any answer is no, revise before merge.

## 17. Final Rule

All repository, product, and documentation language must preserve the system’s identity as a speech-score composition system whose fundamental object is not inert text but structured temporal language.

Use adoption-friendly aliases at the surface where helpful.
Preserve canonical internal terms in schema, contracts, architecture, and code.
Do not name the system as a TTS tool, script reader, or voice generator.
