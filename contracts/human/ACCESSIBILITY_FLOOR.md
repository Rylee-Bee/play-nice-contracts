---
contract_id: accessibility-floor
title: Accessibility Floor
version: 1.0.0
status: canonical
layer: human
applies: [ui, web, product]
triggers: [ui-work, always-for-ui]
rationale: Accessibility is architecture, not polish, not a plugin, not a special mode. The default product must already be accessible; preferences may improve comfort but may never lower the floor.
---

<!-- contract-receipt: ridge-meadow-kindle -->

# Accessibility Floor

## Purpose

Ensure the default product is usable by people with different vision, motor control, attention, and assistive technology. Accessibility is a universal design requirement — not a user preference, not a mode, not a different product.

## NORMATIVE RULES

1. All functionality is reachable and operable by keyboard alone. No keyboard traps. Escape exits overlays.
2. Focus is always visible (sufficient-contrast indicator, never removed for aesthetics) and follows logical source/reading order.
3. Interactive targets have a minimum hit area of 44×44 CSS px (visual icons may be smaller; hit areas may not).
4. Status and meaning are never carried by color, icon, position, animation, glow, or expression alone — an explicit text label accompanies every status.
5. Real heading hierarchy with no skipped levels; landmarks (`header`, `nav`, `main`); a skip-to-content link is the first focusable element on pages.
6. Real accessible names for every meaningful interactive element; real labels for inputs; native controls and platform primitives (`dialog`, `popover`, `details`) preferred over invented ones.
7. Error messages are specific: name what failed, confirm what still works, suggest the next reasonable action.
8. Browser zoom and user text scaling are never disabled. Web UIs reflow at 200% zoom without clipping, truncation, or page-level horizontal scrolling.
9. `prefers-reduced-motion` is honored unconditionally and overrides application motion preferences. Platform forced-colors / high-contrast modes are supported additively, never fought.
10. Destructive actions are named by verb and consequence, never "OK / Yes / Proceed". Confirmations start focus on the safe action.
11. No essential interaction requires hover, drag, double-click, or fine motor precision. Where drag exists as convenience, a button/menu alternative exists.
12. Dialogs and drawers behave: modal ones trap focus, make the background inert, close on Escape, and restore focus to the trigger; non-modal ones move focus in and back out.
13. Preferences tune an already-accessible product; there is no "accessibility mode". No combination of preferences may drop below this floor.

## RATIONALE

Accessibility requirements encode real, common human conditions — limited vision, motor differences, screen readers, low bandwidth, fatigue. Building them into the default makes the product work for everyone (including automation and keyboard-heavy power users) instead of maintaining a separate "accessible" build that silently rots. Distilled from Personal World's and VEFR's accessibility contracts.

## HUMAN EXAMPLES

- A screen-reader user hears "Status: needs attention, certificate expires in 2 days" — not a colored dot.
- A keyboard-only user can reach, operate, and exit every overlay.
- Zooming to 200% reflows the layout; nothing is clipped or hidden behind a scrollbar-less page.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Automated checks (axe-class scans, target-size probes, heading-order checks, zoom/reflow tests) run in CI for web UIs.
- Accessibility semantics (motion, contrast, text scale, density, targets) are core-owned state or schema — not theme-owned. A theme consumes them; it never replaces them.
- Preference schemas carry an accessibility floor: `minimum` constraints that no value can go below.
- Automated checks are proxies; a real-browser 200% zoom check and manual spot checks remain required human gates for release.

## GOOD EXAMPLES

```json
{"targets": {"type": "enum", "values": ["standard", "large"], "default": "standard",
             "floor": "standard", "note": "standard = 44px minimum; large = 56px"}}
```

## ANTI-PATTERNS

- "We'll add accessibility after the design settles."
- An `aria-label` that says "button".
- Color-only status badges.
- Removing focus outlines for a cleaner look.
- A preference called "accessibility mode" that gates all accessibility behind an opt-in.

## ACCEPTANCE CHECKS

- Keyboard-only walkthrough of the main flows: pass?
- Every status has a text label: pass?
- 200% zoom without page-level horizontal scroll: pass?
- axe-class automated scan at serious/critical: zero?
- Do any preference combinations violate the floor? (Structurally impossible, not policy-promised.)