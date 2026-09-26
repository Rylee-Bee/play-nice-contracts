---
contract_id: themes-and-personalization
title: Themes and Personalization
version: 2.0.0
status: canonical
layer: people
applies: [ui, web, product, sites]
triggers: [theme, themes, dark mode, light mode, appearance, customization, personalization, theme preferences, branding, accent, skin, styling]
rationale: People make the product theirs without customization eroding accessibility, coherence or meaning.
---

<!-- contract-receipt: ochre-fabric-mill -->

# Themes and Personalization

## In short

Let people make it theirs. One stack decides who wins: the floor, then packs,
then project, then personal preferences, then theme. Nothing lower breaks what
is above.

## Applies when

- You ship themes, dark mode, skins, or user preference/settings systems.
- Not this contract's job: what the floor itself requires (see accessibility);
  how loud motion or sound is (see sensory-safety).

## Rules

1. **One authority stack.** Floor → pack rules → project decisions → personal
   preferences → theme. Each lower layer may adjust; no layer may break a
   requirement above it.
2. **Every theme ships on the floor.** Each theme is verified against the
   accessibility contract — proven, not promised.
3. **Comfort has a lane.** Density, contrast (within the floor's band),
   larger targets, text scale, motion and accents: adjustable within the
   floor, never below it.
4. **No "accessibility mode".** Preferences tune an already-accessible
   product; no switch turns accessibility on or off.
5. **Decoration stays decoration.** Personality, companions and mascots carry
   no operational meaning; companion art is `aria-hidden`, and the real
   control keeps its own useful label.
6. **Themes leave cleanly.** Switching a theme off, or removing it, loses no
   function, state or information.
7. **Core owns semantics.** Accessibility properties (motion, contrast, text
   scale, target size) belong to core or project state; themes consume them
   and never own or rewrite them.
8. **Presentation only.** A theme never changes the information architecture,
   navigation, DOM semantics or reading order.
9. **Preferences belong to the person.** Personal preferences are exportable
   and portable, and never silently imposed on other users of the same system
   (see the floor, rule 16).
10. **The floor is structural.** Preference schemas carry minimum values and
    are validated server-side, so a combination that breaks the floor cannot
    be stored at all — not merely warned against.

## Examples

- A dark, low-glare default and a high-contrast comfort mode with added
  borders; both pass the floor.
- A companion character switched off in settings with zero loss of function.
- Not: a "cute" theme that drops contrast below the floor; a mascot whose
  expression is the only health signal; one user's theme becoming everyone's
  default.

## Why

Customization that fights the floor forces a cruel choice, and customization
without layering fights itself. One stack lets a thousand comfortable
experiences sit on a single coherent, accessible product — and gives every
"who wins?" argument one plain answer.

## You're done when

- Turning every personalization off leaves the product fully functional and
  fully accessible.
- No theme plus preference combination can break the floor — tested, not
  asserted.
- No decoration carries operational meaning.
- The stack in rule 1 is the only one; docs and code use it, and no competing
  layer list exists.

## Machine notes

- Preference schema:
  `{"targets": {"values": ["standard", "large"], "default": "standard",
  "floor": "standard"}}`.
- Theme manifests declare the slots they fill; unknown slots are rejected.
