---
contract_id: low-vision-and-reflow
title: Low Vision and Reflow
version: 1.0.0
status: canonical
layer: human
applies: [ui, web, design]
triggers: [ui-work, layout, typography]
rationale: People zoom, scale text, and use platform high-contrast modes. Layouts must survive all three without clipping, horizontal page scroll, or lost meaning.
---

<!-- contract-receipt: dell-echo-quay -->

# Low Vision and Reflow

## Purpose

Make interfaces survive real magnification: browser zoom, text scaling, and platform high-contrast modes — without trapping content, clipping controls, or forcing horizontal page scrolling.

## NORMATIVE RULES

1. Web UIs must reflow at 200% zoom (and equivalent text scaling) without clipping, truncation, or page-level horizontal scrolling. For suitable web UIs this is a release gate, verified in a real browser — not only by CSS proxies.
2. Text scaling is supported independently of zoom (preference or platform text size), with a documented floor (e.g. effective body ≥14px at scale 1.0) and a generous ceiling (≥200%).
3. Whole-page horizontal scrolling is avoided for normal application content. Dense technical tables may have contained, localized scrolling inside labeled regions — never as page-level scroll.
4. Contrast modes are coherent, not blinding: high-contrast modes increase luminance separation and add explicit component borders; they do not merely maximize brightness everywhere. Contrast targets live in a band (e.g. 8–10:1 preferred), not just a floor.
5. Component boundaries are clear on request: focus indicators, borders, and panel separation exist for people who need spatial structure.
6. Ambiguous icons have labels (text or accessible name); meaning is never positional only ("the leftmost tab is the dangerous one" is a defect).
7. Controls remain large enough (≥44px floor; larger via preference), line lengths stay readable (measure bounded), and text wraps rather than clipping (`overflow-wrap` rather than truncation for meaningful strings).
8. Platform forced-colors / high-contrast mode is supported: system palettes are not fought; app treatments are additive.

## RATIONALE

Zoom and text scaling are the most-used accessibility features in the world and the cheapest to support when designed in. Retrofitting reflow after a fixed-grid design is surgery; designing for it is a habit.

## HUMAN EXAMPLES

- At 200% zoom on a narrow window, the settings form stacks into one column; everything remains operable.
- A dense log table scrolls horizontally inside its own labeled panel; the page itself never scrolls sideways.
- With the OS high-contrast theme on, the app uses the system colors and stays fully legible.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- CI proxies: viewport-width + text-scale matrix tests; assertion of no `document.scrollingElement` horizontal overflow on app routes.
- Release gate: real-browser 200% zoom check (human or scripted real browser).
- `overflow-wrap: anywhere` for long identifiers; `text-overflow: ellipsis` only where the full value is otherwise reachable (title, detail view).
- Forced-colors media queries adjust, not override.

## GOOD EXAMPLES

```css
table.logs { overflow-x: auto; }
/* contained scrolling for a genuinely wide table, labeled by its caption */
body { overflow-x: clip; } /* never as the only reflow strategy */
```

## ANTI-PATTERNS

- Fixed-pixel layouts that clip at 150%.
- Truncated hashes with no way to see the full value.
- "High contrast" that turns the whole UI maximum-white.
- Relying on `overflow-x: hidden` to claim reflow compliance.

## ACCEPTANCE CHECKS

- Real browser at 200% zoom: every core flow operable, no page-level horizontal scroll?
- Text scale at 200%: layout survives, nothing clipped?
- Forced-colors mode: legible and coherent?
- Every truncated string reachable in full somewhere?