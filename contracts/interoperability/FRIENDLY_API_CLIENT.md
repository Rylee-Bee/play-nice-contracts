---
contract_id: friendly-api-client
title: Friendly API Client
version: 1.0.0
status: canonical
layer: interoperability
applies: [integration, api, external-service]
triggers: [external-api, provider, integration-work]
rationale: When interacting with someone else's system: learn its documented contracts first, respect its limits, read before writing, retry intelligently, and stay idempotent. A good guest is a reliable guest.
---

<!-- contract-receipt: harbor-prairie-fable -->

# Friendly API Client

## Purpose

Define how to be a good citizen of other people's systems: learn before acting, respect the service, read before write, retry intelligently, be idempotent.

## NORMATIVE RULES

### Learn before acting

1. Prefer, in order: (1) the current documented API; (2) the official SDK if it materially helps; (3) supported protocols; (4) documented authentication; (5) documented compatibility/version notes.
2. Avoid undocumented/private endpoints unless explicitly necessary and understood — and document the reason when used.
3. Avoid scraping UI when a suitable API exists.
4. Check documented API versions and deprecation notices before building.

### Respect the service

5. Honor pagination, quotas, rate limits, `Retry-After`, caching guidance, ETag/conditional requests, documented timeouts, webhook/event mechanisms, connection limits, and API versions.
6. Use bounded concurrency. Use backoff with jitter where retrying. Do not hammer a system simply because automation can.
7. Do not disable or bypass protections (TLS verification, rate limits) to make things "work".

### Read before write

8. For mutations follow:
   ```text
   observe → understand current state → understand desired state →
   preview/diff when possible → smallest useful mutation →
   verify against the authoritative source → record provenance
   ```

### Retry intelligently

9. Retry transient failures within bounds. Do NOT blindly retry: authentication failure, authorization failure, invalid data, policy refusal, semantic conflict, destructive failure, or explicit human rejection — these are answers, not obstacles.
10. Never assume idempotency: use provider idempotency mechanisms (keys, tokens) where offered; treat unspecified endpoints as non-idempotent.

## RATIONALE

Every provider integration written in anger (no pagination, no backoff, retry-on-401 loops) has produced the same failures: rate-limit bans, duplicated writes, mysterious 5xx storms. Being friendly to other systems is not politeness — it is the difference between integrations that survive and integrations that get you throttled at 3 AM.

## HUMAN EXAMPLES

- A sync job that reads one page at a time, respects a 429 with `Retry-After: 120`, and resumes — instead of hot-looping.
- A rename operation that first GETs the current name, diffs, applies once, then verifies — instead of POSTing the rename three times "to be safe".

## MACHINE / IMPLEMENTATION IMPLICATIONS

- API clients centralize: pagination handling, rate-limit/backoff policy, timeout defaults, retry classification (retryable vs. terminal), and idempotency keys.
- Non-retryable error classes are encoded per client (auth, validation, conflict), not discovered per incident.
- Concurrency is a bounded, configured value, never unbounded parallelism.
- Every external mutation logs provenance (endpoint, request id, when).

## GOOD EXAMPLES

```python
# terminal classes: never retried
NO_RETRY = {401, 403, 409, 422}
# transient classes: retried with backoff+jitter, bounded
RETRYABLE = {429, 500, 502, 503}
```

## ANTI-PATTERNS

- Retrying a 401 forever with the same bad token.
- Fetching all pages with no limit on a rate-limited API.
- Scraping HTML because the JSON API needed a key.
- Mutating before reading ("delete and recreate" to update).
- Unbounded goroutine fan-out against a shared service.

## ACCEPTANCE CHECKS

- Does the client honor pagination and rate limits on every path?
- Are terminal failures classified and never retried?
- Is every mutation preceded by observation and followed by authoritative verification?
- Would this client survive a provider that is slow, flaky, or hostile?