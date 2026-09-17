---
contract_id: what-why-next
title: What / Why / Next
version: 1.0.0
status: canonical
layer: experience
applies: [ui, product, agents, notifications]
triggers: [human-facing-work, status-reporting, agents]
rationale: Important work should naturally answer what is happening, why it matters, and what can happen next. This is an information-design contract, not a demand for three labeled cards everywhere.
---

<!-- contract-receipt: timber-nectar-zenith -->

# What / Why / Next

## Purpose

Important states, events, and work items should naturally answer three questions:

```text
WHAT is happening?
WHY does it matter?
WHAT can happen next?
```

## NORMATIVE RULES

1. This is an information-design contract, not a layout: no page is required to render three literal labeled cards. The questions must simply be answerable from the surface.
2. WHAT: the primary fact, in the person's vocabulary (concepts, not vendor internals).
3. WHY: the consequence or stakes, when it is not obvious. Omit the why only when it is genuinely self-evident; never invent urgency.
4. NEXT: the next reasonable action or an explicit "nothing needed". An explicit no-action is a first-class answer.
5. The order is deliberate: state before explanation before action. Never lead with the CTA. Lead with human meaning before implementation detail (see Progressive Disclosure). Use the simplest clear language for the first layer (see Copy and Language).
6. Errors follow the same shape extended: what failed, why (if known), what still works, is anything unsafe, can it be retried, next action (see the error rules in Failure and Degradation).
7. Notifications and agent reports inherit this shape.

## RATIONALE

When a surface answers what/why/next, the reader can act without investigation, triage without panic, and stop without guilt. When it doesn't, every event becomes a research project — the reader must reconstruct context that the system already had.

## HUMAN EXAMPLES

```text
WHAT: Nightly backup finished with 1 warning.
WHY: One snapshot took 42 minutes (usually 3) — likely disk contention.
NEXT: Nothing required. See history if it repeats tomorrow.
```

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Event/attention payloads model `summary`, `impact`, and `next_action` fields (nullable — explicit null, never invented values).
- Attention-item APIs surface next actions as machine-usable references (links, command names).
- Agent truth reports end with a NEXT line; "nothing required" is representable.

## GOOD EXAMPLES

- A card: "Deploy #214 is waiting on your approval — it updates the public API. [Review diff] [Approve] [Reject]"

## ANTI-PATTERNS

- "Something happened!" with no what.
- A wall of telemetry with no consequence statement.
- Every item screaming "ACT NOW".
- A CTA with no statement of what the thing is.

## ACCEPTANCE CHECKS

- For each important state/event on this surface, can a reader answer what, why (or self-evidently skip it), and next?
- Is "nothing needed" expressible?
- Does the layout lead with state, not action?