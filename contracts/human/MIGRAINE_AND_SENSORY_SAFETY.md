---
contract_id: migraine-and-sensory-safety
title: Migraine and Sensory Safety
version: 1.0.0
status: canonical
layer: human
applies: [ui, web, design]
triggers: [ui-work, visual-design, animation]
rationale: Interfaces should be pleasant for people sensitive to visual and motion load. These are engineering requirements, stated without any personal medical history: restrained luminance, no strobing, no required motion.
---

<!-- contract-receipt: fathom-opal-zenith -->

# Migraine and Sensory Safety

## Purpose

Design interfaces that remain usable for people sensitive to visual and motion load: low glare, restrained motion, no surprise flashes. These requirements are stated purely as engineering requirements; the medical reasons behind them belong to no repository.

## NORMATIVE RULES

1. No flashing or strobing content. No rapid luminance oscillation, ever.
2. No enormous pure-white canvases by default; no neon visual language; no required bright saturated accents. Long-session comfort is the default target.
3. Default loading indicators are static. No shimmer, no pulsing skeletons, no breathing glows.
4. No continuous decorative rotation or ambient motion by default. Peripheral movement is restrained.
5. Transitions are short and gentle (sub-300ms, ease-out class) and gated behind no-preference; motion defaults to reduced.
6. `prefers-reduced-motion: reduce` is honored unconditionally and suppresses all nonessential motion, overriding any application preference.
7. Every animated or motion-carried meaning has a static alternative. Animation never carries essential meaning.
8. Success does not require fireworks: completion feedback can be a quiet, static confirmation.
9. Where a documented relationship exists between specific hues and visual discomfort (e.g. high-glare blue range), palettes may demote those hues as a comfort decision — while never dropping below contrast minimums.

## RATIONALE

Sensory-safe design is simply good long-session design. The requirements stand on their own as engineering: nobody's visual cortex enjoys strobing skeletons at 2 AM. The personal reasons that originally motivated them are private and stay out of the library.

## HUMAN EXAMPLES

- A page that loads with a static "Loading…" indicator, not a shimmering skeleton.
- A "save succeeded" confirmation that appears quietly as text, without confetti.
- An interface that can be used for hours in a dim room without glare discomfort.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- A motion preference vocabulary with a floor of `reduced` (or stricter), where OS-level reduced-motion always overrides.
- Static fallbacks exist for every animated affordance and are the default rendering.
- CSS transitions are gated behind `prefers-reduced-motion: no-preference` in addition to application preference.
- CI-able checks: no `animation`/`transition` outside gated classes; luminance budget checks on large surfaces.

## GOOD EXAMPLES

```css
@media (prefers-reduced-motion: no-preference) {
  .card { transition: transform 160ms ease-out; }
}
/* otherwise: no transition; state changes are instant and static */
```

## ANTI-PATTERNS

- A skeleton-pulse loader as the default.
- Rotating decorative gears, bouncing mascots, or ambient breathing glows.
- Meaning revealed only by animation ("watch the arrow to see the order").
- Pure white `#FFFFFF` full-bleed background with no low-glare alternative.
- Strobing "urgent!" attention-grabbers.

## ACCEPTANCE CHECKS

- With OS reduced-motion on: is every interaction fully usable and meaningful, with zero nonessential motion?
- Is every default loading state static?
- Does any meaning depend on motion or animation?
- Could someone use this interface for three hours in a dim room comfortably?