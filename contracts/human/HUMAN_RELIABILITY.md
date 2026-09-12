---
contract_id: human-reliability
title: Human Reliability
version: 1.1.0
status: canonical
layer: human
applies: [ui, agents, operations, product]
triggers: [always, human-facing-work, workflows]
rationale: Systems must remain safe, understandable, and operable when the person using them is not at maximum attention, memory, or energy. Human reliability is architecture, not polish.
---

<!-- contract-receipt: willow-north-yarrow -->

# Human Reliability

## Purpose

The system must not require heroics. It should absorb and organize complexity rather than requiring the human to continuously hold it in working memory. It must be operable by a person at less than their best.

## NORMATIVE RULES

1. Do not require the operator to: remember undocumented state, maintain perfect concentration, notice subtle visual differences, infer whether an operation succeeded, repeatedly inspect healthy systems "just in case", or reconstruct why a decision was made.
2. Operator attention is finite. Treat unnecessary cognitive load as technical debt.
3. After an interruption, a person should be able to answer — without reconstructing the project: What is true? Is anything unsafe or urgent? What changed? What needs me? What can wait? What should I do next?
4. Prefer: visible state over remembered state; safe defaults over perfect recall; explicit uncertainty over false confidence; reversible actions over fragile ones; one obvious path over several equivalent paths; automation over repetitive vigilance; natural stopping points over endless continuation.
5. The calm, simple interface must never depend on hiding important truth.
6. Agent and automation work must model healthy collaboration: pursue the objective, surface discoveries, distinguish required work from optional improvements, avoid performative busywork, respect stop conditions, and make it easy to say "done for now". The human's contribution is negotiated, not assumed: the interface adapts when a person says not this way, not this much, not right now, show me less, or give me the recommendation — machinery carries the volume so the human carries only the judgment (see Mutual Contribution by Agreement).
7. An agent must not imply that the human is obligated to continue merely because more work is possible. A healthy stable system is allowed to remain unchanged. "No action needed" is a valid and desirable result.

## RATIONALE

Extracted nearly verbatim from Personal World's Human Reliability Contract, which had itself been extracted from agent policy after the same rules were restated too many times. A system that only works when its operator is at their best fails precisely when it is needed most.

## HUMAN EXAMPLES

- Returning after a week away, the first screen answers "what needs me?" before anything else.
- A long task leaves a note about what it did and what remains, so nobody has to re-derive it.
- The assistant says "That's done. If you want, there's also X — but nothing needs you today."

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Important context belongs in the environment (files, state, handoffs), not in conversation memory.
- Systems support resumption: session state, handoff documents, "where was I?" views.
- Agents emit final truth reports: CURRENT / CHANGED / VERIFIED / CONTRACTS / UNKNOWN / DEFERRED / NEXT.
- Stop conditions are defined before work begins.

## GOOD EXAMPLES

```text
5 unresolved → 3 → 1 → done.  (closure is visible and rewarded)
degraded → repaired → verified.
NEXT: nothing required.
```

## ANTI-PATTERNS

- Infinitely long checklists presented with equal urgency.
- A status page that requires cross-referencing five screens to know if anything is wrong.
- An agent that always finds "one more important thing".
- Interfaces that punish leaving and returning.
- Success that can only be confirmed by remembering what it looked like before.

## ACCEPTANCE CHECKS

- Can a tired person operate this correctly?
- Is anything critical dependent on someone's working memory?
- Is "no action needed" representable and respected?
- Can a returning user find "what needs me?" in under a minute?