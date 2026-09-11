---
contract_id: visual-fidelity-and-composition
title: Visual Fidelity and Composition
version: 1.0.0
status: canonical
layer: experience
applies: [ui, web, design, agents]
triggers: [ui-implementation, design-work, frontend, agent-ui-work]
rationale: Tokens can remain perfectly synchronized while the product still drifts dramatically from design intent. Composition — rhythm, hierarchy, grouping, density — is design truth too, and must be verified, not remembered. Anything important enough to preserve must have a deterministic gate, an explicit required human/browser gate, or both.
---

<!-- contract-receipt: vellum-fen-cedar -->

# Visual Fidelity and Composition

## Purpose

Close the gap between "the values are right" and "the design is right". A product may have perfect token fidelity and still substantially violate its design. Passing token checks MUST NOT be treated as proof of design fidelity.

Provenance note: this contract encodes a lesson first observed during a real frontend UAT (Personal World, September 2026): semantic design tokens survived implementation with mechanical verification, yet the shipped screens drifted dramatically from the intended Figma composition — screen rhythm, grouping, density, card-vs-list choices, hierarchy, whitespace, and companion placement. Token fidelity had a deterministic gate; composition fidelity had prose and human memory. Prose and memory are not gates. This contract generalizes that lesson; no project is a dependency of it.

## NORMATIVE RULES

### 1. Four kinds of design truth

2. Distinguish at all times:

   ```text
   SEMANTIC     — What does this thing mean?
   TOKEN        — What visual primitives does it use?
   COMPOSITION  — How are information, hierarchy, rhythm and space organized?
   BEHAVIOR     — How does it respond and interact?
   ```

3. Each kind has its own truth, its own verification, and its own drift. Semantic and token truth do not imply composition truth. Verification of one kind MUST NOT be reported as verification of another.

### 2. Composition is first-class design data

4. Composition includes: page structure, information hierarchy, grouping, relative prominence, whitespace, alignment, density, repetition, surface usage, card/list/table choices, visual rhythm, companion/artwork placement, navigation relationship, and responsive transformation.
5. Treat these as intentional decisions rather than incidental CSS. Composition decisions are written down — in screen specs, design references, or annotated baselines — not implied by whatever the implementation happened to produce.

### 3. Component gravity

6. Reusable component libraries create architectural and design gravity: if a generic component exists, humans and agents will reuse it even where inappropriate.
7. Shared design systems therefore define not only WHAT COMPONENT EXISTS but also WHERE IT IS APPROPRIATE and WHERE IT IS NOT. Example:

   ```text
   Card
   GOOD: standalone actionable item; discovery/feed content;
         truly bounded entity requiring separation
   BAD:  every status; every summary; every heading group;
         arbitrary page sections
   ```

8. Where misuse repeatedly causes drift, enforce usage through lint rules, wrapper APIs, tests, component ownership conventions, or architectural checks. Do not rely on prose alone when a recurring mistake can be mechanically prevented.

### 4. Design references must be easy to find

9. Every implementation surface has an obvious, current design reference, reachable by a deterministic mapping (e.g. `frontend/src/screens/TodayScreen.tsx` ← `design/screens/today.png` + `design/screens/today.md`), or another documented convention.
10. An implementer must not search several historical documents to determine which visual is current.

### 5. One current canonical pointer

11. Exactly one location answers: "What is the currently approved visual composition?" — e.g. `design/CURRENT.md`. It identifies:
    - the current approved design package;
    - its revision/date;
    - relevant screen references;
    - superseded visual packages (marked historical);
    - canonical tokens;
    - accessibility authority;
    - known intentional deviations.
12. Historical documents remain historical. Three partially-canonical documents competing is a defect: the pointer wins, and its superseded list explains why.

### 6. AI design implementation gate (hard workflow requirement)

13. For substantial user-facing UI implementation by an AI agent, BEFORE writing code:
    ```text
    1. Open the current design reference.
    2. Open the current running implementation.
    3. Compare them side by side.
    4. Record meaningful differences.
    5. Only then propose or delegate implementation.
    ```
14. The comparison covers: composition, hierarchy, density, typography, surfaces, proportions, personality, responsiveness, attention behavior. This is a hard workflow requirement, not a suggestion. "I read the design contract" without the comparison is not compliance.
15. For existing interfaces, the loop is:
    ```text
    DESIGN REFERENCE + LIVE BROWSER → DIFF/FINDINGS → IMPLEMENTATION → LIVE BROWSER → VERIFY
    ```
    Do not infer visual correctness exclusively from JSX/CSS source.
16. Where technically practical, place the reference artifact where the implementation agent is explicitly instructed to inspect it. Agent task briefs identify exact reference files:
    ```text
    Implementation:  frontend/src/screens/TodayScreen.tsx
    Visual reference: design/screens/today.png
    Behavior contract: contracts/experience/...
    Accessibility:    contracts/human/ACCESSIBILITY_FLOOR.md
    ```
    Reduce search ambiguity; a link several levels away is not sufficient.

### 7. Wrong vs right examples

17. Where a recurring design failure is known, preserve an explicit anti-pattern example: a `wrong/`/`right/` pair or a single annotated comparison board. Example:
    ```text
    WRONG: card-per-datum status dashboard
    RIGHT: heading + quiet divider + grouped list
    ```
18. Agents learn extremely effectively from concrete contrast. Do not rely only on statements such as "don't overuse cards" — show what replacing the anti-pattern actually looks like.

### 8. Visual regression

19. Where suitable: use Playwright (or equivalent), capture canonical viewport screenshots, store reviewed baselines, compare meaningful surfaces, and require intentional updates to baselines. Lightweight is fine; presence is required for surfaces with an approved composition.
20. Three verification layers, all necessary:
    ```text
    Token checks:       Did our primitives change?
    Visual regression:  Did the screen change?
    Human UAT:          Is the change actually good?
    ```
21. Visual regression does not replace human design review; it catches accidental compositional drift between accepted states.

### 9. Design verification levels

22. Encode and report design verification as levels; do not declare design verification complete because D0/D1 pass:
    ```text
    D0 — TOKENS:     colors, typography primitives, spacing values
    D1 — STRUCTURE:  correct semantic elements/components
    D2 — COMPOSITION: hierarchy, grouping, density, rhythm, proportion
    D3 — BEHAVIOR:   responsive, interactions, states
    D4 — EXPERIENCE: does the actual human experience match the intended product?
    ```
23. D2 and D4 require eyes: browser comparison and human acceptance respectively. D0 alone is never sufficient evidence of fidelity.

### 10. Visual contract attestation

24. When a task resolves this contract, its task-impact acknowledgement explicitly identifies:
    ```text
    design reference:
    live surface:
    known intended composition:
    known anti-patterns:
    verification method:
    ```
    Example:
    ```text
    VISUAL IMPACT
    reference: design/screens/today-rylee.png
    surface:   /today
    preserve:  greeting-area companion; plain grouped capability rows; quiet healthy state
    avoid:     card-per-datum; status-chip noise
    verify:    browser side-by-side; Playwright baseline; true 200% zoom
    ```
    This prevents "I read the design contract" from becoming meaningless boilerplate.

### 11. Composition must respect attention design

25. A composition is incorrect if it technically resembles a mockup but violates: quiet-when-healthy, What/Why/Next, obvious focus, progressive disclosure, interruption recovery, or complexity on demand.
26. Likewise, attention simplification must not erase the approved visual personality. Design fidelity is both visual and functional.

## RATIONALE

The observed failure mode: a token drift gate proved the primitives were synchronized while the shipped screens no longer resembled their design — because the gate measured the wrong layer. Composition drift is as real as token drift and far more insidious, since nothing red goes off when it happens. The fixes are structural: composition written down as data (specs, baselines), component misuse made mechanically preventable, one canonical pointer for what is current, a forced compare-before-code gate for AI implementers, and verification levels that name which layer was actually checked.

## HUMAN EXAMPLES

- An agent implementing TodayScreen opens `design/screens/today.png` and the live `/today` in a browser first, records "grouped list vs current card grid; companion missing from greeting area", then implements — and the PR's attestation shows the comparison happened.
- A visual-regression diff fails when a status page quietly becomes card-per-datum, before anyone internalizes the drift.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Screen reference mappings are deterministic and documented (screen → reference files).
- `design/CURRENT.md` (or equivalent) is a data file: package id, revision, screen list, superseded list, deviations.
- Component libraries encode usage guidance alongside definitions; lint/architectural rules exist for known recurring misuses.
- Visual regression baselines are reviewed artifacts; updates to baselines are explicit, intentional commits.
- Attestation schema accepts the VISUAL IMPACT block fields (reference, surface, preserve, avoid, verify).

## GOOD EXAMPLES

```text
D-verification report for /today:
D0 TOKENS: PASS (token-drift test green)
D1 STRUCTURE: PASS (landmarks, components correct)
D2 COMPOSITION: PASS (browser side-by-side vs design/screens/today.png; diff: none)
D3 BEHAVIOR: PASS (200% zoom reflow; reduced-motion off)
D4 EXPERIENCE: PASS (human UAT, Rylee 2026-09-12)
```

## ANTI-PATTERNS

- "Tokens all green" reported as "design verified".
- Composition decisions living only in a Figma file's arrangement and one person's memory.
- A Card component used for every status, summary, and section because it exists.
- Three design docs, each partially canonical, none authoritative.
- An agent implementing from the source code's existing habits without opening the reference.
- Baseline screenshots updated reflexively to make diffs go away.

## ACCEPTANCE CHECKS

- Can an implementer find the current approved composition of any screen in one lookup?
- Did any substantial UI task record a design-reference-vs-live comparison before coding?
- Are known recurring misuses mechanically prevented (lint/wrapper/test), not just proscribed?
- Is design verification reported by level (D0–D4), with D2/D4 honest about needing eyes?
- Does the attestation's VISUAL IMPACT name real files, real surfaces, and a real verification method?