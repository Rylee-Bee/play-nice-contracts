---
contract_id: themes-and-personalization
title: Themes and Personalization
version: 1.0.0
status: canonical
layer: experience
applies: [ui, web, product]
triggers: [ui-work, theming, preferences]
rationale: Allow customization without destroying product coherence or accessibility. Layering keeps user comfort, themes, and decoration from fighting the floors beneath them.
---

<!-- contract-receipt: cinder-opal-window -->

# Themes and Personalization

## Purpose

Let people make the product theirs — personality, accent, density, contrast, motion, companions — without letting customization erode accessibility, coherence, or meaning.

## NORMATIVE RULES

1. Personalization is layered; a lower layer may never violate a requirement above it:
   ```text
   PLATFORM / ASSISTIVE REQUIREMENT
           ↓
   ACCESSIBILITY FLOOR
           ↓
   USER COMFORT
           ↓
   THEME / PERSONALITY
           ↓
   DECORATION
   ```
2. A theme must not break accessibility: every theme ships against the same floor, verified.
3. Comfort settings may adjust density, contrast (within floor+band), target sizing (upward), text scaling, and motion (within floor) — never below the floor.
4. Themes may affect: personality, companion presence, accent, iconography, aesthetic tone. Decoration is decoration: personality never carries operational meaning (a mascot is never a status indicator).
5. Themes are switchable and removable: turning a theme off loses no functionality. Companion art is decorative and `aria-hidden`; the actionable control keeps its own useful label.
6. Theme and comfort preferences are user-owned state: exportable, portable (see Portability), and never silently imposed on other users of the same system.
7. A coherent product remains coherent: themes alter presentation slots defined by the core; they do not reorder information architecture or invent new navigation concepts.
8. No value combination in any preference schema may violate the floor — structurally validated, not policy-promised.

## RATIONALE

Personalization that fights accessibility forces a cruel choice; personalization without layering fights itself. The layering pyramid (distilled from Personal World's accessibility contract and preference schema) lets a thousand users have a thousand comfortable, accessible experiences over one coherent product.

## HUMAN EXAMPLES

- A dark, low-glare default; a high-contrast comfort mode with added borders; both pass AA.
- A companion character that can be turned off with zero functional loss.
- Dense layout for the expert, relaxed layout for the tired evening — same product, same meaning.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Preference schemas encode floors (`minimum` constraints) and are validated server-side; the client cannot submit floor-violating combinations.
- Theme manifests declare the slots they may fill; unknown slots are rejected.
- Accessibility semantics (motion, contrast, text scale, targets) are core-owned state or schema — themes consume, never own.
- Theme application never changes DOM semantics or source order.

## GOOD EXAMPLES

```json
{"motion": {"values": ["off", "reduced", "subtle"], "default": "reduced", "floor": "off"},
 "targets": {"values": ["standard", "large"], "default": "standard", "floor": "standard"}}
```

## ANTI-PATTERNS

- A "cute" theme that reduces contrast below AA.
- A mascot whose expression is the only signal for system health.
- Preferences that only the client enforces.
- A theme that reorders the DOM for looks, breaking screen-reader order.
- One user's theme becoming every user's default.

## ACCEPTANCE CHECKS

- Are all floor constraints validated server-side against every theme and preference combination?
- Does turning every personalization off yield a fully functional, fully accessible product?
- Does any decoration carry operational meaning? (Must be no.)