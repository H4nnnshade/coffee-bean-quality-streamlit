---
version: alpha
name: Arabica Aurora
description: Dark inspection console for coffee bean quality — aurora light band, gradient KPI rail, tabular numerics.
colors:
  primary: "#FF6B4A"
  secondary: "#A8A8B3"
  tertiary: "#4ADE80"
  neutral: "#0A0A0C"
  surface: "#141416"
  surface-raised: "#1C1C20"
  surface-sunken: "#101012"
  border-subtle: "#FFFFFF12"
  border-medium: "#FFFFFF24"
  text-primary: "#FFFFFF"
  text-secondary: "#A8A8B3"
  text-muted: "#8A8A93"
  hairline: "#5A5A63"
  action: "#C2410C"
  action-hover: "#9A3412"
  danger: "#FF5C5C"
  positive: "#4ADE80"
  aurora-left: "#2E8B7A"
  aurora-center: "#3B3B8F"
  aurora-right: "#E8552E"
  chip-defect-bg: "#2A1215"
  chip-defect-text: "#FDA4AF"
  chip-longberry-bg: "#2B1C0A"
  chip-longberry-text: "#FCD34D"
  chip-peaberry-bg: "#0E1B33"
  chip-peaberry-text: "#93C5FD"
  chip-premium-bg: "#0B2318"
  chip-premium-text: "#6EE7B7"
typography:
  display:
    fontFamily: Plus Jakarta Sans
    fontSize: 2.375rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  h1:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.875rem
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  h2:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.625rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  h3:
    fontFamily: Plus Jakarta Sans
    fontSize: 1.125rem
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.9375rem
    fontWeight: 500
    lineHeight: 1.55
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.875rem
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.875rem
    fontWeight: 500
    lineHeight: 1.4
  caption:
    fontFamily: Plus Jakarta Sans
    fontSize: 0.75rem
    fontWeight: 400
    lineHeight: 1.4
  numeric-lg:
    fontFamily: JetBrains Mono
    fontSize: 1.5rem
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  numeric-md:
    fontFamily: JetBrains Mono
    fontSize: 0.9375rem
    fontWeight: 600
    lineHeight: 1.3
  numeric-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.8125rem
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: 8px
  md: 12px
  lg: 20px
  xl: 24px
  pill: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
components:
  button-primary:
    backgroundColor: "{colors.action}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    height: 44px
    padding: 24px
    typography: "{typography.label}"
  button-primary-hover:
    backgroundColor: "{colors.action-hover}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    height: 44px
    padding: 24px
    typography: "{typography.label}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    height: 44px
    padding: 24px
    typography: "{typography.label}"
  card-surface:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: 28px
  card-stat-label:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.sm}"
    padding: 8px
    typography: "{typography.caption}"
  badge-positive:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.positive}"
    rounded: "{rounded.pill}"
    padding: 8px
    typography: "{typography.numeric-sm}"
  badge-negative:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.danger}"
    rounded: "{rounded.pill}"
    padding: 8px
    typography: "{typography.numeric-sm}"
  nav-item-active:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    size: 44px
  search-input:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.pill}"
    height: 44px
    padding: 20px
    typography: "{typography.body-sm}"
  chip-defect:
    backgroundColor: "{colors.chip-defect-bg}"
    textColor: "{colors.chip-defect-text}"
    rounded: "{rounded.sm}"
    padding: 8px
    typography: "{typography.caption}"
  chip-longberry:
    backgroundColor: "{colors.chip-longberry-bg}"
    textColor: "{colors.chip-longberry-text}"
    rounded: "{rounded.sm}"
    padding: 8px
    typography: "{typography.caption}"
  chip-peaberry:
    backgroundColor: "{colors.chip-peaberry-bg}"
    textColor: "{colors.chip-peaberry-text}"
    rounded: "{rounded.sm}"
    padding: 8px
    typography: "{typography.caption}"
  chip-premium:
    backgroundColor: "{colors.chip-premium-bg}"
    textColor: "{colors.chip-premium-text}"
    rounded: "{rounded.sm}"
    padding: 8px
    typography: "{typography.caption}"
---

## Overview

Arabica Aurora is the dark counterpart of the light "vibrant crypto" palette locked in
`ARCHITECTURE.md` §19. It keeps the same design language — gradient KPI rail, aurora light
band, tabular numerics, hairline borders — and inverts the substrate from `#F8FAFC` to
`#0A0A0C`.

The product is an inspection console, not a marketing page. Density is deliberate: the
operator uploads one bean photo and needs a verdict, three backbone opinions, and a
probability distribution inside a single screen. Nothing decorative may compete with the
verdict chip.

Three surfaces, strictly ordered by elevation:

1. `neutral #0A0A0C` — the app field.
2. `surface #141416` — cards. One card per logical unit, never nested cards.
3. `surface-raised #1C1C20` — only interactive state (active nav tile, popover, tooltip).

The aurora band is a single full-width absolutely-positioned layer behind the header and
the top of both columns. It is decoration. It carries no status information and is exempt
from WCAG SC 1.4.11 for that reason. Never let a verdict colour depend on the aurora.

## Colors

- **Primary `#FF6B4A`** — "Roast Ember". Sole driver for interaction: active tab text,
  secondary button border and label, link affordances, chart stroke start. 7.02:1 on
  `neutral`; 6.53:1 on `surface`.
- **Action `#C2410C`** — solid fill only, for filled buttons. `#FF6B4A` cannot carry white
  text (2.82:1, fails AA), so the filled variant darkens to `#C2410C` at 5.18:1. The
  ember hue reads as the same family while passing.
- **Neutral `#0A0A0C`** — app background. Never used as a text colour.
- **Surface `#141416` / `surface-sunken #101012`** — card fill, subtle vertical gradient
  `#141416 → #101012`. `surface-sunken` is for inset regions only (search field, empty
  preview well, code blocks) so inset regions read as pressed *into* the card.
- **Text `#FFFFFF` / `#A8A8B3` / `#8A8A93`** — 20.4:1, 8.40:1, 5.79:1 on `neutral`;
  18.4:1, 7.58:1, 5.38:1 on `surface`. All three pass AA. There is no fourth, darker text
  tone: `hairline #5A5A63` is 2.90:1 and is **not permitted on text**, only on 1px
  dividers, chart gridlines, and inactive icon strokes at ≥ 3:1 against `surface` is
  required — `#6B6B73` is the lowest legal icon stroke.
- **Positive `#4ADE80` / Danger `#FF5C5C`** — 11.35:1 and 6.53:1 on `neutral`. These are
  the only two colours allowed to describe a classification outcome direction. Confidence
  deltas use them; verdict chips do not (see chip tokens).
- **Chip tokens** — the four quality classes keep distinct hues, darkened into tinted
  wells so a chip never out-shouts the verdict headline. All four pairs pass ≥ 7:1.

The aurora band is a three-stop gradient `#2E8B7A → #3B3B8F → #E8552E` at 100% width,
~200px tall, with an 8% noise overlay in `overlay` blend. Cards that overlap it use
`backdrop-filter: blur(20px)`.

## Typography

`Plus Jakarta Sans` for all prose, `JetBrains Mono` for every number that can change
between two renders — confidence, latency, image dimensions, probability percentages,
split ratio. The mono face is what makes a column of confidences scannable; do not
substitute the sans face for numerals because it "looks cleaner".

Numeric display uses `font-variant-numeric: tabular-nums` and `letter-spacing: -0.02em`.
Large numbers always carry negative tracking; body copy never does.

Uppercase micro-labels (`Engine Pipeline`, `Kelas Mutu`) are `caption` at `700` with
`letter-spacing: 0.06em`. They are the only uppercase text in the system.

## Layout

1440×900 reference frame. Base unit 4px.

- Sidebar rail: 90px fixed, `neutral`, no border. Icons 22px, 28px vertical gap, active
  tile 44×44 at `surface-raised`.
- Content: outer padding 24px top, 32px sides and bottom.
- Two columns: main flexible, right rail fixed 360px, 24px gutter.
- Main column stacks KPI rail → chart card, 24px gap.
- Stat groups inside a card: 48px column gap, no dividers between them — spacing only.
- Card internal section gap 32px; card padding 28–32px.

Responsive: below 900px the right rail drops under the main column; below 600px the KPI
rail goes 2×2 and the sidebar collapses to a 56px icon strip.

## Elevation & Depth

Three levels only.

1. Flat — cards on `neutral`, separated by `border-subtle` 1px. No shadow.
2. Raised — tooltip, popover, active nav tile: `0 20px 60px rgba(0,0,0,0.5)` plus
   `surface-raised` fill.
3. Glow — reserved for the primary CTA and the chart stroke:
   `0 8px 24px rgba(255,107,74,0.3)`. Glow is never applied to a card.

Cards carry a faint inner top highlight `rgba(255,255,255,0.04)` instead of a shadow. On a
near-black field a drop shadow is invisible; the highlight is what separates the card from
the field.

## Shapes

`rounded.sm 8px` for chips and inline wells, `md 12px` for buttons, inputs, nav tiles,
`lg 20px` for cards, `xl 24px` for the app shell, `pill` for badges and the segmented
control. Never mix two radii inside one component.

The donut uses `stroke-linecap: round` and a 4px gap between segments; the segmented
control uses a 12px pill container with a filled active segment, no underline indicator.

## Components

`button-primary` is the single high-emphasis action per screen — in this product it is
"Jalankan Klasifikasi". Every other action is `button-secondary` (ember outline on
surface). Never place two filled buttons in one viewport.

The KPI rail is four gradient cards, `115deg`, white solid text, white `0.22` icon tile,
`rgba(255,255,255,0.20)` border, and a colour-matched glow. Gradient stops are locked in
`ARCHITECTURE.md` §19.2 and are grandfathered at 4.56:1 — they are the one place in the
system where white text sits just above the AA floor, and they must not be re-tinted
without a new spec.

`search-input` sits on `surface-sunken` with a 1px `border-subtle` ring and a muted
magnifier glyph. It is a filter affordance, not a command palette.

## Do's and Don'ts

- Do keep every number in `JetBrains Mono` with tabular figures.
- Do let the verdict chip own the largest type on the screen.
- Do use `rgba(255,255,255,0.06)` hairlines; never a solid grey border on dark.
- Don't put white text on `#FF6B4A` — use `action #C2410C` for filled surfaces.
- Don't use `#5A5A63` for text at any size.
- Don't nest a card inside a card. Inset regions use `surface-sunken`, not a second card.
- Don't animate a card's background colour; animate transform and shadow only, 180–200ms.
- Don't add a fourth elevation level.
