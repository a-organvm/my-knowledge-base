---
name: Domain architecture — concentric circles
description: 6 domains across 3 circles (handle/name/system) on Cloudflare, with env vars in chezmoi and SOP in praxis-perpetua
type: project
---

Domain strategy designed and SOP'd on 2026-04-16. Three concentric circles, all Cloudflare Registrar.

**Domains (all verified AVAILABLE as of 2026-04-16):**
- Handle: `4jp.dev` ($10.18/yr)
- Name: `anthonypadavano.com` ($10.46) + `anthonypadavano.dev` ($10.18 defensive)
- System: `organvm.dev` ($10.18) + `organvm.org` ($10.13) + `organvm.io` ($50 defensive)
- Total: $101.13/yr ($51.13 without .io)

**Why:** .dev over .io (HSTS, stable pricing, no geopolitical risk). Split .dev/.org for ORGANVM (making organs I-IV on .dev, speaking organs V-VII on .org).

**How to apply:** Env vars in chezmoi.toml (`domain_*` fields) → `dot_zshenv.tmpl` → `15-env.zsh` derived vars. 21+ DOMAIN_* vars available in every shell session. SOP at `meta-organvm/praxis-perpetua/standards/SOP--domain-architecture-and-dns.md`.

**Status:** Domains not yet purchased. Registration is Phase 1 of the SOP. All availability confirmed via Vercel domain checker + DNS probing.
