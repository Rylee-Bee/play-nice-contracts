---
contract_id: review-and-integration
title: Review and Integration
version: 1.0.0
status: canonical
layer: agents
applies: [agents, engineering]
triggers: [multi-agent, merge-work, batch-work]
rationale: Parallel work integrates serially and is tested as combined state. Worker-green is not integration-green; the foreman verifies, rejects, and reassigns without drama; the current diff is reviewed before merge.
---

<!-- contract-receipt: harbor-zenith-ember -->

# Review and Integration

## Purpose

Define how parallel work becomes one coherent system: serial integration, combined-state verification, honest review of actual diffs, and rejection as a normal mechanism.

## NORMATIVE RULES

1. Parallelize only where ownership is clear; integrate serially. Multiple agents never simultaneously redesign shared foundations (shell, router, design tokens, core schema, shared API client, policy, canonical contracts) — shared foundations get one owner.
2. Worker-green is not integration-green. The combined state is tested after merge at the integration SHA — the full deterministic gate plus integration-specific suites.
3. Review the current diff: what is reviewed is what is actually being merged (at the integration SHA), not what a worker says it wrote.
4. Rejection is normal: the foreman/orchestrator rejects worker output that fails criteria and reassigns or fixes — recorded, without treating rejection as failure (see Orchestration).
5. Integration order follows dependency order; conflicting changes to one seam are serialized (one lands, the other rebases on fresh truth).
6. Verification of integration uses the evidence grades of Testing and Verification — no grade inflation for combined state ("CI TESTED at integration SHA", not "should be fine").
7. Merge authority is explicit and separate from push authority (see Bounded Work); integration is a gate with a name and a record.
8. Human gates apply at integration where consequences are real (release, deletion of old systems, product acceptance).

## RATIONALE

Two parallel lanes both "green" produced a broken merge because each had changed the other's import path; that produced the rule this contract encodes. Combined-state testing catches the class of failure no worker can see: the interaction. And reviewing real diffs (not summaries) is the only review that survives confident workers.

## HUMAN EXAMPLES

- Three UI lanes merge one at a time; after each merge, the shared shell suite runs; the third lane rebases because the tokens changed.
- A rejected worker diff returns with a one-line record: "rejected: axe found color-only status at two lines; reassigned to same worker with pointer to StatusChip rules."

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Integration is scripted: merge → gate → record, per lane, in dependency order.
- Shared-foundation lanes are detectable (owned-path overlap) and serialized by tooling.
- Integration records persist per lane: base, merged SHA, gate results, rejections.

## GOOD EXAMPLES

```text
lane-a (leaves)    → merged @d41f2c; gate: 214 passed
lane-b (leaves)    → merged @e02b81; gate: 216 passed (rebased once on d41f2c)
lane-c (shell/tokens) → serialized first, sole owner of tokens
final: combined suite + human zoom gate → PASS
```

## ANTI-PATTERNS

- Merging all branches at once and hoping.
- Two lanes both "owning" the token file.
- Reviewing the worker's summary instead of the diff.
- Treating a rejected lane as a catastrophe instead of a reroute.
- Skipping combined-state tests because each lane was tested.

## ACCEPTANCE CHECKS

- Did integration run serially in dependency order?
- Was the full gate green at the final integration SHA?
- Were rejections recorded with reasons?
- Was any shared foundation edited by more than one lane? (Must be no.)