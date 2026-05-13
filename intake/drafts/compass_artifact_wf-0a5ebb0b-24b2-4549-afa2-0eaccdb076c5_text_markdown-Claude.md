# Bulletproof automated multimedia creative system architecture

**Theory grounds expression; expression informs theory; automation amplifies without intervention.** This architectural specification presents a complete, GitHub-native system where seven "organs" operate in harmonic parallelism—each with distinct cadence, function, and form—while a central registry maintains coherence. The system draws on epistemological frameworks from creative institutions (Bauhaus, MIT Media Lab), ontological models from information science (SKOS polyhierarchy, faceted classification), and automation patterns from modern DevOps to create infrastructure that "plays like chords."

---

## The epistemological foundation: why this ordering works

The hierarchy **Theory → Art/Commerce/Public Process → Community/Marketing** reflects how knowledge actually flows in creative practice. The Bauhaus model established this empirically: foundational theory (Vorkurs) precedes and enables parallel workshop expressions, which ultimately converge in building (Bau). Christopher Frayling's taxonomy—research *into*, *through*, and *for* art—confirms that practice and theory form a bidirectional loop, not a one-way transmission. MIT Media Lab's "antidisciplinary" approach (Joi Ito, 2014) further demonstrates that the most generative work emerges from the "white space between disciplines" rather than within them.

**The key insight from practice-based research**: onto-epistemology describes a state where *being*, *doing*, and *knowing* are inseparable (Robin Nelson, 2022). Theory isn't merely applied to practice; practice generates theory. This justifies the parallel organ structure—Art, Commerce, and Public Process don't wait for Theory to finish; they inform it continuously. The amplification organs (Community, Marketing) then mechanically extend what emerges from this generative interplay.

Musical counterpoint provides the governing metaphor: voices that are "harmonically dependent yet independent in rhythm and melodic contour." Each organ maintains its own temporal logic while contributing to an emergent polyphonic whole. Deleuze and Guattari's rhizome extends this—any point can connect to any other, the system can break and reconstitute on new lines, and multiplicity replaces strict hierarchy.

### The seven-organ model with temporal logic

| Organ | Function | Cadence | Form |
|-------|----------|---------|------|
| **I. Theory** | Foundational knowledge, frameworks, epistemology | Slow, irregular (months to years) | Dense writing, diagrams, proofs |
| **II. Art** | Aesthetic expression, creative works | Project-driven, irregular | Multimedia artifacts |
| **III. Commerce** | Client work, products, revenue generation | Deadline-driven, external constraints | Deliverables, contracts |
| **IV. Public Process** | Building in public, process artifacts | Rhythmic, sparse (weekly/monthly) | Changelogs, working notes |
| **V. Community** | Discussion, membership, relationships | Human-paced, responsive | Forums, Discord, gatherings |
| **VI. Marketing** | Mechanical amplification, syndication | Automated, frequent | Social posts, newsletters |
| **VII. Archive** | Preservation, immutable records | Event-driven (on completion) | Frozen versions, DOIs |

---

## GitHub organization architecture

A single GitHub organization maximizes collaboration while using team-based access control and semantic naming for governance. Creating multiple organizations introduces friction; instead, repository naming encodes organ membership directly.

### Repository naming convention

**Pattern**: `{organ}--{project-or-function}--{qualifier}`

Double-hyphens separate semantic units for machine parseability while remaining human-readable:

```
theory--epistemology-of-practice--notes
art--album-synthesis-2026--source  
commerce--client-acme--campaign-q1
public--changelog--feed
community--discord-bot--sync
marketing--social-dispatch--automated
archive--project-alpha--v1-frozen
orchestration--start-here               ← Central registry (no qualifier needed)
```

The `orchestration--start-here` repo serves as the **single source of truth**—a registry that maps all repositories, their relationships, dependencies, and cross-organ linkages.

### Organ prefixes with immutable semantics

| Prefix | Immutable Location Rule |
|--------|------------------------|
| `theory--` | Content evolves but repo location never changes |
| `art--` | Work published here remains here; new versions = new repos or tags |
| `commerce--` | Client repos archived in-place when completed |
| `public--` | Process documentation accumulates; nothing deleted |
| `community--` | Infrastructure repos persist; discussion in GitHub Discussions |
| `marketing--` | Automation repos; content flows through, nothing stored |
| `archive--` | Frozen snapshots; protected branches; no modifications |

### Directory structure within repositories

Adapting the PARA method (Projects, Areas, Resources, Archive) with Johnny.Decimal numbering:

```
any-repo/
├── README.md                    # Self-documenting entry point
├── .meta/                       # System configuration
│   ├── registry.json            # Relationships to other repos
│   ├── schema.json              # Metadata schema for this repo
│   └── hooks/                   # Git hooks for validation
│
├── 00-inbox/                    # Unsorted incoming (staging)
├── 10-source/                   # Primary working material
├── 20-process/                  # Work-in-progress documentation
├── 30-output/                   # Completed artifacts
├── 40-exports/                  # Deliverable formats
└── 90-archive/                  # Historical versions (never deleted)
```

### Metadata frontmatter standard

Every significant file includes YAML frontmatter combining Dublin Core elements with organ-specific fields:

```yaml
---
title: "Project Alpha Composition"
id: "art--album-synthesis-2026--source/10-source/track-03"
type: audio                        # audio | visual | document | code
status: draft                      # inbox | draft | review | approved | final | archived
organ: [art, public]               # Multi-organ participation
created: 2026-01-15
modified: 2026-02-03
version: "0.3"
creator: "Studio Name"
related:
  - "theory--composition-framework--notes"
  - "public--changelog--feed"
cadence: project                   # slow | deadline | rhythmic | human | mechanical
---
```

---

## The central registry: orchestration--start-here

This repository is the **canonical index** of all repositories, their relationships, and cross-organ linkages. It auto-generates from repository metadata via GitHub Actions, ensuring the registry reflects reality without manual maintenance.

### Registry schema (registry.json)

```json
{
  "$schema": "creative-system-registry-v1",
  "generated": "2026-02-03T14:00:00Z",
  "organs": {
    "theory": {
      "repos": [
        {
          "name": "theory--epistemology-of-practice--notes",
          "status": "active",
          "cadence": "slow",
          "feeds": ["art--album-synthesis-2026--source"],
          "fed-by": ["public--changelog--feed"]
        }
      ]
    },
    "art": { "repos": [...] },
    "commerce": { "repos": [...] },
    "public": { "repos": [...] },
    "community": { "repos": [...] },
    "marketing": { "repos": [...] },
    "archive": { "repos": [...] }
  },
  "cross-organ-works": [
    {
      "id": "project-alpha",
      "participates-in": ["art", "public", "commerce"],
      "canonical-repo": "art--project-alpha--source",
      "related-repos": [
        "commerce--project-alpha--client-deliverables",
        "public--project-alpha--process-log"
      ]
    }
  ],
  "dependency-graph": {
    "theory--composition-framework--notes": {
      "enables": ["art--album-synthesis-2026--source"]
    }
  }
}
```

### Auto-indexing workflow

The registry regenerates on any repository change across the organization:

```yaml
# .github/workflows/regenerate-registry.yml
name: Regenerate Registry
on:
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  repository_dispatch:
    types: [repo-updated]

jobs:
  index:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Fetch all org repos
        env:
          GH_TOKEN: ${{ secrets.ORG_ADMIN_TOKEN }}
        run: |
          gh api /orgs/${{ github.repository_owner }}/repos \
            --paginate --jq '.[] | {name, description, topics}' > repos.json
      
      - name: Parse metadata from each repo
        run: |
          node scripts/parse-repo-metadata.js repos.json > registry.json
      
      - name: Generate dependency graph
        run: node scripts/build-dependency-graph.js registry.json
      
      - name: Commit updated registry
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: regenerate registry [automated]"
          file_pattern: registry.json dependency-graph.json
```

---

## GitHub Actions automation stack

### Cross-repo orchestration pattern

When work in one organ should trigger actions in another:

```yaml
# In art--project-alpha--source: notify public process on release
name: Notify Public Process
on:
  release:
    types: [published]

jobs:
  dispatch:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger public changelog update
        run: |
          curl -X POST \
            -H "Authorization: token ${{ secrets.CROSS_REPO_TOKEN }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/${{ github.repository_owner }}/public--changelog--feed/dispatches \
            -d '{"event_type": "art-release", "client_payload": {"repo": "${{ github.repository }}", "version": "${{ github.event.release.tag_name }}", "notes": "${{ github.event.release.body }}"}}'
```

### Automated promotion workflow

Move work between states based on criteria (e.g., when a PR merges with `approved` label):

```yaml
name: Promote to Archive
on:
  pull_request:
    types: [closed]
    branches: [main]

jobs:
  check-promotion:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check if ready for archive
        id: check
        run: |
          if grep -q "status: final" .meta/metadata.yml; then
            echo "promote=true" >> $GITHUB_OUTPUT
          fi
      
      - name: Create archive tag
        if: steps.check.outputs.promote == 'true'
        run: |
          VERSION=$(grep "version:" .meta/metadata.yml | cut -d'"' -f2)
          git tag -a "archive-v${VERSION}" -m "Archived version ${VERSION}"
          git push origin "archive-v${VERSION}"
      
      - name: Trigger archive creation
        if: steps.check.outputs.promote == 'true'
        run: |
          curl -X POST \
            -H "Authorization: token ${{ secrets.CROSS_REPO_TOKEN }}" \
            https://api.github.com/repos/${{ github.repository_owner }}/archive--$(basename ${{ github.repository }})--frozen/dispatches \
            -d '{"event_type": "create-archive-snapshot"}'
```

### Semantic release with conventional commits

```yaml
name: Semantic Release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Semantic Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: npx semantic-release
```

With `.releaserc.yml`:
```yaml
branches: [main]
plugins:
  - "@semantic-release/commit-analyzer"
  - "@semantic-release/release-notes-generator"
  - "@semantic-release/changelog"
  - "@semantic-release/github"
  - "@semantic-release/git"
```

---

## Multi-organ participation: how work exists in multiple places

The system uses **polyhierarchical references** (from SKOS/semantic web principles) rather than duplication. A single canonical repo exists; other organs reference it through the registry.

### Pattern: canonical repo + federated references

```
art--project-alpha--source          ← Canonical location (immutable)
    │
    ├── referenced by: commerce--project-alpha--client-deliverables
    │       └── .meta/registry.json: { "canonical": "art--project-alpha--source" }
    │
    ├── referenced by: public--project-alpha--process-log
    │       └── .meta/registry.json: { "canonical": "art--project-alpha--source" }
    │
    └── surfaced to: marketing--social-dispatch--automated
            └── GitHub Action watches releases, dispatches to social
```

### Git subtrees for shared assets

When actual files must appear in multiple repos (e.g., brand assets):

```bash
# In consuming repo, add shared assets as subtree
git remote add shared-assets git@github.com:org/shared--brand-assets.git
git subtree add --prefix=assets/brand shared-assets main --squash

# Update when upstream changes
git subtree pull --prefix=assets/brand shared-assets main --squash
```

### Cross-repo issue linking

GitHub's native cross-repo references maintain bidirectional awareness:
```
See also: org/theory--epistemology-of-practice--notes#15
Implements: org/art--album-synthesis-2026--source#42
```

Organization-level GitHub Projects aggregate issues across repos for unified views.

---

## Organ V, VI, VII automation: public process, community, marketing

### Organ V: Public Process (building in public)

**Stack**: Hugo or Eleventy + GitHub Pages + RSS

```yaml
# .github/workflows/publish-public.yml
name: Publish to Public
on:
  push:
    branches: [main]
    paths: ['20-process/**', '30-output/**']
  release:
    types: [published]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
      
      - name: Build
        run: hugo --minify
      
      - name: Deploy to Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

**Automatic changelog from commits** using git-cliff:
```yaml
- name: Generate changelog
  uses: orhun/git-cliff-action@v2
  with:
    config: cliff.toml
    args: --verbose
  env:
    OUTPUT: CHANGELOG.md
```

### Organ VI: Community automation

**Discord-GitHub integration** (append `/github` to Discord webhook URL):
```yaml
- name: Discord notification
  run: |
    curl -H "Content-Type: application/json" \
      -d '{"content": "🎉 New release: ${{ github.event.release.name }}"}' \
      "${{ secrets.DISCORD_WEBHOOK_URL }}"
```

**Membership gating with GitHub Sponsors**:
- Attach private repos to sponsorship tiers (native GitHub feature)
- Auto-managed access—GitHub handles invites/revocations
- Sponsors-only content delivery without custom infrastructure

**Patreon integration via n8n or Pipedream**:
- Webhook fires on `members:pledge:create`
- Automation adds user to GitHub org team
- Welcome email via Buttondown/ConvertKit

### Organ VII: Marketing automation (zero-touch POSSE)

**POSSE = Publish (on your) Own Site, Syndicate Elsewhere**

```yaml
# .github/workflows/social-dispatch.yml
name: Social Dispatch
on:
  release:
    types: [published]

jobs:
  syndicate:
    runs-on: ubuntu-latest
    steps:
      - name: Post to Mastodon
        uses: cbrgm/mastodon-github-action@v2
        with:
          url: ${{ secrets.MASTODON_URL }}
          access-token: ${{ secrets.MASTODON_TOKEN }}
          message: |
            🚀 ${{ github.event.release.name }}
            ${{ github.event.release.html_url }}
      
      - name: Queue newsletter item
        run: |
          curl -X POST https://api.buttondown.email/v1/emails \
            -H "Authorization: Token ${{ secrets.BUTTONDOWN_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{"subject": "New: ${{ github.event.release.name }}", "body": "${{ github.event.release.body }}", "status": "draft"}'
```

**Buttondown RSS-to-email** for automated newsletters:
- Connect RSS feed from public site
- Cadence options: per-item, daily digest, weekly digest
- Creates drafts for review or auto-sends

**Complete syndication flow**:
```
Git Commit → GitHub Actions → Build Site + RSS
                                    ↓
                            Buttondown (email)
                                    ↓
                            Mastodon/Twitter
                                    ↓
                            Discord webhook
```

---

## Immutable reference architecture

### Content-addressed storage pattern

Every published artifact receives a content-addressed identifier:

```
Mutable Reference    →    Resolution Layer    →    Immutable Content
─────────────────────────────────────────────────────────────────────
"latest"             →    Registry lookup     →    sha256:abc123...
"v1.0"               →    Tag resolution      →    sha256:def456...
"project-alpha"      →    Concept DOI         →    All versions
```

### DOI integration via Zenodo

For works requiring external citation:

1. Connect GitHub repo to Zenodo (one-time setup)
2. Create GitHub Release
3. Zenodo automatically archives and mints DOI
4. **Concept DOI** points to all versions; **Version DOI** points to specific release

```yaml
- name: Create Zenodo release
  if: startsWith(github.ref, 'refs/tags/v')
  run: |
    # Zenodo GitHub integration handles this automatically
    # Just ensure .zenodo.json exists with metadata
```

### Immutable location guarantee

The naming convention encodes immutability:
- `archive--project-alpha--v1-frozen` cannot be renamed
- Branch protection rules prevent force-push
- Git tags mark permanent snapshots
- DOIs provide external immutable references

### Reference syntax for internal linking

```
creative://theory/epistemology-of-practice/notes               # Concept (all versions)
creative://theory/epistemology-of-practice/notes@v2.0          # Specific version
creative://theory/epistemology-of-practice/notes@sha256:abc    # Exact content
```

Registry resolves these to actual GitHub URLs or content hashes.

---

## Design patterns for parallelism: playing like chords

### Harmonic constraint: the registry as tonic

Just as Western harmony revolves around a tonic chord that provides gravitational center, `orchestration--start-here` serves as the tonal center. All organs reference it; it references all organs. Work can move freely but always maintains relationship to the registry.

### Temporal cadence management

Each organ operates on its own schedule, managed through GitHub Actions cron:

```yaml
# Theory: slow, quarterly review
- cron: '0 9 1 */3 *'  # 9am on 1st of every quarter

# Public Process: weekly rhythm
- cron: '0 10 * * 1'   # 10am every Monday

# Marketing: multiple times daily
- cron: '0 */4 * * *'  # Every 4 hours
```

**Cadence-aware automation**: workflows check current date against expected cadence before executing, preventing mechanical organs from overwhelming human-paced ones.

### Counterpoint pattern: independent voices, harmonic whole

Three principles from musical counterpoint applied to organ design:

1. **Melodic independence**: Each organ has its own content logic (Art makes art, Commerce serves clients, Theory develops frameworks)
2. **Harmonic interdependence**: All organs contribute to coherent whole via registry relationships
3. **Rhythmic variety**: Different cadences prevent monotony and create productive tension

### The weaving metaphor: warp and weft

- **Theory = warp** (vertical threads, fixed framework, provides structure)
- **Art/Commerce/Public = weft** (horizontal threads, pass through structure, create pattern)
- **Community/Marketing = selvage** (edge binding, finishes the fabric, prevents unraveling)

---

## Tool recommendations summary

| Organ | Primary Tools | Automation |
|-------|---------------|------------|
| **Theory** | Obsidian, LaTeX, Markdown | Quartz for publishing |
| **Art** | DAW, Adobe CC, Blender | semantic-release |
| **Commerce** | Project files, contracts | Deadline-triggered workflows |
| **Public** | Hugo/Eleventy + GitHub Pages | RSS, git-cliff |
| **Community** | GitHub Discussions, Discord | Webhooks, bots |
| **Marketing** | Buttondown, Mastodon | POSSE automation |
| **Archive** | Zenodo, frozen branches | DOI minting |
| **Registry** | JSON + GitHub Actions | Auto-indexing |

---

## Implementation sequence

**Week 1**: Establish naming conventions and create `orchestration--start-here` with initial registry schema. Set up reusable workflows in `.github` repository.

**Week 2**: Create one repo per organ with proper naming. Configure branch protection and semantic-release. Test cross-repo dispatch.

**Week 3**: Deploy public site (Hugo/Eleventy). Configure RSS feeds. Connect Buttondown for newsletter automation. Set up Discord webhooks.

**Week 4**: Connect Zenodo for DOI minting. Implement full POSSE pipeline. Document system in registry README.

The system then runs itself. New repos trigger registry regeneration. Releases cascade to public→community→marketing. Archives mint DOIs. The orchestration plays like chords—parallel voices, independent cadences, harmonic whole.