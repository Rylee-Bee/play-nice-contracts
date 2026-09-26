---
contract_id: room
title: Room
version: 2.1.0
status: canonical
layer: surfaces
applies: [apis, services, ui, integrations]
triggers: [room, front door, descriptor, cards, needs-you, room actions]
rationale: Many small independent backends can share one front door only if each serves the same few endpoints with the same honest shapes.
---

<!-- contract-receipt: thatch-beacon-heron -->

# Room

## In short

A room is any service that serves five fixed endpoints under `/room`.
One front door learns the shapes once and can display, link, and act on
every room generically, with a hard floor under risky actions.

## Applies when

You build a room, a front door, or anything speaking the room interface.
Not this contract's job: one product's deployment policy (see Machine
notes) or general API manners (api).

## Rules

1. A room serves exactly five endpoints; the path stays `/room` and
   never versions — the `contract` field does that. (MUST)
2. `GET /room` is the descriptor: its name, icon, own code version and
   commit, an `updated_at` time, and a status limited to `healthy`,
   `degraded`, `unhealthy`, or `unknown`. These are the room/0 wire
   words: `unhealthy` means the shared `unavailable` or
   `needs_attention`; changing the set needs room/1. A room
   that cannot verify itself says `unknown`, never `healthy`. (MUST)
3. `GET /room/cards` lists cards. Each card's `observed_at` is the
   underlying item's own time — when the thing was created or last
   changed, never the request time — with `stale_after_s`; past that,
   present the card as stale, never as current. (MUST)
4. Card `tone` is optional and only `good_news`, `update`, or
   `when_ready`: a display hint, never priority. Treat an unrecognized
   tone as `update` and log it; never crash or drop the card. Urgency
   belongs in needs-you, not in cards. (MUST)
5. `GET /room/needs-you` lists what a person must handle: the title, why
   it waits, and the action ids that resolve it. (MUST) A need that is a
   choice may list up to six short `choices`; the front door offers them
   as buttons and sends the picked one as the action's input. (MAY)
6. Links are same-origin paths: starting with `/`, no scheme, not `//`.
   Consumers reject anything else rather than following it. (MUST)
7. `GET /room/actions` lists actions with an input JSON Schema, whether
   they write state, and a default autonomy: `auto`, `check_in`, or
   `ask_first`. (MUST)
8. `POST /room/actions/{id}` is idempotent: the caller sends an
   `Idempotency-Key`; a repeated key returns the stored receipt and never
   applies the change twice. (MUST)
9. Every action call returns a receipt — success, refusal, or failure —
   with `ok`, an honest summary, exactly what changed, and when. Never a
   silent success, never an unlabelled error. (MUST)
10. Autonomy is the strictest of caller policy, room default, and a class
    floor. Deploys, secret access or change, pushes to a default branch,
    deletes, and spending are always `ask_first`; no policy, preference,
    or remembered consent lowers them. (MUST)
11. An `ask_first` action without a valid approval token fails closed.
    Tokens are opaque, scoped to one action and requester, single
    purpose, expiring, and never echoed back. (MUST)
12. The front door renders an unreachable room as unreachable, with a
    last-seen time, and never blanks or stalls the rest of the estate
    over one failed room. (MUST)
13. The front door authenticates the person; room-to-room calls use
    scoped bearer tokens, never the human's session token. No response
    field ever carries a secret value (see the floor, rule 11). (MUST)
14. `contract` declares the interface version (`room/0` today).
    Compatible additions keep the value; a breaking change takes a new
    value and a migration path; an unknown value fails clearly rather
    than guessing. (MUST)

## Examples

- A card is past its `stale_after_s`: the front door dims it — "last
  observed 3h ago" — instead of showing it as current.
- Tapping "Deploy" prompts for approval even though the caller's policy
  says `auto`: deploy sits on the floor.
- Bad: a room that lost its database reports `healthy`; a retry reusing
  an `Idempotency-Key` applies a transfer twice.

## Why

A front door that must learn each backend's private shape cannot host
many small backends cheaply. Five fixed, honest endpoints make the seam
generic — and the autonomy floor exists because the room is the last
place a policy mistake can be caught before it spends, deletes, or
deploys.

## You're done when

- All five endpoints exist and schema-test against
  `schema/room.schema.json`.
- A write with no approval token fails closed at `ask_first`, and the
  floor classes cannot be lowered.
- An unreachable room renders unreachable; unverifiable state reads
  `unknown` or stale, never `healthy`.
- A repeated `Idempotency-Key` returns the same receipt with nothing
  applied twice.

## Machine notes

```text
GET  /room              -> {contract,id,name,icon,version,commit,status,updated_at}
                           + voice? (display hint for captioning, never a claim about a person)
GET  /room/cards        -> [{id,title,body,link,lane,tone?,freshness:{observed_at,stale_after_s}}]
GET  /room/needs-you    -> [{id,title,why,actions,choices?,link?,created_at}]
GET  /room/actions      -> [{id,label,input_schema,default_autonomy,writes}]
POST /room/actions/{id} -> {action_id,ok,summary,changed,at}   header: Idempotency-Key
```

`lane` is `personal` or `work`; times are RFC 3339; descriptor `status`
is `healthy`, `degraded`, `unhealthy`, or `unknown` (the room/0 wire words; see rule 2). Schemas:
`schema/room.schema.json`. Building, deploying, registering, and
rolling back rooms independently behind one product is that product's
spec (for Worlds: the Worlds product spec), not a rule of this contract.
