---
name: Rob Inbound Engine Architecture Spec
description: Architectural pivot from manual SDR (Instagram DMs/weed scraping) to automated organic inbound engine for Hokage Chess / BODI.
type: project
---
# Rob Bonavoglia: Inbound Engine Architecture Spec

**Date:** 2026-04-28
**Pivot:** Transitioning Rob from Manual SDR ("weed scraping") to Automated Inbound Engine

## 1. The Redteam Diagnosis
The previous architecture assumed the BODI "funnel" was a mature, scalable system that could be ported to Hokage Chess. The 2026-04-27 Redteam analysis exposed this as a critical error: the BODI "funnel" is actually a high-touch, 1-to-1 manual sales pipeline reliant on Rob sending Instagram DMs to cold leads. This creates a hard ceiling on scale dictated by Rob's waking hours.

## 2. The Architectural Pivot
We are abandoning the attempt to port the manual SDR process. Instead, we must build a true **Organic Inbound Engine** that replaces the Level 1 bottleneck across both brands.

### The New Funnel Flow
1. **Traffic Generation (Organic Inbound)**: SEO / YouTube / POSSE syndication. Rob's energy shifts from 1-to-1 DMs to 1-to-Many content creation.
2. **Landing Page (The Anchor)**: A dedicated, branded landing page replacing the fragile Google Form.
3. **Lead Magnet Delivery (Level 1 → Level 2 Transition)**: Automated email delivery (via Kit) of premium content (e.g., "Road to 1500" PDF guide, exclusive PGNs) upon email capture.
4. **CRM Integration**: Automated lead routing from Kit into Teamzy. Teamzy shifts from being a manual ledger of cold DMs to an intake receiver for warm, qualified leads.

## 3. Operational Requirements

### Infrastructure Needed
- **Landing Page Host**: Cloudflare Pages / Vercel (to host the static site).
- **Email Service Provider (ESP)**: Kit (formerly ConvertKit) API integration for the email capture form.
- **Lead Magnet Asset**: A high-value digital artifact ready for automated delivery.

### Rob's Role Shift
- **Stop**: Manually finding and DMing followers on Instagram.
- **Start**: Creating Bridge Content (PRT-040) designed to point viewers directly to the new Landing Page URL.
