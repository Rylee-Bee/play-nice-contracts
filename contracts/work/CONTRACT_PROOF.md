---
contract_id: contract-proof
title: Contract Proof
version: 2.0.0
status: canonical
layer: work
applies: [agents, projects, sites, tools]
triggers: [receipt, proof, verify receipt, playnice check, badge, adoption, well-known, current version, claim compliance]
rationale: Being current with the rules needs one cheap, checkable statement per kind of participant, not a ceremony that proves reading instead of following.
---

<!-- contract-receipt: aspen-nimbus-reef -->

# Contract Proof

## In short

Agents start with one receipt line. Projects show a bee badge drawn by
their own check. Sites publish one public file. Each is checkable in
seconds; none is permission.

## Applies when

You are about to work under these contracts, ship a repo that adopts
them, or run a site that claims them. Not its job: which contracts
apply to a task (the resolver and the packs say).

## Rules

1. An agent starts substantial work with one line, written from the
   files it actually read:
   `Play-Nice floor <version> · receipt <word> · packs <a, b>`.
   The `packs` part lists only the packs it read for this task; say
   none if you read none. Never write the line from memory or guess
   the words. (MUST)
2. `playnice verify "<line>"` answers one question: is this line
   current for the library today? Current means keep working. Out of
   date means re-read the pages and write a fresh line. There is no
   other ritual.
3. When the floor or a pack changes meaningfully, its version and
   receipt word change, and older lines stop verifying. That is the
   whole staleness signal: the check tells you, you re-read, you
   continue.
4. The line proves you read the rules. It grants nothing: authority
   for a specific action still comes from the task (see the floor,
   rule 5), and inventing a receipt word is a lie about reading (see
   the floor, rule 1).
5. A project shows its proof as the bee badge, produced by
   `playnice check` in the project's own CI. The badge links to the
   check run that drew it; a copied picture is decoration, not proof.
   (MUST for claiming current)
6. The badge states its condition in words as well as color: "plays
   nice · vX", "behind · vY is out", "fix needed" (see the floor, rule
   14).
7. A site's proof is one public file at
   `/.well-known/play-nice.json` giving its version, packs, and a
   contact. `playnice check https://site` reads it, runs light checks,
   and draws the same badge.
8. Claim only what is true right now: no packs you didn't read, no
   badge for a check that isn't green, and refresh a site's well-known
   file before its own `expires` date. (MUST)
9. If two applicable contracts genuinely conflict, say so and stop
   with the pair and the tension named — an honest blocked answer is
   compliant behavior (see the floor, rule 9).
10. The old eight-step gate — freshness check, resolve, read, hash
    verify, attest, commitment — and the legacy `contractctl` tooling
    around it are retired; they are documented in
    `docs/PLAYNICE.md` for existing adopters.

## Examples

- Good: `Play-Nice floor 1.0.0 · receipt honey-cell-lantern · packs
  work` — written after reading the floor and the work pack;
  `playnice verify` returns current.
- Bad: an agent copies yesterday's line without re-reading after a
  pack bump; `verify` returns out of date and the work is stopped
  until it reads.
- Bad: a README shows a downloaded badge picture with no link to any
  check run.

## Why

The old gate had eight steps and still only proved retrieval, not
following: agents summarized contracts from memory, or acknowledged
everything and changed nothing. One line per agent, one drawn badge
per project, one public file per site — each machine-checkable in a
second — keeps the honest part of the old design (you can check, and
staying quiet about failing is not allowed) at near-zero cost.

## You're done when

- `playnice verify` returns current for the line you wrote this
  session.
- The badge in the README links to a real check run and its word-state
  matches.
- The site's well-known file serves, names its version and packs, and
  has a contact.
- No proof artifact claims a pack or state that isn't true.

## Machine notes

Line grammar: `Play-Nice floor <semver> · receipt <word-word-word>[
· packs <id>[, <id>...]]` — version and receipt word copied verbatim
from the floor page's front matter and receipt comment; pack ids are
the layer names (e.g. `work`).

`/.well-known/play-nice.json`:

```json
{
  "schema": "play-nice/site-v1",
  "version": "<floor version>",
  "receipt": "<floor receipt word>",
  "packs": ["work", "people"],
  "contact": "mailto:owner@example.com",
  "expires": "2027-03-01"
}
```

`contact` and `expires` follow the security.txt pattern so a stale
claim ages out on its own. Commands: `playnice verify "<line>"`,
`playnice check` (repo; writes badge), `playnice check <url>` (site).
Legacy: `contractctl` gate workflow in `docs/PLAYNICE.md`.
