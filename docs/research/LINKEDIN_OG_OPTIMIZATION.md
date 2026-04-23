# Documentation: LinkedIn OG Preview Optimization

## Objective
Ensure that sharing the site URL on LinkedIn generates a professional, high-impact "First Impression" through optimized Open Graph (OG) tags.

## Core OG Tags
Add the following `<meta>` tags to the `<head>` section of your `index.html` (or the equivalent layout file in your Vite/React app):

```html
<!-- Primary Meta Tags -->
<title>Personal Knowledge Base | {OS.me} Ecosystem</title>
<meta name="title" content="Personal Knowledge Base | {OS.me} Ecosystem" />
<meta name="description" content="A comprehensive system for exporting, atomizing, and searching AI conversation history. Built for the high-density researcher." />

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website" />
<meta property="og:url" content="https://your-site-url.com/" />
<meta property="og:title" content="Personal Knowledge Base | {OS.me} Ecosystem" />
<meta property="og:description" content="Transforming chat chaos into structured intelligence. Semantic search, SQLite integration, and recursive knowledge units." />
<meta property="og:image" content="https://your-site-url.com/og-image.png" />

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image" />
<meta property="twitter:url" content="https://your-site-url.com/" />
<meta property="twitter:title" content="Personal Knowledge Base | {OS.me} Ecosystem" />
<meta property="twitter:description" content="Transforming chat chaos into structured intelligence. Semantic search, SQLite integration, and recursive knowledge units." />
<meta property="twitter:image" content="https://your-site-url.com/og-image.png" />
```

## Implementation Checklist
1. **The Image:** Create a high-resolution (1200x630px) PNG that features the UI or the "Knowledge Graph" to visual intrigue.
2. **The Description:** Keep it under 200 characters to prevent truncation on LinkedIn's mobile app.
3. **LinkedIn Post Inspector:** After deployment, run the URL through the [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/) to clear the cache and verify the preview.

## Verification
- Paste the URL into a LinkedIn "Start a post" field (without publishing) to see the live preview.
- Ensure the image is not cropped and the title captures the "Recursive Intelligence" value proposition.
