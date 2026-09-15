# Play-Nice Quick Reference

> **This is a reminder, not an attestation substitute and not a contract.**
> Every item below links to its canonical source. When in doubt, read the
> contract. This document is non-normative.

---

## Core principles (from [Trusted Translation](principles/trusted-translation.md))

1. Preserve participant-specific authority —
   [Portability and Ownership](../contracts/core/PORTABILITY_AND_OWNERSHIP.md),
   [Authorization](../contracts/security/AUTHORIZATION.md)
2. Translate intent without silently changing meaning —
   [Stable Truth, Replaceable Machinery](../contracts/core/STABLE_TRUTH_REPLACEABLE_MACHINERY.md)
3. Preserve provenance across translations —
   [Provenance and Audit](../contracts/core/PROVENANCE_AND_AUDIT.md)
4. Distinguish fact, inference, and UNKNOWN —
   [Truth and Evidence](../contracts/core/TRUTH_AND_EVIDENCE.md)
5. Translation ≠ authorization —
   [Authorization](../contracts/security/AUTHORIZATION.md)
6. Prefer interoperability over forced uniformity —
   [Play Nice Together](../contracts/core/PLAY_NICE_TOGETHER.md)
7. Keep underlying native interfaces inspectable —
   [Human and Machine Parity](../contracts/interfaces/HUMAN_AND_MACHINE_PARITY.md)
8. Make failures recoverable —
   [Recovery and Reversibility](../contracts/core/RECOVERY_AND_REVERSIBILITY.md)
9. Trust coordinators based on evidence and behavior, not position —
   [Collaborative Good Faith](../contracts/core/COLLABORATIVE_GOOD_FAITH.md)
10. Keep inspiration non-normative; canonical contracts remain authoritative

## Before consequential execution

[Assume UNKNOWN](../contracts/core/ASSUME_UNKNOWN.md): classify OBSERVED / INFERRED /
ASSUMED / UNKNOWN; separate AUTHORITY / EVIDENCE / INTERPRETATION / DECISION. Name
the highest-impact unproven belief, specify what would contradict it, and perform
the cheapest reasonable check before the dependent action. Record result, limits,
reservations, decision, and recovery. An inconclusive check leaves UNKNOWN.

## Evidence grades ([Testing and Verification](../contracts/engineering/TESTING_AND_VERIFICATION.md))

```text
SOURCE INSPECTED
UNIT TESTED
INTEGRATION TESTED
CONTAINER TESTED
CI TESTED
DEPLOYED
RUNTIME VERIFIED
BROWSER VERIFIED
HUMAN ACCEPTED
```

Never silently upgrade one grade to another. State the exact command that
produced the evidence.

## Stop states ([Bounded Work](../contracts/engineering/BOUNDED_WORK.md))

These are success, not failure:

```text
objective complete
diminishing returns
human decision required
evidence insufficient
authoritative sources conflict
next action materially increases risk
verification impossible
```

`DEFERRED` with a reason is a first-class recorded state.

## UNKNOWN ([Truth and Evidence](../contracts/core/TRUTH_AND_EVIDENCE.md))

`UNKNOWN` is a valid state. Never silently convert it into `healthy`,
`PASS`, or `complete`. Failure to prove something is not evidence of its
opposite.

## Ask, don't guess ([Ask for Help](../contracts/core/ASK_FOR_HELP.md))

```text
KNOW                        → act
CAN SAFELY DISCOVER         → discover
ANOTHER PARTICIPANT CAN
ANSWER CHEAPLY              → ask
HIGH-COST / HIGH-RISK /
AMBIGUOUS                   → ask or escalate
UNKNOWN AND NOBODY CAN
ANSWER                      → preserve UNKNOWN
```

`WAITING_FOR_HELP` is a successful stop state. Questions are resumable
state, not chat messages.

## Capability ≠ authority ([Authorization](../contracts/security/AUTHORIZATION.md))

Keep distinct at all times:

```text
capability    participation    agreement    authorization    acceptance
```

Being able to do something does not mean you are permitted to do it.
Ambiguous authorization fails closed.

## Consequential decisions

Remain with the applicable owner (usually the human). A coordinator
routes and verifies; it does not decide the consequential parts.

## No model castes ([Participation and Contribution](../contracts/core/PARTICIPATION_AND_CONTRIBUTION.md))

Authority comes from role, evidence, contracts, ownership, and
verification — never from model size, price, or provenance. Route
according to capability, not prestige.

## Worker ≠ integration ([Review and Integration](../contracts/agents/REVIEW_AND_INTEGRATION.md))

Worker-green is not integration-green. The combined state is tested
after merge at the integration SHA.
