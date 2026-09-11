---
contract_id: recovery-and-reversibility
title: Recovery and Reversibility
version: 1.0.0
status: canonical
layer: core
applies: [operations, agents, infrastructure, data]
triggers: [mutations, destructive-actions, deployment, automation, risky-change]
rationale: Systems fail and people make mistakes. Design recovery before relying on perfect operation; a system is only trustworthy when its failures are survivable and its mistakes are reversible.
---

<!-- contract-receipt: meadow-fathom-aster -->

# Recovery and Reversibility

## Purpose

Make mistakes survivable and failure recoverable. Recovery must not require heroics from a person who is tired, interrupted, or new.

## NORMATIVE RULES

1. Mutating operations provide, where practical, some combination of: preview or dry-run, bounded blast radius, a known-good state to return to, post-change verification, and documented rollback.
2. Backups and rollback paths exist before they are needed, and are tested, not assumed.
3. Never rely on the operator never making mistakes. Guardrails over vigilance.
4. Mistakes are evidence. Record them and improve the guardrail; do not hide them or shame the person.
5. After any mutation, verify against the authoritative source before declaring success.
6. Ambiguous state is preserved, never guessed at or deleted.
7. The recovery path itself must be documented and reachable by a newcomer, not institutional knowledge.

## RATIONALE

The homelab's hard-won rule — PROVE STALE → CLEAN, never LOOKS STALE → DELETE — exists because deletion based on an assumption destroyed real work. Reversibility is what makes bold automation safe: a system that can undo its mistakes can be allowed to try.

## HUMAN EXAMPLES

- A settings change shows a diff before saving and offers "revert to previous" after.
- Deleting a worktree first lists dirty state, unique commits, and remote backup — and refuses if any is ambiguous.
- A failed deploy restores the previous version automatically or says clearly how to.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Destructive operations require a proof-of-staleness or safety check; the burden of proof is on deletion.
- Snapshots/checkpoints are cheap, automatic where possible, and named for the change that created them.
- Rollback is an explicit, testable path (documented command or API), not a theoretical possibility.
- `undo`/`revert`/`restore` semantics exist wherever the surface is stateful.

## GOOD EXAMPLES

```text
deploy --preview    → shows what will change, changes nothing
deploy              → applies, then verifies health; failure triggers documented rollback
```

## ANTI-PATTERNS

- "Are you sure?" as the only guardrail for a destructive action.
- Rollback documented as "restore from backup" where no tested restore procedure exists.
- Deleting anything merely because it looks unused or stale.
- Burying the undo path in tribal knowledge.
- Treating a person's mistake as a reason for shame rather than a missing guardrail.

## ACCEPTANCE CHECKS

- For each destructive action: what proof must exist before it proceeds?
- Is there a tested rollback for the most recent significant change?
- Can recovery be executed by someone who did not author the system?
- Are recent mistakes recorded with the guardrail they produced?