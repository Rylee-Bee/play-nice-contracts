---
contract_id: room
title: Room
version: 1.0.0
status: canonical
layer: interfaces
applies: [api, ui, integration, automation]
triggers: [api-design, api-work, room-contract, interface-design, mutations, autonomy]
rationale: Many small independent backends can share one front door only if each serves the same five endpoints with the same honest shapes, the same idempotent writes, and a non-lowerable autonomy floor for consequential actions.
---

<!-- contract-receipt: fathom-ridge-wren -->

# Room

## Purpose

Let one front-door application render and operate many small, independent
backends — **rooms** — without owning any room's code. A room is any service
that serves the same five HTTP endpoints; the front door learns the shape once
and can display, link, and act on every room generically.

## NORMATIVE RULES

1. A room serves exactly these five endpoints. The path stays `/room`; there is
   no per-version path.
   ```text
   GET  /room              -> room descriptor
   GET  /room/cards        -> list of cards
   GET  /room/needs-you    -> list of needs
   GET  /room/actions      -> list of actions
   POST /room/actions/{id} -> action receipt
   ```
2. `GET /room` returns the room descriptor:
   ```json
   {
     "contract": "room/0",
     "id": "ledger",
     "name": "Ledger",
     "icon": "book",
     "voice": "dry and precise",
     "version": "1.2.0",
     "commit": "a1b2c3d",
     "status": "healthy",
     "updated_at": "2026-09-25T13:05:48Z"
   }
   ```
   `id`, `name`, `icon`, `version`, `commit`, `status`, and `updated_at` are
   required. `voice` is an optional display persona label only — a hint for how
   the front door may caption the room, never a claim about a person. `version`
   and `commit` identify the room's own code. `updated_at` is RFC 3339.
   `status` is exactly one of `healthy`, `degraded`, `unhealthy`, `unknown`.
3. `GET /room/cards` returns a list of cards:
   ```json
   [
     {
       "id": "card-1",
       "title": "Rent due soon",
       "body": "Next withdrawal is scheduled.",
       "link": "/ledger/rent",
       "lane": "personal",
       "freshness": { "observed_at": "2026-09-25T12:00:00Z", "stale_after_s": 3600 }
     }
   ]
   ```
   `lane` is exactly one of `personal`, `work`. `freshness.observed_at` is RFC
   3339 and `freshness.stale_after_s` is integer seconds after which the card is
   stale. `link` is a same-origin path the front door may follow.
4. `GET /room/needs-you` returns a list of needs:
   ```json
   [
     {
       "id": "need-1",
       "title": "Confirm the transfer",
       "why": "A withdrawal above the usual threshold is waiting.",
       "actions": ["confirm-transfer"],
       "created_at": "2026-09-25T12:30:00Z"
     }
   ]
   ```
   Each `actions` entry is an `id` published by `GET /room/actions`; a need that
   charges attention names the action that resolves it. `created_at` is RFC 3339.
5. `GET /room/actions` returns a list of actions:
   ```json
   [
     {
       "id": "confirm-transfer",
       "label": "Confirm transfer",
       "input_schema": { "type": "object", "properties": {}, "additionalProperties": false },
       "default_autonomy": "ask_first",
       "writes": true
     }
   ]
   ```
   `input_schema` is a JSON Schema for the action's input. `writes` is `true`
   when invoking the action can change state outside the room's response.
   `default_autonomy` is exactly one of `auto`, `check_in`, `ask_first`.
6. `POST /room/actions/{id}` returns a receipt:
   ```json
   {
     "action_id": "confirm-transfer",
     "ok": true,
     "summary": "Transfer confirmed; settlement scheduled.",
     "changed": ["transfer-8812"],
     "at": "2026-09-25T13:05:48Z"
   }
   ```
   The receipt is always returned — including for a refusal or a failure, with
   `ok: false` and an honest `summary` — never a silent success and never an
   unlabelled error. `changed` lists exactly what changed and is empty when
   nothing did. `at` is RFC 3339.
7. `POST /room/actions/{id}` MUST be idempotent. The caller supplies an
   `Idempotency-Key` header; a repeated key returns the same receipt and never
   re-applies the mutation (see Idempotency). Retrying an action without a key
   is not a contract the room may assume.
8. Autonomy is decided by the caller — the policy owner, human or the front
   door acting on the owner's configured policy — not by the room and not by
   the requester. A room advertises `default_autonomy` as its default, not as a
   ceiling; the effective autonomy is the strictest of the caller's policy, the
   room's default, and the class floor in rule 9.
9. A room MUST refuse a write when its effective autonomy is `ask_first` and
   the request carries no valid approval token. Some action classes are always
   `ask_first` and cannot be lowered by policy, preference, or remembered
   consent: deploys; secret access or change; pushes to a default branch;
   deletes; and spending. An action in one of these classes advertises
   `ask_first` and fails closed without an approval token.
10. An approval token is opaque, scoped to the action and the requester, single
    purpose, and expiring; a room validates scope, action, and expiry (see
    Authorization, External Mutations). The token is never a secret value and is
    never echoed in any response.
11. Honesty over optimism: a room that cannot verify a fact reports `unknown`,
    never `healthy`. `unknown` is not `healthy` and it is not failed. A card past
    its `stale_after_s` is presented as stale and MUST NOT render as current.
    Never invent a default value in place of an unverified fact (see Truth and
    Evidence, Explicit State, Failure and Degradation, Machine Readable Output).
12. A front door MUST render an unreachable room as unreachable, with the
    last-seen time when one is known, and MUST NOT blank or stall the rest of
    the estate because one room failed (see Failure and Degradation).
13. Rooms sit same-origin behind the front door's auth proxy; the front door
    authenticates the human and forwards an authenticated context. Room-to-room
    calls use scoped bearer tokens under least privilege — never the human's
    session token (see Authentication, Least Privilege). No response may contain
    a secret value; secrets are referenced symbolically, never copied into a
    descriptor, card, need, action, or receipt (see Secrets, Data
    Classification).
14. Versioning follows Versioning and Compatibility. The path stays `/room`; the
    `contract` field in `GET /room` declares the interface version (`room/0`
    today). Compatible additions are MINOR clarifications of the same contract
    value; a breaking change requires a new contract value and an explicit
    migration path. A consumer that does not understand a contract value fails
    clearly rather than guessing. `room/0` is pre-1.0 and may change.

## RATIONALE

A front door that must know every backend's private shape cannot host many
small backends cheaply, and a backend that must know the front door's internals
cannot be moved or replaced. Five fixed endpoints with honest shapes make the
seam between them generic: the front door renders any room, and a room stays
ignorant of the front door. The autonomy floor exists because the room is the
last place a policy mistake can be caught — a deploy, a delete, or a secret
change must not become automatable just because one caller's preference says
so. Honest status and unreachable rendering exist because a front door that
shows a stalled room as healthy is more dangerous than one that shows it is
gone.

## HUMAN EXAMPLES

- A card's `observed_at` is older than its `stale_after_s`; the front door dims
  it and says "last observed 3h ago" rather than presenting it as current.
- Tapping "Deploy" in a room prompts for approval even though the caller's
  policy says `auto`, because deploy is in the non-lowerable floor.
- One room stops responding; the front door shows "unreachable — last seen 12
  minutes ago" for that room while every other room keeps working.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- The five response shapes are schema-tested against `schema/room.schema.json`.
- The idempotency store is keyed by `Idempotency-Key` per action, so a retry
  converges on the recorded receipt.
- Effective autonomy is computed as the strictest of caller policy, room
  default, and the non-lowerable class floor — never the loosest.
- Approval tokens are checked for scope, action, and expiry at the operation
  boundary; refusals are journaled.
- The front door circuit-breaks per room and persists last-seen timestamps so
  unreachable rendering stays truthful.
- Responses are structurally secret-free: no secret values by construction.

## GOOD EXAMPLES

```json
// GET /room — a room that cannot verify its backing store says so
{"contract": "room/0", "id": "ledger", "name": "Ledger", "icon": "book",
 "version": "1.2.0", "commit": "a1b2c3d", "status": "unknown",
 "updated_at": "2026-09-25T13:05:48Z"}
```

```http
POST /room/actions/confirm-transfer
Idempotency-Key: 7f3c9a
→ {"action_id": "confirm-transfer", "ok": true,
   "summary": "Transfer confirmed; settlement scheduled.",
   "changed": ["transfer-8812"], "at": "2026-09-25T13:05:48Z"}
→ retry with the same key returns the same receipt; nothing is applied twice
```

## ANTI-PATTERNS

- Reporting `healthy` when a dependency could not be reached — silence read as
  good news.
- Rendering stale card data as current, or an unreachable room as unchanged.
- Letting policy, a preference, or remembered consent lower deploy, secrets,
  default-branch pushes, deletes, or spending below `ask_first`.
- A non-idempotent action endpoint where a retry double-applies.
- A room holding or forwarding the human's session token, or room-to-room calls
  reusing it.
- Inventing a placeholder default when a fact is unknown.
- Secret values in a descriptor, card, need, action, or receipt.
- A new path per version that strands existing front-door clients.

## ACCEPTANCE CHECKS

- Do all five endpoints exist with the declared shapes, schema-validated?
- Does a write with no approval token fail closed whenever effective autonomy is
  `ask_first`?
- Can policy lower deploy, secrets, default-branch pushes, deletes, or spending
  below `ask_first`? (Must be no.)
- Does an unreachable room render as unreachable with a last-seen time?
- Is unverifiable state reported as `unknown` or stale, never `healthy`?
- Is `POST /room/actions/{id}` idempotent under a repeated `Idempotency-Key`?
- Does `GET /room` carry `contract: room/0`, with the path staying `/room`?
- Do any responses carry secret values? (Must be no.)