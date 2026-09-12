---
contract_id: play-nice-together
title: Play Nice Together
version: 1.2.0
status: canonical
layer: core
applies: [architecture, everything]
triggers: [always, new-interface, new-subsystem, design-review]
rationale: The constitution of this library: everything should play nicely with everything else — humans, bots, services, APIs, CLIs, UIs, assistive technologies, and future tools. A good system does not demand the world adapt to it.
---

<!-- contract-receipt: glade-thicket-compass -->

# Play Nice Together

## Purpose

This is the founding contract. Every other contract in this library is a specific working-out of one idea:

> **Everything should play nicely with everything else.**

A good system should be understandable by a human, operable by automation, inspectable by an agent, interoperable with other tools, accessible to people with different needs, recoverable after failure, and replaceable without destroying the truth it manages.

## NORMATIVE RULES

1. Design every layer so it can play nicely with the layers around it. Consider the next participant — human, bot, program, service, or session — in every decision.
2. Do not intentionally make one interface first-class while leaving all others as undocumented hacks. If a capability exists through several surfaces (CLI, API, web, agent tool, automation), those are views of the same capability: they converge on common state, vocabulary, and policy.
3. Where practical, expose: understandable state, documented interfaces, machine-readable output, human-readable output, discoverable capabilities, explicit versions, stable identifiers, useful errors, safe defaults, clear side effects, verification, recovery, import/export, and provenance.
4. Do not demand that the world adapt to the tool. Expose understandable capabilities; respect other systems' contracts; preserve human ownership; fail honestly; leave evidence for whatever comes next.
5. Humans are part of the system. Bots are part of the system. Failure is part of the system. Interruption is part of the system. Replacement is part of the system. The next maintainer is part of the system. Design for all of them.
6. Do not rely on invisible institutional knowledge: if understanding requires having been there, the design is unfinished.
7. When two systems must interact, follow the Friend rules: learn the other system's documented contracts before acting; respect its limits; read before writing; leave it as you found it or better.
8. A good participant knows when to act, when to discover, when to ask, and when to preserve uncertainty. Asking another participant for information they naturally own is often more interoperable than building machinery to infer it; every well-formed question is an opportunity to reduce friction at the boundary between systems (see Ask for Help).
9. A friendly participant does not merely say "I agree." It also offers the useful information that makes future cooperation easier — capabilities, interfaces, references, limits — and a friendly project remembers that information so the participant does not have to explain itself again next session. Mutual courtesy is encoded as durable, structured project context (see Project Context and Participant Packs).

## RATIONALE

Systems that treat humans, machines, and each other as hostile strangers become brittle, hostile, and lonely. Systems designed for mutual legibility compound in value: each participant can verify the others, and none becomes a bottleneck. This principle survived every stack transition observed across this ecosystem. Asking for help belongs here too: a system that can formulate a good question is easier to integrate, and one that can answer is easier to use — every well-formed question reduces friction at the boundary between participants. And remembering what collaboration partners have told us belongs here as much as remembering the rules: mutual courtesy encoded as architecture is what lets the ecosystem get easier to join every time a new participant arrives.

## HUMAN EXAMPLES

- A CLI, a web page, and an agent tool that all answer "is the deploy healthy?" the same way.
- A config file a human can read, a script can parse, and a future tool can extend — with a comment that says which one wins.
- An error message that says what failed, what still works, and what to try next.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Capability definitions exist once; surfaces render them.
- Shared vocabulary modules (status, error identifiers) are imported, not reimplemented.
- Machine-readable and human-readable outputs are both generated from the same source of truth.
- Interface parity is testable: one definition of "what does this operation do" governs all surfaces.

## GOOD EXAMPLES

```text
Service seems okay :)                     ← bad: unverifiable, unparseable
{"status": "healthy", "observed_at": ...}  ← good machine state
"Everything looks good."                   ← good human rendering of the same state
```

## ANTI-PATTERNS

- A perfect web UI over an undocumented, unusable CLI.
- An API that only the original frontend author understands.
- Errors like "Something went wrong."
- A system whose only recovery instructions are "ask the person who built it."
- Treating accessibility, observability, or portability as someone else's job.

## ACCEPTANCE CHECKS

- Can the next participant (human, bot, program, session) understand where it stands?
- Is any surface a second-class citizen by omission rather than by explicit decision?
- Would this design survive its UI framework, its AI provider, and its primary author being replaced?
- Does this layer make the layers around it easier, or does it demand adaptation?