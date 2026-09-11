---
contract_id: design-source-and-fidelity
title: Design Source and Fidelity
version: 1.0.0
status: canonical
layer: experience
applies: [design, ui, web]
triggers: [design-work, figma, tokens, ui-work]
rationale: Design tools are replaceable machinery. Semantic tokens and repo-native artifacts are the durable design truth; tool output is derived. When implementing from a visual design source, extract truth — never guess it.
---

<!-- contract-receipt: heather-ledger-juniper -->

# Design Source and Fidelity

## Purpose

Make design decisions produce artifacts useful to designers, frontend engineers, agents, tests, and future tools — and make implementation faithful to design intent without either side becoming a dependency of the other.

## NORMATIVE RULES

1. Canonical design truth lives in repo-native, portable formats: semantic tokens (`design/tokens.json`-class files), documented contracts, and implemented reference behavior. Never in a `.fig` file, a Figma project ID, a tool's internal variable store, or any vendor's API shape.
2. Tokens are semantic, not tool-internal:
   ```text
   surface.canvas  text.primary  status.needs_attention  focus.ring
   ```
   — not `Figma Variable 3348`. Generated tool representations (Figma variables, CSS custom properties) are derived artifacts, drift-checkable against the source.
3. Accessibility semantics (motion, contrast, text scale, density, targets) are core-owned. A design tool implements them; it does not own them.
4. When a visual design source (e.g. Figma) is the approved source of truth for a design stage:
   - inspect it; extract values (tokens, geometry, type) rather than guessing or eyeballing;
   - preserve design provenance where useful (frame/file IDs in handoffs make changes traceable);
   - compare implementation against the actual composition, honoring hierarchy and intent — not merely copying colors.
5. Accessibility outranks literal pixel matching. The accessibility floor is never negotiable for fidelity; when design and floor conflict, the floor wins and the conflict is recorded back to design.
6. A contributor must be able to clone the repo, inspect design contracts and tokens, and implement or redesign without any design tool.
7. Design handoffs name one authoritative source per decision; summaries route, they do not govern.

## RATIONALE

The "invented pastels" class of bug — themes that drifted because someone eyeballed a color instead of extracting it — and the "can't modify the UI without a Figma workspace" class of lock-in both come from the same root: design truth living in the wrong place. Tokens-as-contract fixes both and lets agents and tests verify fidelity mechanically.

## HUMAN EXAMPLES

- An engineer opens `design/tokens.json`, finds `status.needs_attention`, and knows its color, contrast band, and meaning — no Figma account required.
- A theme regression test fails when a hand-edited color diverges from tokens.
- A designer's frame ID lives beside the implemented component for traceability, while the component itself depends only on tokens.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- A generation step (`tokens.json` → derived CSS/tool representation) plus a `--check` drift gate in CI.
- No color literals outside the token-derived layer (enforceable by lint/test).
- Handoff documents cite frame/file IDs for provenance without making them load-bearing.

## GOOD EXAMPLES

```text
design/tokens.json (canonical, semantic)
  → gen → tokens.css (only file where hex may appear)
  → gen → Figma variables (derived, replaceable)
```

## ANTI-PATTERNS

- Hard-coded hex values scattered through components.
- Code tokens generated FROM Figma instead of TO it.
- "Just match the screenshot" implementations without extraction.
- A design system that requires a specific tool to change a spacing value.
- Pixel-perfect clones of an inaccessible design.

## ACCEPTANCE CHECKS

- Can a new contributor implement the design with zero design-tool access?
- Does the drift gate fail on token divergence?
- Are token names semantic and stable across themes?
- Did any implementation value come from eyeballing rather than extraction? (Must be no.)