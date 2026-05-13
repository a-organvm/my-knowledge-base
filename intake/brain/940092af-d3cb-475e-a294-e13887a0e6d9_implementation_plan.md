# Full Interactive p5.js Slide Rewrite

The user observed that simply laying abstract p5.js loops *behind* static HTML cards (which had broken/highlighted states) did not achieve the goal. The slides must be driven by the animation, not just decorated by it.

Instead of background noise, the p5.js sketches will become the **primary visual storytelling element** for each slide, replacing the broken UI cards entirely. The only HTML we will keep is the Slide Title and Subtitle.

## 1. Upgrade P5 Environment
- #### [MODIFY] `src/web/components/PitchDeck/ui/slides/P5Wrapper.tsx`
  - Remove `pointer-events-none` and opacity filters so the sketches are full-opacity and can respond to mouse interaction (e.g., hover states).
  
## 2. Tear Down Broken HTML UIs
- #### [MODIFY] [Slide1.tsx](file:///Users/4jp/Workspace/intake/peer-audited--behavioral-blockchain/styx-project/src/web/components/PitchDeck/ui/slides/Slide1.tsx) through [Slide10.tsx](file:///Users/4jp/Workspace/intake/peer-audited--behavioral-blockchain/styx-project/src/web/components/PitchDeck/ui/slides/Slide10.tsx)
  - Rip out the broken grids, cards, and static `animate-fade-in` elements.
  - Simplify the React component to just standard Typography (h2, p) resting cleanly over (or beside) a dedicated `DynamicP5Background` that acts as the primary visual aid.

## 3. Rewrite Interactive p5Sketches
- #### [MODIFY] [p5Sketches.ts](file:///Users/4jp/Workspace/intake/peer-audited--behavioral-blockchain/styx-project/src/web/components/PitchDeck/ui/slides/p5Sketches.ts)
  - **Slide 1 (Hook)**: Interactive particle system that forms the word "STYX" or a precise geometry.
  - **Slide 2 (Intention-Behavior Gap)**: Draw the actual "User Retention Curve" dynamically in P5 instead of using static HTML bars.
  - **Slide 3 (Weaponizing Loss Aversion)**: A physics simulation demonstrating "Escrow" (particles pulled forcefully into a central gravity well) vs "Endowed Progress" (particles accelerated rapidly outwards).
  - **Slide 4 (Fury Bounty)**: Interactive node graph where users can click a node to trigger a "Fraud Detection" ping that sends red pulses to auditor nodes.
  - **Slide 5 (Legal Guardrails)**: Draw the Aegis Protocol shield geometry dynamically.
  - **Slide 6 (Market Pipeline)**: Draw a funnel or pipe showing Phase 1 flowing into a larger Phase 2 grid.
  - **Slide 7 (Unit Economics)**: Ensure the 15% house cut and other metrics are visualized via data flows in p5, not static cards.
  - **Slide 8 (Tech Stack)**: P5 drawing the database, queue, and storage icons connecting.
  - **Slide 9 (The Team)**: Three unified, rotating gears representing the team's skillset.
  - **Slide 10 (The Ask)**: Replace the bulleted list with an upward animated timeline drawn directly on canvas.

## Verification
1. Open the app locally on `http://localhost:3000/pitch`.
2. Ensure the broken HTML cards from Slide 2+ are completely gone.
3. Verify that the user retention curve and other concepts are now animated cleanly inside the p5.js canvas.
