---
contract_id: polling-webhooks-and-caching
title: Polling, Webhooks, and Caching
version: 1.0.0
status: canonical
layer: interoperability
applies: [integration, api, operations]
triggers: [external-api, monitoring, sync, event-driven]
rationale: Get notified when notification exists, poll politely when it doesn't, and cache honestly — cached data must never masquerade as current observation.
---

<!-- contract-receipt: ellsworth-sail-wren -->

# Polling, Webhooks, and Caching

## Purpose

Choose the right change-detection mechanism, use each politely, and keep cached truth honest about its age.

## NORMATIVE RULES

1. Prefer event mechanisms (webhooks, change streams, push) where offered; use polling as fallback, and politely.
2. Poll within documented limits: honor rate limits and `Retry-After`, use conditional requests (ETag/If-Modified-Since), back off on errors, and choose intervals from the provider's documented guidance — not from impatience.
3. Cache with honesty: every cached value is `stale`-aware. Cached observations carry `observed_at`; re-showing old data as current is a defect (see Truth and Evidence).
4. Cache invalidation is explicit: write paths invalidate what they change; TTLs bound staleness; readers can always refresh.
5. Webhook receivers verify authenticity (signatures/secrets), respond promptly (acknowledge, then process), and treat webhook payloads as notifications to verify — not as authoritative state (re-query the source before consequential action).
6. Duplicate delivery is expected: webhook processing is idempotent (see Idempotency).
7. Missed events are expected: periodic reconciliation (a slower full read) catches what push missed.
8. The poll-vs-webhook choice is documented per integration, with the reason.

## RATIONALE

Impatient polling gets integrations banned; blind webhook trust gets them exploited; honest caching failures silently mislead dashboards. The same three lessons recur in every monitoring and sync system: be polite, verify pushes, label age.

## HUMAN EXAMPLES

- A status row shows "checked 30s ago" for fresh data and "checked 3 days ago — may be out of date" for stale, instead of both looking identical.
- A webhook storm triggers processing that acknowledges instantly and verifies against the API before writing anything consequential.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Polling clients share the bounded/backoff machinery of Friendly API Client.
- Cache layers expose age and source; status composition treats `stale` as its own state, worse than healthy, better than unknown (per the shared vocabulary).
- Webhook endpoints: signature verification, fast 2xx ack, queue for processing, idempotent handlers, reconciliation schedule.

## GOOD EXAMPLES

```json
{"status": "stale", "observed_at": "2026-09-08T01:00:00Z",
 "note": "last successful poll; provider unreachable since"}
```

## ANTI-PATTERNS

- Polling every 5 seconds against an API that documents 60-request/hour limits.
- Trusting a webhook payload as final truth without re-querying.
- A cache with no timestamps whose data looks live forever.
- Retry-storming a webhook provider that is down.

## ACCEPTANCE CHECKS

- Is the mechanism per integration documented with a reason?
- Does any cached value ever render indistinguishable from a fresh observation?
- Are webhook handlers idempotent under duplicate delivery?
- Is there a reconciliation path for missed events?