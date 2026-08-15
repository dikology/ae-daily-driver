---
name: dataviz
description: Use when reviewing an existing product-analytics chart/dashboard, or when exploring/discovering insights in a dataset ad-hoc. Produces or reviews a vertical stack of "insight cards" combining data-visualization grammar rules (Section A) with Apple-style direct-manipulation motion (Section B). Picks output mode by user intent (Section E). Trigger on "review this chart/dashboard", "explore this data", "build an analytics card", "adhoc analysis", "canvas", "save report".
---

# Dataviz

A single format for two modes: **Review** (audit existing chart/dashboard code) and **Discovery** (ad-hoc exploration of a dataset). Both modes operate on the same unit of content: an **insight card** — one chart or statement, encoded correctly (Section A) and animated/interacted with restraint (Section B). Deliver via the output mode the user requests (Section E).

Default to flagging in Review mode; approval is earned, not assumed. Default to progressive disclosure in Discovery mode; never dump more than one new insight per turn.

---

## Section A — Visualization Grammar Rules

Every card's chart must be checked against the tables below before it is approved or added to the stack. Sources: [data-to-viz.com](https://www.data-to-viz.com/), [caveats](https://www.data-to-viz.com/caveats.html).

### A.1 — General grammar

| Category | Rule | Anti-pattern (block on sight) |
|---|---|---|
| Data-ink ratio | Maximize ink spent on data; strip decorative gridlines, 3D bevels, drop shadows on bars | 3D pie chart, gradient-filled bars, chartjunk borders |
| Color budget | Max ~7-10 colors across the whole dashboard; max 3 accent colors per single card | Rainbow palette on a categorical axis with 12+ categories |
| Encoding-to-data-type match | Categorical → color/shape; quantitative → position/length; ordinal → sequential color | Continuous metric encoded only by hue with no legend gradient |
| Scale consistency | Same field must share the same scale/domain across all cards in one facet/comparison set | Two "revenue by month" cards in the same stack with different y-axis max |
| Overview-to-detail | Card shows the aggregate/pattern first; raw rows or drill-down appear only on explicit request | Dumping a 500-row raw table as the first card of an analysis |
| Grayscale-safe | Encoding must stay legible without color (pattern, shape, or position fallback) | Line chart distinguishing 5 series by color only, no dash/marker variation |
| One card, one claim | Each card answers exactly one question; no multi-panel card with 4 unrelated metrics | A single card mixing revenue, churn, and NPS in one grid |

### A.2 — Data type → chart type

Determine the input shape first, then pick the chart. **One main insight = one primary chart per card.**

| Data shape | Typical choice | Avoid |
|---|---|---|
| One numeric variable | histogram, density, box/violin | pie |
| Two numeric variables | scatter; many points → 2d density / sample | rainbow hue on points |
| Numeric + time (one series) | **line** / area | pie by month |
| Numeric + time (many series) | line up to ~5–7 series; else faceting / top-N | spaghetti |
| One category + numeric | **bar/column** (sorted by value) | pie with >5–6 slices |
| Multiple categories + numeric | grouped/stacked bar; heatmap | radar "because it looks cool" |
| Hierarchy / part-to-whole | treemap, stacked bar | 3D pie |
| Flow A→B | sankey | arrows without magnitudes |
| Correlations across many numerics | heatmap / correlogram | dozens of scatter plots |

### A.3 — Required practices

1. **Sort categories** by magnitude unless a natural order exists (months, funnel stages).
2. **Label axes and units** (devices, %, events/s).
3. **Title = conclusion**, not "Chart 1" — e.g. "App MAU grew 8% over 6 weeks."
4. **Do not truncate the Y axis on bar charts** without an explicit reason — it distorts height comparisons.
5. **Minimize ink:** no 3D, gratuitous gradients, or decorative colors with no meaning.
6. **Color = meaning:** one series / one segment = one color across all cards in the same answer.
7. **Annotate the key point** (peak month, feature launch) when it carries the story.
8. **Do not make the reader do mental math:** show the delta / share on or beside the chart.

### A.4 — Common caveats (block or fix)

| Problem | Do instead |
|---|---|
| **Pie / angles** hard to read | bar or table; pie only for 2–5 slices |
| **Spaghetti** (too many lines) | top-N + "other", small multiples, or one focus line |
| **Dual axis** easily misleads | two separate charts or index to base 100 |
| **Rainbow palette** for a numeric scale | sequential palette (light→dark) |
| **Overplotting** on scatter | transparency, sample, hexbin/density |
| **Boxplot hides n and shape** | violin / strip + show n |
| **Stacked bar** hard to compare middle segments | grouped bar or focus on one segment's share |
| **Bubbles encoded by radius** | encode by **area**, not radius |
| **3D** | always 2D |
| **Extreme aspect ratio** | normal proportions (~16:9 or square) |
| **Inconsistent colors** across cards | one legend / one encoding scheme |
| **Long vertical category labels** | horizontal bar |
| **Histogram without bin-size check** | try 2–3 bin widths; pick the stable pattern |

### A.5 — Pre-send checklist

Before approving a card (Review) or adding it to the stack (Discovery):

- [ ] Chart type matches data shape (A.2 table)
- [ ] No spaghetti / pie with 10+ slices / dual-axis without justification
- [ ] Categories ordered meaningfully
- [ ] Title states the conclusion; axes labeled in the user's language
- [ ] Series and point counts are reasonable (≤7 series on line; ≤15 categories on bar)
- [ ] Colors consistent across cards in the same analysis
- [ ] A table with exact numbers sits beside the chart (the chart is not the sole source of truth)

## Section B — Motion & Interaction Principles

Subset of Apple's direct-manipulation principles, applied only to how cards enter, reorder, and respond to touch/drag — never to the chart's data encoding itself.

| Principle | Applied to cards | Concrete rule |
|---|---|---|
| Direct manipulation (1:1 tracking) | Dragging a card must track the pointer exactly, no lag | translateX/Y bound directly to pointer delta, no easing during drag |
| Interruptibility | A card mid-transition can be grabbed and redirected instantly | Never block input during an animation; kill and re-target on grab |
| Velocity handoff | Swipe-to-dismiss/reorder inherits release velocity | Apply momentum/projection on release, not a fixed-duration snap |
| Rubber-banding | Dragging past the first/last card resists and springs back | Damped overscroll, never a hard stop |
| Spatial consistency | New cards enter from a consistent, predictable origin (bottom or right) | Same enter/exit anchor for every card in the stack |
| Hint in direction of gesture | Partially-revealed next card hints at scroll direction | Peek 10-15% of the next card at rest |
| Reduced motion | All entrance/reorder animation must have a static fallback | Respect prefers-reduced-motion: crossfade instead of slide/spring |

### The Core Idea

> "When we align the interface to the way we think and move, something magical happens — it stops feeling like a computer and starts feeling like a seamless extension of us."

An interface is fluid when it behaves like the physical world: things respond instantly, move continuously, carry momentum, resist at boundaries, and can be redirected mid-motion. Everything below is a way to get closer to that.

Apple frames design as serving four human needs: **safety/predictability, understanding, achievement, and joy.** Every rule here serves one of them.

### Direct manipulation — 1:1 tracking

> "Touch and content should move together."

When the user drags something, it must stay glued to the finger — and respect the offset from *where they grabbed it*. Snapping to the element's center on grab breaks the illusion immediately.

- Use Pointer Events with `setPointerCapture` so tracking continues even when the pointer leaves the element's bounds.
- Track a short **velocity/position history** (last few `pointermove` events), not just the current point — you'll need velocity at release.

```js
el.addEventListener('pointerdown', (e) => {
  el.setPointerCapture(e.pointerId);
  const grabOffset = e.clientY - el.getBoundingClientRect().top; // respect where they grabbed
  // ...track position + timestamp history for velocity
});
```

### Interruptibility — the single most important principle

> "The thought and the gesture happen in parallel."

Every animation must be interruptible and redirectable at any moment. A user must be able to grab a moving element mid-flight and reverse it without waiting for the animation to finish. A closing modal the user grabs again should follow the finger — not finish closing first, then reopen.

- **Never lock out input during a transition.**
- **Always animate from the *presentation* (current) value, never the target value.** On interrupt, read the element's live on-screen transform and start the new animation from there. Starting from the logical/target value causes a visible jump.
- **Avoid CSS transitions and `@keyframes` for anything gesture-driven** — they can't be smoothly grabbed and reversed mid-flight. Springs animate from the current value by default, which is exactly what interruption needs.
- **When a gesture reverses, blend velocity — don't hard-cut it.** Replacing one animation with another at a reversal creates a velocity discontinuity, a "brick wall." Spring libraries that carry velocity through a re-target avoid it. (This is what iOS's *additive animations* do natively; on the web, choose a spring library that re-targets from the current velocity.)
- **Decompose 2D motion into independent X and Y springs.** A single spring on a 2D distance desyncs when X and Y have different velocities.

### Velocity handoff — the seam between drag and animation

When a gesture ends, the animation must **continue at the finger's exact velocity**, so there's no visible seam between dragging and animating. This is the detail that most separates "fluid" from "fine."

Pass the pointer's release velocity as the spring's initial velocity. Some spring APIs want **relative** velocity — normalize it by the remaining distance to the target:

```
relativeVelocity = gestureVelocity / (targetValue − currentValue)
```

Example: element at `y=50`, target `y=150` (100px to go), finger moving 50px/s → initial spring velocity = `50 / 100 = 0.5`. Framer Motion / Motion take absolute px/s velocity directly (`velocity` option), so you usually hand it the raw value.

### Spatial consistency — symmetric paths, anchored origins

> "If something disappears one way, we expect it to emerge from where it came."

- **Enter and exit along the same path.** A panel that slides in from the right must dismiss to the right. In-from-right / out-the-bottom feels disconnected and confusing.
- **Anchor interactions to their source.** A menu, popover, or sheet should originate from the element that triggered it — set `transform-origin` to the trigger, so the spatial relationship between button and content is obvious. (This is the same origin-awareness point as popovers scaling from their trigger, not their center.)
- **Mirror the easing on reversible transitions** so the outbound path matches the return path (use inverse cubic-bézier control points for the two directions).

### Rubber-banding — soft boundaries

At an edge, resist progressively instead of stopping hard. A hard stop reads as "frozen"; continuous resistance reads as "responsive, but there's nothing more here." Apply damping that increases the further past the boundary the user drags.

```js
// The further past the bound, the less the element follows — real things slow before they stop
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

### Gesture design details (the "feel" checklist)

- **Tap:** highlight on touch-*down* (instant), commit on touch-*up*. Add ~10px of hysteresis/hit padding around the target, and allow cancel-by-dragging-away and back.
- **Drag/swipe:** require a small movement threshold (hysteresis, ~10px) before committing to a direction, then track 1:1.
- **Detect all plausible gestures in parallel from the first move**, then confidently cancel the losers once intent is clear. Avoid recognizers that only report a *final* state (`swipeleft`-type events) — they throw away the continuous tracking you need for feedback.
- **Minimize disambiguation delays.** Double-tap detection unavoidably delays single taps; only pay that cost where double-tap truly exists.

### Materials & depth — translucency conveys hierarchy

Apple uses translucent materials as a floating functional layer that brings structure without stealing focus. On the web, approximate with `backdrop-filter`.

- **Build nav/toolbars/sheets as translucent layers** (`backdrop-filter: blur()` + a semi-transparent background) with content scrolling underneath — not opaque bars that consume a fixed strip.
- **Material weight encodes hierarchy:** darker/heavier materials separate structural regions (sidebars); lighter materials draw attention to interactive elements (buttons). **Never stack a light translucent surface on another** — legibility collapses.
- **Bigger surfaces should read as thicker:** stronger blur + a deeper shadow than small chips. Consider context-aware shadow — heavier over busy/text content for separation, lighter over plain backgrounds.
- **Dim to focus, separate to keep flow.** A modal task pairs the surface with a dimming scrim and pushes the background back/down. A parallel, non-blocking panel uses translucency and offset *without* a scrim so the flow isn't broken. For stacked sheets, progressively dim and push back each parent layer.
- **Vibrancy keeps text legible over changing backgrounds.** Over blurred/translucent surfaces, don't use flat gray text — use higher-contrast, slightly heavier weight, and a small letter-spacing bump. Put color on a solid layer, not the translucent foreground.
- **Scroll edge effects, not hard dividers.** Instead of a 1px border under a sticky header, fade a small blur/gradient mask where content meets floating chrome — only where floating UI actually overlaps content.
- **Materialize, don't just fade.** For glass/blur surfaces, animate blur radius and scale together on enter/exit, so the surface reads as a real material arriving rather than a plain opacity fade.

```css
.toolbar {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.4); /* bright top edge = light catching the material */
}
```

### Reduced motion & accessibility

Reduced motion doesn't mean *no* feedback — it means a gentler, non-vestibular equivalent. Respond to three independent signals and bake them into your components:

- **`prefers-reduced-motion: reduce`** — replace slides/springs/parallax with short opacity **cross-fades or static transitions**. Drop elastic/overshoot. Keep opacity/color changes that aid comprehension.
- **`prefers-reduced-transparency: reduce`** — make translucent surfaces frostier/solid: raise background opacity, drop the blur.
- **`prefers-contrast: more`** — near-solid backgrounds with a defined, contrasting border.

Also: avoid full-viewport moving backgrounds, slow looping oscillations (near 0.2 Hz / one cycle per 5s), and abrupt brightness jumps (ease dark↔light theme changes). Make large moving objects semi-transparent while they travel, and fade big surfaces out during a large reposition and back in once settled.

```css
@media (prefers-reduced-motion: reduce) {
  .sheet { transition: opacity 200ms ease; transform: none !important; }
}
@media (prefers-reduced-transparency: reduce) {
  .toolbar { background: white; backdrop-filter: none; }
}
```

### Typography — optical sizing, tracking, leading

Apple designs type to change shape with size; the same discipline applies on the web. (From *The Details of UI Typography*, WWDC 2020.)

- **Tracking (letter-spacing) is size-specific — never one value for all sizes.** Large display text wants *negative* tracking (letters read too far apart as they grow); small text wants slightly *positive* tracking for legibility. A fixed `letter-spacing` is wrong somewhere. Tighten headings, leave body near `0`.
- **Leading (line-height) tracks size inversely.** Tight on large headings, looser on body copy. Increase it for scripts with tall ascenders/descenders; tighten it for dense, information-heavy UI.
- **Build hierarchy from weight + size + leading as a set,** not size alone. Emphasize with weight — it adds presence without taking more space.
- **Respect the user's text-size setting** (Dynamic Type). Scale layout *with* the text — spacing in `rem`/`em`, not fixed px — so a larger font doesn't break the layout.
- **Default to the platform's system font** before a custom face; it already ships optical sizing, tracking tables, and legibility tuning. Override only with a reason.

```css
:root { font: 100%/1.5 system-ui, sans-serif; } /* body: system font, comfortable leading */

.display {
  font-size: clamp(2rem, 5vw, 4rem);
  line-height: 1.05;        /* tight leading for large text */
  letter-spacing: -0.02em;  /* negative tracking as it grows */
  font-optical-sizing: auto;
}
```

### Design foundations — the eight principles

The motion and craft above serve Apple's eight design principles (*Principles of Great Design*, WWDC 2026). Use these as the names you reason with:

1. **Purpose.** Make with intention; decide what *not* to build. Every feature asks for the user's time, attention, and trust — spend that budget only where it pays off.
2. **Agency.** Keep people in control: offer choices, don't force a single path. Back it with forgiveness — easy undo for slips, a confirmation dialog only for genuinely destructive, irreversible actions (use sparingly; overusing it trains people to click through).
3. **Responsibility.** Act in the user's interest. Privacy: ask at the right moment, only for what's needed, transparently. Safety: anticipate misuse and harm — especially with AI (an allergy-aware recipe app must not suggest a harmful ingredient). Add previews, confirmations, disclaimers; cut a feature whose risk outweighs its value.
4. **Familiarity.** Build on what people already know. Use metaphors that are neither too literal nor too abstract (a trash can means delete), and honor their physics. Be consistent: things that look the same must behave the same and live in the same place (close is always top-left on macOS) so people can predict what happens next. Only break a familiar pattern if you can prove it's better — then test it, don't assume.
5. **Flexibility.** Design for different contexts, devices, and the full range of abilities. Adapt to the platform (iPhone = quick touch; desktop = deep workflows with precise pointer control) and to the situation. Design inclusively (age, language, expertise, accessibility). When no single layout fits everyone, let people personalize — rearrange controls, hide what they don't use.
6. **Simplicity — not minimalism.** Strip the unnecessary so the core purpose shines; burying everything in one place looks minimal but isn't simple. Be concise (plain language, no jargon, fewer steps) and clear (use hierarchy — order, spacing, contrast — so the most important thing is the most obvious). Every element earns its place; sometimes *adding* context simplifies (a video scrubber that shows time remaining). Show the common path first, advanced options one level deeper.
7. **Craft.** Uncompromising attention to detail builds trust. Beautiful typography, colors that adapt to light/dark, clear iconography, and responsive animations that give immediate, natural feedback. Nothing is random — every spacing, timing, and alignment value is a deliberate choice you can defend. Jittery scroll, misaligned icons, and layouts that break on rotation read as carelessness. Craft needs iteration and longevity — keep evolving the design as features and hardware change.
8. **Delight.** The result of getting the other seven right, not confetti tacked on top. Decide the emotion you want people to feel (calm, confident, excited) and reinforce it in every decision.

Tactical rules that serve these:

- **Feedback comes in four kinds:** status, completion, warning, error. Confirm meaningful actions, expose ongoing status, warn before problems, validate inline (not on submit).
- **Wayfinding.** Every screen should answer: Where am I? Where can I go? What's there? How do I get out? Never trap the user.
- **Grouping & mapping.** Proximity implies relationship; place a control near what it affects and arrange controls to mirror what they change. If you need a label to explain a control, the mapping is weak.
- **Direct, specific labels beat safe generic ones.** Name nav items for their contents ("Progress", "Library"), not vague umbrellas ("Home"). Specificity creates predictability.

### Process

- **Prototype interactively — an interactive demo is worth "a million static designs."** You discover the interface by building and playing with it; a working prototype also sets a concrete bar that prevents a mediocre final implementation.
- **Design interaction and visuals together.** "You shouldn't be able to tell where one ends and the other begins." Motion is not a layer added after the pixels.
- **Test with real people in real context**, and review motion with fresh eyes — play it in slow motion / frame-by-frame to catch what's invisible at full speed.

## Quick Reference

| Need | Technique | Concrete value |
| --- | --- | --- |
| Default UI spring | Critically damped, no overshoot | `damping 1.0`, `response 0.3–0.4` |
| Momentum / flick spring | Under-damped, slight bounce | `damping ~0.8`, `response 0.3–0.4` |
| Gesture → spring velocity | Hand off release velocity | `gestureVelocity / (target − current)` if normalized |
| Flick landing point | Project momentum | `current + (v/1000)·d/(1−d)`, `d ≈ 0.998` |
| Interrupt cleanly | Start from presentation (live) value | read the on-screen transform |
| Avoid reversal "brick wall" | Carry velocity through re-target | spring that blends velocity |
| Reversible transition | Mirror the easing curve | inverse cubic-bézier |
| Decide reverse vs. commit | Use velocity **sign**, not position | at release |
| 1:1 drag | Pointer Events + capture | respect the grab offset |
| Feedback | On pointer-down, continuous | never only at the end |
| Boundary | Rubber-band, don't hard-stop | progressive resistance |
| Translucent chrome | `backdrop-filter` layer | content scrolls under |
| Type tracking | Size-specific, never fixed | tighten large text (`-0.02em`), body near `0` |
| Reduced motion | Cross-fade, not slide/spring | `@media (prefers-reduced-motion)` |

## Section C — Review Mode

Use when the user provides existing chart/dashboard code or a screenshot.

1. Walk every card against Section A (A.1–A.5) first (data correctness before polish).
2. Walk every card's transition/drag behavior against Section B.
3. Output as a findings table:

| Card | Issue | Section | Severity (Block/Warn) | Fix |
|---|---|---|---|---|
| ... | ... | A or B | ... | concrete code/encoding change |

4. End with a verdict line: **Approved** only if zero Block-severity findings remain.

## Section D — Discovery Mode

Use when the user provides a raw dataset and wants ad-hoc/exploratory analysis.

1. Ask one question of the data at a time; produce exactly one new card per answer.
2. Each new card must pass Section A (A.1–A.5) before being added to the stack (no unchecked chart ever enters the stack).
3. Default view: aggregate/pattern card. Only add a raw-detail card if the user explicitly drills in.
4. New cards enter the stack following Section B's spatial-consistency and reduced-motion rules.
5. Never restate a metric already shown in an earlier card — if a new question reuses a prior card's scale, reuse that card's field/domain rather than re-deriving it.

## Section E — Output Modes

Visualization is expensive (tokens, time, external APIs). **Do not render charts unless the user's request matches a format below.** If ambiguous ("make it look nice"), ask one clarifying question: chat chart, saved file, or interactive canvas?

| # | Trigger | Where | Charts |
|---|---|---|---|
| 1 | Default question (no explicit viz request) | Chat | No — text + table only |
| 2 | "report" / "chart" / "graph" / "visualize" / "build an analytics card" | Chat | Yes — one card at a time (Discovery) or findings table (Review) |
| 3 | "save report" / "export report" / "put in analyses" | File in `analyses/` | Yes — same content as #2, persisted |
| 4 | "canvas" / "interactive report" / "open beside chat" / "dashboard in canvas" | Canvas or equivalent | Yes — interactive card stack |
| 5 | "save SQL" / "for validation" / "export queries" | `analyses/validation/` | No — code + question only |

Format 5 can combine with 1–4. Do not commit saved reports unless the user explicitly asks.

### Saved report (format 3)

If the user does not specify a file format, ask once (default = markdown):

1. **markdown** — `.md` in `analyses/` + images alongside (or embedded links)
2. **html** — one self-contained `.html` in `analyses/` (see below)
3. **pdf** — `.pdf` in `analyses/`

Naming: `analyses/YYYY-MM-DD_<slug>.{md|html|pdf}`. After saving, tell the user the path in chat.

### HTML = always single-file (default)

When output is HTML — whether format 3 or the non-Cursor fallback for format 4 — produce **one** self-contained artifact:

- Path: `analyses/YYYY-MM-DD_<slug>.html`
- CSS and JS inline (`<style>`, `<script>`); embed Plotly/Vega-Lite via CDN or inline bundle
- Data inline as JSON — no external file dependencies, no build step
- Images as **data URIs** (`data:image/png;base64,…`) — not separate files, not external URLs as the only dependency
- **No** `analyses/assets/…` folder and **no** relative links to sibling files
- One `<div class="card">` per insight card, stacked vertically (Discovery order = DOM order)
- Apply Section B motion via plain CSS/JS in the file (`prefers-reduced-motion`, inline drag/swipe script)

Separate asset folders are allowed **only** if the user explicitly asks for "multi-file" / "with assets folder."

### Canvas / interactive (format 4)

Triggers: "canvas", "interactive report", "open beside chat", "dashboard in canvas."

| Environment | Action |
|---|---|
| **Cursor** | Cursor Canvas: one `.canvas.tsx` per the `canvas` skill (`~/.cursor/skills-cursor/canvas/SKILL.md`). Data inline, no `fetch`. |
| **Non-Cursor** (VS Code / CLI / other IDE) | **Equivalent** — the same single-file HTML as format 3 (`analyses/YYYY-MM-DD_<slug>.html`); give path + how to open in browser. |

Do not substitute format 2 (chat + static image) when the user asked for canvas/interactive. If the environment is unclear, ask once: "Canvas in Cursor, or single-file HTML?"

In canvas/HTML interactive output, follow the same card order and Section A/B rules as chat cards.

### Anti-patterns (output)

- Charts without an explicit viz request (format 1 → no charts)
- HTML report with external assets folder or broken relative links (must open as one file)
- "Canvas" in a non-Cursor environment without the HTML equivalent
- "Save report" without writing a file or stating the path
- Format 5 without `question.md` or without `analyses/validation/` folder structure
