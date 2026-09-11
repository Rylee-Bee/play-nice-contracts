---
contract_id: human-and-machine-parity
title: Human and Machine Parity
version: 1.0.0
status: canonical
layer: interfaces
applies: [ui, cli, api, agents]
triggers: [interface-design, always-for-surfaces]
rationale: Important state has both a human representation and a machine representation. Human friendliness must not destroy machine precision; machine precision must not force humans to read raw JSON.
---

<!-- contract-receipt: lantern-latch-river -->

# Human and Machine Parity

## Purpose

Every important state is legible twice: as understandable human language/interface, and as stable machine schema — both generated from the same truth.

## NORMATIVE RULES

1. Important state has both representations. Bad:
   ```text
   Service seems okay :)
   ```
   Better machine state:
   ```json
   {"status": "healthy", "observed_at": "...", "source": "...", "warnings": []}
   ```
   with a human UI that can simply say:
   ```text
   Everything looks good.
   ```
2. Where a capability exists through several surfaces (CLI, API, web, agent tool, automation), they are views of the same capability: same state, same vocabulary, same policy. Do not create five unrelated versions of the same operation.
3. Neither representation is derived from prose: human language is generated FROM machine state (translation at the presentation boundary), never the reverse.
4. Human friendliness must not destroy machine precision; machine precision must not require humans to read raw JSON. The machine vocabulary stays stable while human wording improves freely.
5. Every capability is reachable through every appropriate surface: a human by UI/CLI, an agent by tool/JSON, a script by CLI `--json`, a program by API. No surface is a hack.
6. Do not make one interface first-class while leaving others as undocumented side doors — unless there is a compelling technical reason, recorded.
7. Interface parity is testable: the same underlying operation, exercised through each surface, yields equivalent truth (same states, same effects, same policy applied).

## RATIONALE

Systems that optimize only for humans strand their automation; systems that optimize only for machines strand their tired operators. The parity pattern (one canonical state + machine schemas + human translation layer) serves both without double maintenance — and it is what lets agents and people genuinely collaborate over the same system.

## HUMAN EXAMPLES

- "Everything looks good." in the UI, `{"status": "healthy"}` from the API, `healthy` from the CLI — one fact, three renderings.
- An agent's tool call and a person's click invoke the same endpoint, honor the same approvals, and leave the same audit trail.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Translation layers live at presentation boundaries (UI i18n strings, CLI human formatters); machine identifiers never leak wording into schemas.
- Parity tests exercise representative operations through all surfaces.
- Surface feature drift is reviewed: a capability added to one surface is added or consciously excluded elsewhere, with the reason recorded.

## GOOD EXAMPLES

```text
machine: {"error": "provider_unreachable", "retryable": true}
human:   "Couldn't reach Gitea. Everything else keeps working. [Retry]"
```

## ANTI-PATTERNS

- A UI-only status concept; a CLI-only operation; an API-only permission.
- Human strings that scripts must parse.
- Machine JSON that humans must read to understand their own system.
- Five spellings of "unavailable" across five surfaces.

## ACCEPTANCE CHECKS

- For each important state: is there both an honest machine form and a useful human form?
- Are all surfaces of one capability demonstrably the same operation?
- Can human wording improve without breaking any machine consumer?
- Is any surface an undocumented side door? (Record or fix.)