# Play-Nice Harness Evidence Ledger

**Status: EXPERIMENTAL**

This ledger turns observations into testable harness hypotheses. Do not promote attractive wording without evidence.

## Confidence vocabulary

- **SEED** — plausible hypothesis; evidence collection has begun.
- **SUPPORTED** — repeated evidence, but transfer/counterexample work remains.
- **STRONG** — repeated cross-domain/cross-participant evidence with counterexample testing.
- **REJECTED** — evidence does not support a universal law; retain the lesson and reason.
- **ADAPTER** — useful behavior, but evidence suggests it is role/model/domain specific.

## Candidate ledger

| ID | Candidate | Initial evidence / motivation | Counterexample question | Transfer target | Confidence |
|---|---|---|---|---|---|
| H01 | Observe before claiming | Repeated stale-state/canonical-state corrections in engineering work; Play-Nice freshness work | When is cached/pinned state intentionally sufficient? | Claude/Fable → Hermod → VEFR | SEED |
| H02 | Know who owns truth | Provider/Project Worlds/VEFR authority separation repeatedly improved correctness | Can explicit delegated authority safely move truth temporarily? | Engineering + world simulation | SEED |
| H03 | Separate epistemic kinds | Fact vs observation vs inference and world truth vs character belief both matter | What is the minimum useful distinction set? | Engineering ↔ characters/worlds | SEED |
| H04 | UNKNOWN is valid | Guessing to keep moving repeatedly creates false state; ask-for-help contract already preserves UNKNOWN | When should safe discovery replace UNKNOWN immediately? | All roles | SEED |
| H05 | Ask for help at competence/authority boundary | Granite Hermod onboarding successfully produced bounded help; Play-Nice encodes WAITING_FOR_HELP | Can excessive escalation destroy usefulness? Where is the threshold? | Small + frontier models | SEED |
| H06 | Constrain authority, not creativity | Strong autonomous design can survive when boundaries are clear | Which constraints actually improve creativity vs merely reduce options? | Coding + design + character generation | SEED |
| H07 | Define success externally | Self-reported completion has diverged from owner UAT and deterministic validation | Which low-risk tasks can be safely self-graded? | Engineering + structured generation | SEED |
| H08 | Verify consequential results deterministically | Tests, schemas, provider re-observation and UAT outperform confidence | What counts as consequential, and when is deterministic verification unavailable? | All operational roles | SEED |
| H09 | Re-observe before consequential action | Plans can become stale during concurrent/long-running work | How fresh is fresh enough by task class? | Orchestration + operations | SEED |
| H10 | Preserve evidence | Raw/rejected outputs and provenance enable later harness refinement | What is the minimum evidence that avoids burdensome logging? | Experiments + operations | SEED |

## Observation record template

Copy this block for meaningful evidence:

```markdown
### OBS-YYYY-NNN — short name

- Source / participant:
- Task / domain:
- Harness / model / version:
- Canonical context or revision:
- What happened:
- Expected behavior:
- Result:
- Candidate(s) affected: Hxx
- Supports / contradicts / complicates:
- Deterministic evidence:
- Human/UAT evidence:
- Counterfactual: what harness change might have changed the outcome?
- Model-specific or likely transferable?
- Notes / links:
```

## Promotion record template

```markdown
### Hxx promotion review

- Proposed wording:
- Failure/capability addressed:
- Supporting observations:
- Contradicting observations:
- Models/participants tested:
- Domains tested:
- Counterexample tests:
- Why kernel instead of adapter:
- Interaction with canonical contracts:
- Testable behavioral consequence:
- Decision: PROMOTE / KEEP EXPERIMENTAL / ADAPTER / REJECT
- Decision evidence / owner review:
```

## Research discipline

A failed hypothesis is useful. Preserve rejected candidates and why they failed so later contributors do not rediscover the same attractive but unsupported rule.
