---
contract_id: data-classification
title: Data Classification
version: 1.0.0
status: canonical
layer: security
applies: [data, api, agents, configuration]
triggers: [data-modeling, exports, always-for-data]
rationale: Data has classes — public, private, secret — and every reader, writer, export, and model context respects them. The core assigns classification; payloads and providers cannot grant their own.
---

<!-- contract-receipt: inkstone-quartz-sail -->

# Data Classification

## Purpose

Every piece of data carries a classification that governs where it may appear: exports, logs, model context, other users' views.

## NORMATIVE RULES

1. Classify data — at minimum: `public` (safe anywhere), `private` (owner-scoped, never in shared outputs), `secret` (see Secrets contract). Additional classes allowed where a domain needs them (e.g. `world`, `internal`), but the set is closed per system and documented.
2. The core assigns classification when recording facts. A payload's self-declared class is ignored; a provider cannot upgrade its own data to a friendlier class by supplying it.
3. Reads and writes respect class everywhere: exports filter by class; UI surfaces render according to class; logs and model context exclude `secret` and respect `private` boundaries.
4. Classification travels with data: exports carry per-record classes; imports preserve them; provenance does not launder classification.
5. Access to another boundary's private material is never implied by administrative access (see Authorization); private memory belonging to another user or boundary is invisible, not merely hidden behind a UI.
6. Ambiguous class fails safe: unknown classification is treated at least as `private`, never as `public`.
7. Classification requirements are testable: an export containing private-classified data is a test failure, not a policy statement.

## RATIONALE

The provider-classification guard in Personal World exists because a provider tried exactly the bypass this contract forbids. Classification-as-data (not classification-as-convention) is what makes multi-user futures, shareable exports, and agent contexts safe by construction rather than by vigilance.

## HUMAN EXAMPLES

- A settings export contains capability choices and preferences but structurally cannot contain journal entries, memories, or tokens.
- An agent working on UI polish is never handed vault material "because it was in the database".
- Sharing a world configuration with a friend shares exactly the world, never the journal.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Every record carries a `classification` field; readers filter on it.
- Export functions are whitelist-per-class; tests prove private/secret material cannot appear.
- Model-context builders select by class and boundary; secrets never enter prompts.
- Importers validate classes against the closed set; unknown class = rejected, not defaulted.

## GOOD EXAMPLES

```json
{"kind": "journal", "classification": "private", "data": {...}}
// settings-export: structurally excludes kinds whose class is private or secret
```

## ANTI-PATTERNS

- One "data" blob with no classes, exported whole.
- Classification decided at render time by UI code.
- "It's fine, the export is only for admins."
- Providers tagging their own payloads `public`.

## ACCEPTANCE CHECKS

- Does every export test prove class exclusion?
- Can any path render or transmit secret-classified data outside a secure workflow? (Must be no.)
- Is unknown classification defaulted to public anywhere? (Must be no.)