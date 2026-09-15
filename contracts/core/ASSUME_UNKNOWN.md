---
contract_id: assume-unknown
title: Assume UNKNOWN — Epistemic Humility Before Execution
version: 1.0.0
status: canonical
layer: core
applies: [humans, agents, engineering, design, operations, workflows]
triggers: [always, assumptions, interpretation, consequential-work, design-review]
rationale: Correct authority and accurate evidence can still produce a wrong interpretation. Make uncertainty cheap to admit, seek disconfirmation before commitment, and make confident mistakes cheap to recover from.
---

<!-- contract-receipt: lantern-thicket-opal -->

# Assume UNKNOWN — Epistemic Humility Before Execution

## Purpose

Assume UNKNOWN before assuming understood. Authority tells you where to look;
evidence tells you what you saw; neither guarantees understanding. Seek
disconfirmation before commitment, rather than waiting for a completed wrong
result to reveal an untested premise.

## NORMATIVE RULES

1. Begin with `UNKNOWN` for claims not yet established. Classify consequential
   claims as `OBSERVED` (directly supported by cited evidence), `INFERRED`
   (reasoned from observations), `ASSUMED` (treated as true without sufficient
   evidence), or `UNKNOWN` (not established). State the scope and source of an
   observation. An observed report establishes what was reported, not that its
   account of the underlying system is true. Never silently promote a claim
   because it is familiar, plausible, repeated, or confidently stated.
2. Separate `AUTHORITY` (who or what governs this decision and within what
   scope), `EVIDENCE` (what was actually inspected), `INTERPRETATION` (what you
   think it means, including alternatives), and `DECISION` (the action selected,
   rationale, reservations, and applicable authorization). None substitutes for
   the others. Correct authority plus accurate evidence can still be misunderstood.
3. Before consequential execution, identify the highest-impact unproven belief
   the plan depends on. Ask: **What would I expect to observe if my interpretation
   were wrong?** Name evidence that would make you revise or abandon the plan.
   Perform the cheapest reasonable disconfirmation check capable of challenging
   that belief before committing to the dependent action. Record what was
   checked, its result, its limits, and how it changed the decision. A check
   selected only to confirm the plan does not satisfy this rule.
4. If a reasonable check is unavailable or inconclusive, preserve `UNKNOWN`
   and the reservation. Stop the dependent consequential action, narrow the work
   to an authorized reversible investigation, or ask the participant who owns
   the missing answer using [Ask for Help](ASK_FOR_HELP.md). An unresolved belief
   must not become permission to proceed through repetition or elapsed time.
   Independent work may continue within its existing authorization.
5. Existing working implementation is evidence of behavior, not automatically
   intent or architecture. Treat inherited architecture as a hypothesis. For a
   redesign, compare the full relevant canonical design family and its structural
   implications against the inherited shell and explicit preservation decisions.
   Let canonical design inform frontend bones within the owner's scope; retain
   components when justified by current requirements, not merely because they
   exist. This is neither a blanket rewrite mandate nor permission to discard
   valid behavior, security, data, or accessibility contracts.
6. Failure to disconfirm is not proof of understanding. Record residual uncertainty
   and revisit the interpretation when new contradictory evidence, scope, or
   authority appears. Receipts, attestations, commitments, and green automated
   gates establish only what their checks cover; they do not certify comprehension.
7. `UNKNOWN`, reservations, and a safe stop are successful outcomes when
   understanding is insufficient. Make uncertainty cheap to admit without ridicule
   or penalty, and confident mistakes cheap to recover from: use bounded changes,
   checkpoints, and explicit recovery paths under
   [Recovery and Reversibility](RECOVERY_AND_REVERSIBILITY.md). Correct the belief
   and preserve the lesson rather than hiding the error or blaming a participant.
8. Scale the record and check to consequence. Reuse the existing task-impact,
   plan, decision, review, or handoff surface; a few clear lines can be enough.
   Do not require a new service, comprehension score, or ritual questionnaire.
   The check must precede the dependent execution, not be backfilled afterward.

## RATIONALE

The [Workshop v3 / V1-shell case study](../../docs/research/workshop-v3-v1-shell.md)
records a reported failure in which agents consulted the correct canonical Figma
authority and implemented screens while preserving an untested inherited shell.
Local fidelity did not establish architectural understanding. This contract adds
a pre-execution challenge to interpretation, complementing
[Truth and Evidence](TRUTH_AND_EVIDENCE.md) without replacing its evidence rules
or the independent [Authorization](../security/AUTHORIZATION.md) boundary.

## HUMAN EXAMPLES

- A migration owner identifies “all consumers accept the new field” as ASSUMED,
  runs a small compatibility probe, and discovers a strict reader before rollout.
- A designer and implementer compare navigation, content regions, and responsive
  composition across the approved family before deciding whether the old shell fits.
- “I found the right reference, but whether this structure preserves its intent is
  UNKNOWN. I can compare the shell composition before changing shared components.”

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Carry claim classifications and the four separate decision fields in existing
  artifacts when consequential; they are epistemic labels, not additions to the
  service-health status schema.
- Record the hypothesis, possible falsifier, performed check, result, limits,
  decision, and recovery path in the task-impact or linked decision record.
- Deterministic tooling can verify artifact presence, source identity, freshness,
  and execution receipts. It cannot prove that an interpretation is understood.
- Put `assume-unknown` in adoption manifests' `always` lists. The resolver does
  not automatically force every core contract into every consumer's adoption.

## GOOD EXAMPLES

```text
AUTHORITY: owner-approved design family governs frontend composition.
EVIDENCE: OBSERVED: the reference and current app both contain navigation.
INTERPRETATION: ASSUMED: the inherited shell should survive.
UNKNOWN: whether the design requires a different shared structure.
HIGHEST-IMPACT BELIEF: preserving the shell preserves design intent.
DISCONFIRMATION: compare the relevant family and preservation decisions;
  incompatible shared regions or responsive behavior would refute this plan.
RESULT: comparison found incompatible regions; no preservation decision found.
LIMIT: absence of a decision alone does not prove replacement is intended.
DECISION: stop shell-dependent implementation; document the structural mismatch
  and resolve intent with the owner. Independent API checks may continue.
RECOVERY: keep the current checkpoint and isolate any approved structural change.
```

## ANTI-PATTERNS

- “I read the canonical Figma file, therefore I understand the architecture.”
- “The shell works, so preserving it must be intended.”
- Checking only token colors when the risky belief concerns layout composition.
- “The tests pass” when none tests the interpretation at issue.
- Writing a disconfirmation record after the consequential work has shipped.
- Treating uncertainty as incompetence, or using it to demand repeated approval
  for facts that inexpensive authorized discovery can establish.

## ACCEPTANCE CHECKS

- Can a reviewer distinguish OBSERVED / INFERRED / ASSUMED / UNKNOWN claims?
- Are AUTHORITY / EVIDENCE / INTERPRETATION / DECISION separate and scoped?
- Before dependent execution, was the highest-impact unproven belief named,
  a possible falsifier specified, and a reasonable check actually performed?
- If unavailable or inconclusive, was the dependent action stopped or narrowed
  with UNKNOWN, a reservation, and an exact next investigation or question?
- Did inherited architecture earn its place against current requirements?
- Are check limits explicit, uncertainty safe to admit, and recovery practical?
