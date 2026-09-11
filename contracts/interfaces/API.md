---
contract_id: api
title: API
version: 1.0.0
status: canonical
layer: interfaces
applies: [api]
triggers: [api-design, api-work]
rationale: APIs are the programmable seam every other surface builds on: versioned, documented, discoverable, honest in envelopes, and stable in identifiers.
---

<!-- contract-receipt: jetty-window-urnfield -->

# API

## Purpose

Make the HTTP API a durable, friendly contract: the seam the CLI, UI, agents, and future clients all consume with confidence.

## NORMATIVE RULES

1. The API defines the programmable seam: UI, CLI, and agent tools are views over it (see Human and Machine Parity). No surface hides API-only magic.
2. Versioned and declared: API version is explicit (path/header); breaking changes bump versions with migration notes (see Versioning and Compatibility).
3. Consistent envelopes: a stable response shape (e.g. `{ok, status, changed, warnings, actions, data}`) across endpoints; clients learn the envelope once.
4. Honest status in every response: canonical status vocabulary (see Explicit State), `observed_at`/`source` where state is reported; never cached-success masquerading as fresh.
5. Errors use stable identifiers with structured context and retryability, mapping to proper status codes: 401 (not authenticated), 403 (not authorized — name the needed scope), 409 (conflict), 422 (validation — per-field), 429 (rate limit + `Retry-After`), 5xx (with correlation IDs).
6. Discoverability: a manifest/capability endpoint answers what this API can do and at what version (see Discovery and Negotiation); unknown routes fail clearly, not blankly.
7. Pagination is the default for list-shaped resources; filters are documented; unbounded queries are rejected or paginated.
8. Idempotency: mutations accept idempotency keys where duplication is possible; PUT/PATCH semantics documented per endpoint (see Idempotency).
9. Read vs. write is obvious: GET is safe; side effects never hide in GETs; journal-worthy mutations journal themselves.
10. Auth is centralized (see Authorization): every protected route checks; none "forgets".
11. Documentation is the contract: endpoints, schemas, examples, and error identifiers are documented (OpenAPI/schema where practical) and drift-tested against reality.

## RATIONALE

The envelope-plus-manifest pattern (Personal World) made CLI, UI, and agents share one truth cheaply; the "provider failure is not core failure" rule kept one broken dependency from failing every response. Both generalize: an API that is versioned, honest, and discoverable is one that future tools can consume without archaeology.

## HUMAN EXAMPLES

- A new client author reads the manifest, finds `source_control` capabilities, and builds against documented shapes — without reading the server's source.
- A 429 response includes `Retry-After: 120`; a 403 names the missing scope and the granting path.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Schema-first or schema-tested: contract tests assert envelope shapes for every route.
- Error identifier registry is shared with CLI/UI translation layers.
- Correlation/request IDs flow through to logs (see Observability).
- Rate limiting documented and consistent; abuse answers are polite (429) not hostile (connection reset).

## GOOD EXAMPLES

```json
{"ok": true, "status": "healthy", "changed": false,
 "warnings": [], "actions": ["recheck"], "data": {...}}
```

## ANTI-PATTERNS

- Side effects on GET.
- Different envelopes per endpoint "as convenient".
- 500s for validation errors.
- Undocumented pagination (returns "everything, sometimes").
- Breaking changes shipped under the same version.
- Errors that differ between CLI, API, and UI for the same failure.

## ACCEPTANCE CHECKS

- Do all surfaces consume this API (or share its models) rather than reimplementing it?
- Is every response envelope-consistent and schema-tested?
- Are error identifiers stable and documented?
- Can a new client integrate from docs alone?