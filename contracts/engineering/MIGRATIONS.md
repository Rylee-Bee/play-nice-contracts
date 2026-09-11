---
contract_id: migrations
title: Migrations
version: 1.0.0
status: canonical
layer: engineering
applies: [engineering, infrastructure, data]
triggers: [migration, system-replacement, schema-upgrade]
rationale: Migrations define current, target, transformation, validation, rollback, and a deletion gate. Starting is not completing; old systems survive until parity is proven where parity matters.
---

<!-- contract-receipt: fathom-latch-harbor -->

# Migrations

## Purpose

Make migrations deliberate, verifiable, and reversible-or-safe. A migration is complete when the new system is proven at parity (where parity matters) — not when it boots.

## NORMATIVE RULES

1. Every migration defines:
   ```text
   CURRENT      — verified description of the existing system's actual behavior
   TARGET       — the intended end state, with acceptance criteria
   TRANSFORMATION — the steps, ordered, with ownership
   VALIDATION   — how parity/completion is proven (tests, evidence grades)
   ROLLBACK     — how to return to CURRENT, tested
   DELETION GATE — the explicit condition under which the old system may be removed
   ```
2. Do not delete old systems until parity is proven where parity matters. The old path stays runnable until the gate is met.
3. Do not declare migration complete because the new system starts. Completion = validation passed (evidence, not vibes — see Testing and Verification).
4. Migrations are data-preserving: data migration paths are tested, round-trippable where practical, and classified (see Portability, Data Classification).
5. Cutover is bounded: feature flags / dual-run windows make the switch gradual and reversible; a big-bang cutover requires explicit justification.
6. The migration state is representable: `partial` (some parity proven), `complete` (all validation passed), with per-item truth for multi-part migrations.
7. Rollback is tested before it is needed; if rollback is genuinely impossible, the migration says so explicitly and justifies the irreversibility.

## RATIONALE

Migration lessons in this ecosystem: the new frontend that "worked" until the legacy HTML was deleted revealed missing parity items; the dashboard removal that went fine because deletion was a separate, evidence-backed decision; the schema bump that needed an explicit rejection path for old readers. The CURRENT→TARGET→…→DELETION GATE skeleton is the distillation.

## HUMAN EXAMPLES

- A parity checklist gates legacy deletion: every item checked at runtime, then the deletion commit removes old code in one clean step.
- "Migration status: 80% of routes verified on the new router; 2 routes pending; old router still active for them" — visible, honest `partial`.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Migration tracking as data: per-item parity status with evidence references.
- Feature flags with expiry: a flag surviving past its window is flagged as debt.
- Dual-run verification tooling where both paths can execute side by side.

## GOOD EXAMPLES

```yaml
migration:
  from: legacy-dashboard
  to: react-shell
  validation: parity-checklist.yml   # per-item, runtime-checked
  rollback: PW_FRONTEND=legacy       # tested 2026-09-10
  deletion_gate: "all parity items runtime-verified + human zoom gate passed"
  status: partial (2 items remaining)
```

## ANTI-PATTERNS

- "The new one is up; delete the old one."
- Declaring victory at first boot.
- Untested rollback documented as "restore from backup".
- Irreversible cutover without saying so.
- Parity assumed because both systems "look right".

## ACCEPTANCE CHECKS

- Are all six parts defined (CURRENT/TARGET/TRANSFORMATION/VALIDATION/ROLLBACK/DELETION GATE)?
- Is deletion gated on proven parity?
- Is current migration state honestly labeled (`partial` vs `complete`)?
- Has rollback actually been exercised?