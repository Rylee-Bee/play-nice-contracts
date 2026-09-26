---
contract_id: one-truth-two-views
title: One Truth, Two Views
version: 2.0.0
status: canonical
layer: surfaces
applies: [apis, clis, ui, tools, agents]
triggers: [json output, machine-readable, structured output, export, cli output, api response, parity]
rationale: One fact stored once and shown twice: plain words for people, stable shapes for machines, both generated from the same source.
---

<!-- contract-receipt: copper-hill-web -->

# One Truth, Two Views

## In short

Keep one source of truth per fact; people get honest wording, machines get
a stable schema, both generated from it. The floor (rule 13) says why;
this says how.

## Applies when

Anything that shows or accepts the same state through more than one path:
UI, CLI, API, agent tools, exports, logs. Not this contract's job: HTTP
details (api) or command-line habits (cli).

## Rules

1. Every important state has both a human form and a machine form,
   generated from one source. (MUST)
2. Same operation, same truth everywhere: each surface of a capability
   shows the same states, words, and policy. A capability lives in the
   system, not behind one surface. (MUST)
3. Human wording is generated from machine state at the presentation
   boundary, never the reverse: scripts must never parse human prose.
   (MUST)
4. Field names, shapes, and error identifiers are contracts: stable
   across releases; breaking changes bump a version. (MUST)
5. Machine output declares its version and time (`schema`, `observed_at`,
   `source`), never relying on context. (MUST)
6. Missing stays missing: `null`, an absent field, or `unknown` — never an
   invented default, an empty string, or a zero read as "not checked".
   (MUST)
7. Every machine-relevant surface offers a machine format: CLI `--json`,
   structured logs where tools consume them, exports with schemas. (MUST)
8. Errors carry a stable identifier, context, and retryability in machine
   form; the human sentence sits beside it, not instead of it (see api
   for HTTP bodies). (MUST)
9. Bulk output is paginated or bounded with explicit totals; consumers
   never guess whether they got everything. (MUST)
10. Where output feeds diffs or lockfiles, make it deterministic: same
    input, same bytes (sorted keys where sensible). (SHOULD)
11. Machine-readable output carries no secret values (see the floor, rule 11).
    (MUST)
12. Parity is tested: run one operation through each surface and check
    the truth matches. Record any surface that deliberately lacks a
    capability, with the reason. (MUST)

## Examples

- One fact, three renderings: UI "Everything looks good.", API
  `{"status": "healthy", "observed_at": …}`, CLI `healthy`.
- Bad: three scripts regex-parse a CLI table; one rewording breaks all
  three.
- Bad: `{ok: true}` with no version, no time, and no source.

## Why

Systems tuned only for people strand their automation; systems tuned only
for machines strand the tired operator at 2 a.m. One canonical state plus
a translation layer serves both without double bookkeeping.

## You're done when

- Every important state has an honest machine form and a useful human
  form.
- Changing a human sentence breaks no machine consumer.
- One operation was exercised through every surface with matching results.
