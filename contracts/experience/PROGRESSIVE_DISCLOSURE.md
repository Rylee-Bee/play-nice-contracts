---
contract_id: progressive-disclosure
title: Progressive Disclosure
version: 1.1.0
status: canonical
layer: experience
applies: [ui, product, docs]
triggers: [human-facing-work, information-design]
rationale: Present the smallest useful amount first, then permit deeper inspection. The mechanism that organizes complexity without removing it.
---

<!-- contract-receipt: glade-lagoon-tulip -->

# Progressive Disclosure

## Purpose

The presentation mechanism behind Complexity on Demand: the smallest useful amount of information first, then progressively deeper inspection on request.

## NORMATIVE RULES

1. The first view of any surface is comprehensible alone (Level 0/1 of the depth ladder).
2. Deeper information is one interaction away — a disclosure, drawer, detail route, or dedicated technical view.
3. Disclosure preserves context: the reader returns to where they were, expanded state is visible, and browser/navigation behavior is sane.
4. Prefer native mechanisms (`details`/`summary`, `dialog`, `popover`, anchor links) over invented ones; whatever is used must be fully keyboard- and screen-reader-accessible.
5. Never use disclosure to hide important truth from everyone: anything material to safety or ownership is visible by default; disclosure is for depth, not for secrets.
6. Summaries must not lie: a "3 warnings" summary must open to exactly three warnings.
7. Progressive disclosure is not pagination of essentials: don't spread one coherent task across five collapsed sections to look minimal.
8. Lead with human meaning. The first sentence tells the person what matters. Technical detail remains available afterward but does not precede the human understanding. Do not make ordinary use depend on understanding APIs, provider architecture, protocol vocabulary, internal enum names, database implementation, or backend topology. Use this order: what happened or what matters, what the person can do, what they need to know to do it safely, deeper explanation and implementation detail.

## RATIONALE

Attention economics (Attention and Focus) demand a small first view; honesty (Human Reliability) forbids hiding truth. Progressive disclosure is the reconciliation: organize entry into attention without deleting capability. Simplicity (Copy and Language rule 9) means reducing unnecessary wording; progressive disclosure means organizing necessary complexity. They are related but not identical.

## HUMAN EXAMPLES

- An inline "details" row on a log entry opens the full payload inline.
- "More from your world" on a dashboard opens a list without leaving the page.
- Documentation: quickstart first, full reference one link away.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- One consistent disclosure component library per surface; no ad-hoc show/hide divs.
- Deep-linkable disclosure state where practical (`#details-<id>`).
- Accessibility: disclosure controls are buttons with accessible names and expanded state (`aria-expanded`).

## GOOD EXAMPLES

```html
<details>
  <summary>Technical details (3 warnings)</summary>
  <!-- exactly three warnings -->
</details>
```

## ANTI-PATTERNS

- "Show more" that reveals yet another summary instead of the data.
- Essential form fields hidden behind "Advanced".
- A modal that must be dismissed to read what it summarizes.
- Custom show/hide widgets invisible to keyboards and screen readers.
- Collapsing everything so the page looks minimal while hiding what users need hourly.

## ACCEPTANCE CHECKS

- First view: understandable alone?
- Every summary: accurate to what it opens?
- Every disclosure: keyboard and screen-reader operable?
- Anything safety-relevant hidden behind a click? (Must be no.)