---
contract_id: external-mutations
title: External Mutations
version: 1.0.0
status: canonical
layer: interoperability
applies: [integration, api, agents, operations]
triggers: [external-mutation, provider-writes, automation, agent-actions]
rationale: Changing someone else's system is the highest-risk routine activity. Gate it with inspection, minimal application, authoritative verification, provenance — and human approval where consequences are real.
---

<!-- contract-receipt: heather-rill-hollow -->

# External Mutations

## Purpose

Make mutations of external systems deliberate, minimal, verified, and attributable — whether performed by a human, an automation, or an agent.

## NORMATIVE RULES

1. Every external mutation follows:
   ```text
   observe → understand current state → understand desired state →
   preview/diff when possible → smallest useful mutation →
   verify against the authoritative source → record provenance
   ```
2. Make the smallest useful mutation. "Delete and recreate" is a last resort with explicit justification, not an update mechanism.
3. Verify against the authoritative source, not the mutation's echo. A 200 from the write endpoint is not proof the world changed; re-read the resource.
4. Record provenance for every mutation: actor (human/agent/automation), intent, target, time, result (see Provenance and Audit).
5. High-consequence mutations require human approval before application: propose → explain → human approves → act. The proposal includes the diff/preview and the blast radius.
6. Trusted automation may act within previously approved boundaries, where the boundaries are visible, editable, and revocable, and the actions are journaled. Remembered rules never silently erase the approval boundary for severe actions.
7. Destructive or irreversible external actions require step-up confirmation naming the consequence — never a casual click (see Copy and Language).
8. Agents never expand mutation authority on their own: the authority granted in the task instruction is the whole authority.
9. Mutations are idempotent or keyed (see Idempotency), so retry never double-applies.

## RATIONALE

The most expensive incidents in this ecosystem came from acting on external systems: deleted branches that weren't fully merged, recreated services with lost config, an "update" that wiped state. Every guard here traces to a real mutation that would have been prevented by observe-diff-verify-attribute.

## HUMAN EXAMPLES

- An agent proposes: "Add label `needs-review` to 3 PRs in burgeswe/personal-world. No other changes." — human approves — agent applies, verifies each PR now has the label, records provenance.
- An automation updates DNS records by ensuring desired state; reruns change nothing.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Mutation clients separate preview/apply/verify operations; UIs and agent tools share them.
- Approval workflows persist the approved rule (boundary), not blanket consent.
- Journaled mutation events carry actor, intent, target, before/after reference.
- Blast-radius metadata (how many resources, reversible or not) accompanies every proposal.

## GOOD EXAMPLES

```json
{"action": "propose", "mutation": "label_pr", "targets": [101, 102, 104],
 "preview": {"add": ["needs-review"]}, "reversible": true,
 "authority": "explicit-task-instruction"}
```

## ANTI-PATTERNS

- Firing a mutation because the tool "was pretty sure".
- Verifying with the write response instead of a fresh read.
- Blanket "you may do whatever helps" authority for automation.
- Recreating resources to change one field.
- Approval prompts that don't show the diff or the count of affected things.

## ACCEPTANCE CHECKS

- Is every external mutation preceded by observation and followed by authoritative verification?
- Are consequences and blast radius named before approval?
- Is every mutation attributable after the fact?
- Can any automation action exceed its approved boundary? (Must be no.)