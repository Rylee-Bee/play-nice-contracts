---
contract_id: search-before-inventing
title: Search Before Inventing
version: 1.0.0
status: canonical
layer: engineering
applies: [architecture, project-management]
triggers: [always, new-subsystem, new-service, new-tool]
rationale: Before adding a subsystem, service, framework, database, agent, schema, cache, queue, workflow engine, or abstraction — inspect existing seams. Extending a coherent existing concept beats building a parallel one.
---

<!-- contract-receipt: beacon-wren-fathom -->

# Search Before Inventing

## Purpose

Prevent parallel-truth proliferation: before anything new is added, existing seams are found and extension is genuinely considered first.

## NORMATIVE RULES

1. Before adding any: subsystem, service, daemon, framework, database, agent, schema, cache, queue, workflow engine, or abstraction — inspect existing seams and answer: does something already own this responsibility?
2. Prefer extending a coherent existing concept to building a parallel one — even when the parallel one would be slightly cleaner in isolation.
3. Introducing a parallel concept requires a recorded reason: what was inspected, why extension was insufficient, what the boundary between the two concepts is.
4. Prefer small files, explicit schemas, boring APIs, deterministic logic, ordinary Git, and visible state. Do not introduce complexity merely because an agent can manage it.
5. Prefer the smallest mechanism that solves the demonstrated problem; promote to infrastructure only when repetition or risk justifies that cost.
6. Retire complexity when its operating burden exceeds its value; replacement by a smaller solution is a good outcome, not a defeat.
7. Where several good tasks compete, finish or park existing work before opening another lane (see Bounded Work).

## RATIONALE

The homelab's "view of the view" dashboard (a dashboard tracking other dashboards) is the canonical case: 70KB of infrastructure removed because the actual work already lived in the system it watched. Every system in this ecosystem that accreted parallel mechanisms eventually paid for them in maintenance, drift, and confusion about where truth lives.

## HUMAN EXAMPLES

- "We need job scheduling" → search finds an existing scheduler seam → extend it, rather than adding a second scheduler that 80% overlaps.
- "We need a status dashboard" → the existing status API already answers it → render it, rather than a new pipeline.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Architecture docs maintain a seam map: what concept owns what responsibility.
- PR/issue templates include "existing seams considered" for new-subsystem proposals.
- Deprecation is a supported path: retiring complexity is recorded as success, not loss.

## GOOD EXAMPLES

```markdown
## Proposal: add X
Existing seams: feature-Y (owns 80%), lib-Z (owns scheduling)
Decision: extend feature-Y with an adapter; no new service.
```

## ANTI-PATTERNS

- A second config system because the first "felt crufty".
- A queue next to a working scheduler "for scale" that never arrived.
- A new tool for what a documented 40-line script already did.
- Dashboards of dashboards.
- "It'll be cleaner to start fresh" without recording what was inspected.

## ACCEPTANCE CHECKS

- For each new thing added this cycle: which existing seam was inspected and why was extension insufficient?
- Is any new mechanism smaller than what it replaces or extends? (Should be yes, or justified.)
- Are any parallel truths accumulating?