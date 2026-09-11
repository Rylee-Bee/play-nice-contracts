---
contract_id: idempotency
title: Idempotency
version: 1.0.0
status: canonical
layer: interoperability
applies: [api, automation, operations]
triggers: [mutations, automation, retries, external-writes]
rationale: Repeated invocation must not accidentally repeat a destructive action. Never assume idempotency; use provider mechanisms where they exist, and design your own operations to be safely repeatable.
---

<!-- contract-receipt: timber-kite-quay -->

# Idempotency

## Purpose

Make "run it again" safe. Repeated or retried invocations — by automation, by a user double-clicking, by a retry loop, by a crash recovery — must not double-apply a mutation.

## NORMATIVE RULES

1. Repeated invocation should not accidentally perform the same destructive action twice. Where an operation is naturally idempotent (setting a value to X), say so. Where it is not (create, charge, append), make it safely repeatable.
2. Use provider idempotency mechanisms where available (idempotency keys, deduplication windows, unique constraints). Never assume idempotency that is not documented.
3. Read-modify-write loops re-read current state before applying; the result converges instead of compounding ("ensure" semantics over "do" semantics).
4. Retried operations carry a stable operation key so the receiver can deduplicate; receivers of mutations accept and honor such keys where practical.
5. Appends (journal entries, events, log lines) are either idempotent by content-hash or explicitly acknowledged as append-many with a documented reader contract.
6. Crash recovery re-derives state from authoritative sources rather than replaying blind (see Recovery and Reversibility); replays check "did this already happen?" before acting.
7. Automation that runs on schedules treats every run as possibly-repeated: guards ("only if changed", "only if not already done") wrap effects.

## RATIONALE

Retry logic (a necessity per Friendly API Client) is only safe when retries can't double-apply. Every "why are there three identical deployments?" incident traces to an idempotency assumption nobody verified. "Ensure" semantics also make automation robust to interruption: rerun from anywhere.

## HUMAN EXAMPLES

- Clicking "Deploy" twice deploys once; the second click reports "already running (started 14:02)".
- A crashed sync resumes and skips the 40 items it already completed — visibly, with a count.
- "Mark all read" clicked five times in frustration has exactly one effect.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Mutation APIs accept optional idempotency keys; stores record `op_key` uniqueness.
- `ensure`-style operations (declarative desired state + convergent apply) are preferred for automation.
- Job/run records persist what has been applied so recovery can skip completed work.
- Content-addressed dedup for journal/event writes where readers require exactly-once semantics.

## GOOD EXAMPLES

```http
POST /api/deploy
Idempotency-Key: 7f3c9a
→ 201 (applied)
→ 200 (already applied, same result)
```

## ANTI-PATTERNS

- Retrying a create endpoint without a key ("duplicate rows as a service").
- Automation that appends a notification per run regardless of change.
- "Delete and recreate" as the update mechanism.
- Assuming `POST` is idempotent because "it seemed to be".

## ACCEPTANCE CHECKS

- Double-run the most destructive automation: what happens? (Must be: nothing twice.)
- Do mutation APIs accept/honor idempotency keys?
- Is any append-semantics store read as exactly-once without a mechanism?