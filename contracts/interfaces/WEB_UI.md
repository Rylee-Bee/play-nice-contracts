---
contract_id: web-ui
title: Web UI
version: 1.0.0
status: canonical
layer: interfaces
applies: [ui, web]
triggers: [ui-work, frontend]
rationale: The web UI is another view of the same system: same capabilities, same vocabulary, same truth. It renders the API's state honestly, never invents data, and never becomes the only way to operate the product.
---

<!-- contract-receipt: thicket-willow-rill -->

# Web UI

## Purpose

Make the web interface a friendly view of the same system the CLI and API expose — honest about state, accessible by default, and never a load-bearing single point of operation.

## NORMATIVE RULES

1. The UI is a view, never the source of truth: it renders API/CLI-shared state; it holds no truth of its own. Nothing on screen is fabricated — every displayed value comes from a real response field, or is explicitly labeled as unknown/loading.
2. Every concept operable in the UI is understandable and operable without it (see CLI parity). The UI may make workflows easier and more discoverable; it must never become the only way to understand or operate the system.
3. The UI renders canonical states only: the shared status vocabulary, real data, honest empty states ("No journal entries yet" — not fake data, not blank mystery), and explicit loading/error states per section (see Explicit State, Failure and Degradation).
4. A failing section degrades alone: one broken widget never blanks the page; per-section states are independent.
5. Accessibility floor applies fully (see Accessibility Floor and its sibling human contracts): keyboard, focus, targets, labels, zoom/reflow, reduced motion.
6. The UI respects the depth ladder: glanceable defaults, drill-down to technical detail, specialist hand-off links at the bottom of the hierarchy (see Complexity on Demand).
7. Presentation preferences (theme, density, motion) come from core-owned preference state/schemas — never from the theme alone (see Themes and Personalization).
8. Design truth follows the design contracts (see Design Source and Fidelity, Visual Fidelity and Composition): semantic tokens, verified composition, no hand-invented values.
9. No external network requests at runtime for assets that could be self-hosted; a deployed UI works offline in its own network.

## RATIONALE

Every system here that treated the UI as "the product" and the CLI/API as plumbing became fragile: UI rewrites became rewrites of the product, and UI-only state drifted from real state. UI-as-view proved cheaper to maintain, test, and replace — and it keeps agents, scripts, and tired humans equally first-class.

## HUMAN EXAMPLES

- The dashboard shows `not_configured` for a capability nobody wired up — an honest vacancy, styled calmly, with a "set up" action.
- A legacy HTML dashboard is deleted in one commit after parity is proven, because the API beneath never depended on it.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- UI state derives from the same endpoints/schemas the CLI uses; typed clients shared.
- Component libraries render from capability manifests and status vocabulary, not hard-coded provider lists.
- Automated browser checks (axe-class, target size, reflow proxies) run in CI; real-browser gates stay human.
- Fabricated-data tests: fail on any hardcoded demo content that pretends to be real.

## GOOD EXAMPLES

```json
// API says: {"status": "not_configured"} → UI renders the word + setup action
// UI never invents {"status": "healthy"} to look complete
```

## ANTI-PATTERNS

- Demo data left in production screens.
- A UI-only status notion ("kinda broken") absent from the vocabulary.
- Operation possible only by clicking through five screens.
- One failed fetch rendering the whole app blank.
- The UI as the sole recovery path for a broken deployment.

## ACCEPTANCE CHECKS

- Does every displayed value trace to a real response field?
- Is every screen usable at the accessibility floor?
- Could the UI be deleted and rebuilt from the API without losing operability?
- Do sections fail independently?