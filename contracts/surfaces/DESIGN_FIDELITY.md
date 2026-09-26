---
contract_id: design-fidelity
title: Design Fidelity
version: 2.0.0
status: canonical
layer: surfaces
applies: [ui, web, agents]
triggers: [design, ui design, visual design, figma, mockup, design tokens, composition, screen reference]
rationale: The approved design is data in the repo, checked layer by layer, so what ships matches what was decided — with no design tool required.
---

<!-- contract-receipt: quarry-birch-gorse -->

# Design Fidelity

## In short

Design truth lives in repo files: semantic tokens, written-down
compositions, one current pointer. Passing one layer's check is never
reported as checking another. Compare with the live screen, not memory.

## Applies when

You create or change a visual design, or implement a screen from an
approved design. Not this contract's job: wording (plain-language) or the
accessibility minimums themselves (People pack).

## Rules

1. Design truth is repo-native and portable: token files, screen
   references, and one "what is current" pointer. A design tool's
   internals or a vendor's API shape never hold it; tool representations
   are generated from the repo, and a drift gate checks them. (MUST)
2. Token names say what they mean (`status.needs_attention`,
   `focus.ring`), not `Figma Variable 3348`; color literals appear only
   in the token-derived layer. (MUST)
3. Anyone can clone the repo and implement or change the design without
   opening a design tool. (MUST)
4. When a visual source (e.g. Figma) is the approved truth for a stage:
   extract the values, never eyeball them; keep file and frame ids
   beside the work as history, not dependency. (MUST)
5. Accessibility outranks pixels: where the design fights the
   accessibility floor, the floor wins and the conflict is recorded back
   to the design. Accessibility semantics are core-owned; a design tool
   implements them, never owns them. (MUST)
6. Meaning, tokens, composition, and behavior are four kinds of design
   truth, each with its own check; passing one is never reported as
   passing another. "Tokens green" is not "design verified". (MUST)
7. Composition is written-down data, not memory: hierarchy, grouping,
   density, rhythm, and card-or-list choices are captured in screen
   specs or annotated baselines, and each screen's current approved
   reference is found in one lookup. Historical documents stay
   historical. (MUST)
8. Before writing substantial UI, open the current reference and the
   live implementation side by side and record the meaningful
   differences; after, verify in a real browser, not from source code.
   (MUST)
9. Component libraries define where each component belongs, not just
   that it exists. Where a misuse keeps recurring, gate it with a lint,
   test, or wrapper instead of another paragraph of prose. (SHOULD)
10. Show a wrong/right pair for every known recurring design failure; a
    concrete contrast teaches better than a rule alone. (SHOULD)
11. Keep reviewed visual-regression baselines for screens with an
    approved composition, and update a baseline only on purpose.
    Regression catches drift; people still decide whether a change is
    good. (SHOULD)
12. Report design verification by level: D0 tokens, D1 structure, D2
    composition, D3 behavior, D4 experience. D0 alone never proves
    fidelity; D2 and D4 need eyes. (MUST)
13. A screen that matches the mockup but breaks the calm defaults —
    quiet when healthy, obvious focus, depth on demand — failed the
    design; simplifying for attention never erases the approved
    personality either. (MUST)

## Examples

- Good: an agent opens `design/screens/today.png` and the live `/today`,
  records "grouped list vs current card grid; companion missing", then
  codes, then re-checks in the browser.
- Bad: "just match the screenshot" with no extraction; a Card wrapping
  every status and section because a Card exists; three partially-current
  design docs with no pointer.

## Why

Tokens can stay perfectly synchronized while the product drifts far from
its design, because a token gate checks the wrong layer. Writing
composition down and checking it layer by layer gives drift somewhere to
be caught before it ships.

## You're done when

- One lookup answers "what is the current approved composition for this
  screen".
- Every substantial UI change has a reference-vs-live comparison on
  record, before and after coding.
- Verification is reported by D-level, with D2 and D4 honestly naming
  whose eyes checked.
- A new contributor can change the design with zero design-tool access.
