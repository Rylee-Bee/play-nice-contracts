# Working with Figma

How we work effectively with this participant.

## Best uses

- approved composition
- visual hierarchy
- spacing and proportions
- design tokens
- assets and exports
- frame references

## Before asking Figma

Check:

- the current design pointer (`.project/design/CURRENT.md`)
- existing exports under `.project/design/exports/`
- project design docs

Figma is reachable via MCP and browser; use the lightest interface that
answers the question. Questions use `play-nice/question-v1`.

## When implementing

Open:

- the current Figma/export reference
- the live browser implementation

Compare them side by side BEFORE modifying code (see the
`visual-fidelity-and-composition` contract). Extract tokens and geometry —
never eyeball.

## Do not assume

- token fidelity proves composition fidelity
- old exports are still canonical (check CURRENT.md)
- Figma visual intent overrides accessibility requirements
  (the accessibility floor outranks pixel matching)

## What the project offers back

- canonical visual source: figma (design stage)
- accessibility contract: accessibility-floor — never negotiable
- composition anti-patterns to avoid: card-per-datum; unnecessary status chrome
- implementation: web frontend
- verification: browser comparison required; screenshot regression on
  meaningful surfaces