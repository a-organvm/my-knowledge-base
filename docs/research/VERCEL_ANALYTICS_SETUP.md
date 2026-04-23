# Setup Guide: Vercel Analytics for React (Vite)

## Objective
Implement Vercel Analytics to establish a conversion rate baseline and monitor user interaction (searching, browsing) without sacrificing performance.

## 1. Installation
Install the Vercel Analytics package in your frontend directory:

```bash
npm install @vercel/analytics
```

## 2. Component Integration
Import and add the `<Analytics />` component to your root entry point (e.g., `web-react/src/main.tsx` or `web-react/src/App.tsx`).

```typescript
import { Analytics } from "@vercel/analytics/react"

export default function App() {
  return (
    <>
      <MyApplication />
      <Analytics />
    </>
  )
}
```

## 3. Configuration in Vercel Dashboard
1. Go to your project on [vercel.com](https://vercel.com).
2. Select the **Analytics** tab.
3. Click **Enable** (the "Web Vitals" and "Speed Insights" are also recommended and free for hobby projects).

## 4. Establishing a Baseline
Review the dashboard after 24-48 hours of traffic to analyze:
- **Unique Visitors:** Total reach.
- **Conversion Rate:** Track a custom event (e.g., `track('Search Triggered')`) to see how many visitors actually engage with the search engine.
- **Top Paths:** Which knowledge units are being viewed most frequently.

## Custom Event Tracking (Optional)
To track specific interactions:

```typescript
import { track } from '@vercel/analytics';

const handleSearch = (query: string) => {
  // ... perform search ...
  track('Search', { query });
};
```
