---
contract_id: recovery-and-history
title: Recovery and History
version: 2.0.0
status: canonical
layer: everyone
applies: [humans, agents, services, tools, automation, data]
triggers: [rollback, undo, deploy, delete, destructive, migration, backup, provenance, audit, history, cutover]
rationale: Mistakes and failures happen, so risky changes need a tested way back and every meaningful change needs a record of who, when, and why.
---

<!-- contract-receipt: sill-coral-moat -->

# Recovery and History

## In short

Give risky changes a preview and a tested way back. Prove things stale
before cleaning them. Record who changed what, when, and why.

## Applies when

You change, move, or delete something that matters — data, systems,
history. The floor already requires asking before anything hard to undo
(see the floor, rule 6); this contract defines what safe-to-try looks
like afterward.

## Rules

1. **Mutating operations offer, where practical:** a preview or dry-run,
   a bounded blast radius, a known-good state to return to, a post-change
   verification, and a documented rollback. (MUST)
2. **Verify against the live source after any mutation** before declaring
   success (see truth-and-evidence). (MUST)
3. **Backups and rollbacks exist before they're needed, and are tested,
   not assumed.** If a change truly can't be undone, say so plainly,
   before making it, and justify the irreversibility. (MUST)
4. **Guardrails, not vigilance.** Never design on the assumption that
   nobody will make a mistake. (MUST)
5. **Prove stale, then clean.** Delete or reset only on evidence the
   thing is genuinely stale; ambiguous state is preserved, never guessed
   at or removed. "Looks unused" is not evidence. (MUST)
6. **Recovery is for newcomers.** The undo path is a documented, testable
   command or button — reachable by someone who didn't build the system. (MUST)
7. **Record consequential changes:** the named actor (human, agent, or
   service — never an anonymous "system"), when, why, what changed, and
   the previous state. Corrections supersede; they don't silently
   rewrite history. (MUST)
8. **Generated content says so:** the model or tool, the source material,
   the date. No secret values in history — name the reference, not the
   value (see the floor, rule 11). (MUST)
9. **Migrations define six parts before they start:** current behavior
   (verified), target with acceptance criteria, ordered steps,
   validation, rollback, and the deletion gate for the old path. (MUST)
10. **A booting system is not a finished migration.** Don't remove the
    old path until parity is proven where parity matters; make cutover
    gradual (flags, dual-run windows) unless a big-bang is explicitly
    justified. (MUST)
11. **Migration state is per item and honest:** partial until every item
    is validated, with evidence for each. (MUST)
12. **Mistakes are evidence.** Record them and improve the guardrail;
    don't hide them and don't shame the person. (SHOULD)

## Examples

- Good: `deploy --preview` shows the diff and changes nothing; `deploy`
  applies, verifies health, and a failure triggers the documented
  rollback.
- Good: "Migration status: 80% of routes verified; 2 pending; old router
  still active for those; deletion gate: all items runtime-verified."
- Bad: "The new one is up; delete the old one." — the deletion skipped
  its gate, and rollback was never tested.

## Why

Bold automation is only safe when mistakes are cheap: reversibility is
what lets systems try things. And "why is this like this?" is the most
expensive recurring question in long-lived work — a durable record turns
it from archaeology into a lookup.

## You're done when

- For each destructive action: the proof required before deleting is
  named, and the action refuses without it.
- The most recent significant change has a rollback that was actually
  run.
- The next maintainer can answer who, when, and why from the record —
  not from chat transcripts.
- Your migration's status says partial or complete, backed by per-item
  evidence.

## Machine notes

```yaml
migration:
  from: legacy-dashboard
  to: react-shell
  validation: parity-checklist.yml   # per-item, runtime-checked
  rollback: PW_FRONTEND=legacy       # tested, with date
  deletion_gate: all parity items runtime-verified
  status: partial                    # 2 items remaining
```

The words `partial` and `complete` come from the shared status vocabulary
(see status-and-state). Journals and audit logs are append-only,
timestamped, and attributable.
