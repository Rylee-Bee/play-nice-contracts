---
contract_id: api
title: API
version: 2.0.0
status: canonical
layer: surfaces
applies: [apis, services]
triggers: [api, endpoint, http, rest api, web service, openapi]
rationale: The API is the seam every other surface builds on, so it must be versioned, documented, discoverable, and honest about errors.
---

<!-- contract-receipt: sparrow-walnut-birch -->

# API

## In short

Version it, document it, and keep one response shape. Errors are RFC 9457
problem details with stable machine identifiers. Everything the UI and CLI
can do runs through this seam.

## Applies when

You design or change an HTTP API that others consume. Not this contract's
job: the human/machine split itself (see one-truth-two-views) or calling
someone else's API (Integration pack).

## Rules

1. The API defines the programmable seam: UI, CLI, and agent tools are
   views over it. No surface hides private magic. (MUST)
2. The API version is explicit (path or header); breaking changes bump it
   and ship migration notes. (MUST)
3. One stable response shape across endpoints; clients learn the envelope
   once. (MUST)
4. Errors are RFC 9457 problem details (`application/problem+json`):
   `type`, `title`, `status`, `detail`, plus a stable machine `error`
   identifier and retryability. Never a bare 500 body. (MUST)
5. Status codes mean what they say: 401 unauthenticated, 403 not
   authorized (name the missing scope), 409 conflict, 422 validation per
   field, 429 rate limit with `Retry-After`, 5xx with a correlation id.
   Rate-limit answers stay polite, never connection resets. (MUST)
6. Reported state is honest: the shared status words (see the floor, rule 8),
   with `observed_at` and `source` where state is shown; never a cached
   success served as fresh. (MUST)
7. Answer "what can this API do?" from the API itself: a manifest or
   capability endpoint; unknown routes fail clearly, not blankly. (MUST)
8. Lists paginate by default; unbounded queries are rejected or
   paginated; filters are documented. (MUST)
9. Mutations accept idempotency keys wherever a retry could duplicate
   work; PUT and PATCH semantics are documented per endpoint. (MUST)
10. GET only reads: side effects never hide in GETs. (MUST)
11. Every protected route checks authorization centrally; none forgets.
    (MUST)
12. Documentation is the contract: endpoints, schemas, examples, and
    error identifiers are written down (OpenAPI where practical) and
    drift-tested against reality. (MUST)

## Examples

- Good: a 429 says `Retry-After: 120`; a 403 names the missing scope and
  how to get it.
- Good: a new client author builds against the manifest and docs alone,
  without reading server source.
- Bad: side effects on GET; 500s for validation errors; a different
  envelope per endpoint "as convenient".

## Why

An API that is versioned, honest, and discoverable is one future tools
can consume without archaeology; one that isn't quietly strands every
other surface on private, undocumented paths.

## You're done when

- Every surface consumes this API (or its shared models) rather than
  reimplementing it.
- Error bodies validate as RFC 9457 and carry stable identifiers.
- Every route's shape is schema-tested, and a new client integrated from
  docs alone.

## Machine notes

```json
{"type": "https://example.com/problems/rate-limited",
 "title": "Rate limit exceeded", "status": 429,
 "detail": "Limit is 120 requests per minute.",
 "instance": "/v1/reports", "error": "rate_limited",
 "retryable": true, "retry_after_s": 120}
```
