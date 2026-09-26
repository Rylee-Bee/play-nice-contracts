---
contract_id: events-and-caching
title: Events and Caching
version: 2.0.0
status: canonical
layer: integration
applies: [integrations, apis, services, automation]
triggers: [webhook, polling, cache, sync, event-driven, monitoring, stale data, refresh]
rationale: Learn about changes without spamming the source: get told when you can, poll politely when you can't, and keep cached data honest about its age.
---

<!-- contract-receipt: thistle-tidemark-roost -->

# Events and Caching

## In short

Take changes from events (webhooks, change streams) where they exist; poll
as a fallback, within the source's limits. Never show cached data as if it
were current: it carries the time it was true.

## Applies when

- You keep a copy of, or watch, something another system owns: a sync job, a dashboard, a webhook receiver, a cache.
- Not this contract's job: how you make the calls themselves (see calling-other-services), or agreeing versions (see versions-and-discovery).

## Rules

1. Prefer the event mechanism where offered; poll only as a fallback, and document the per-integration choice and its reason. (MUST)
2. Poll within documented limits: honor rate limits and `Retry-After`, use conditional requests (`ETag`), back off on errors, and pick intervals from the source's guidance — not from impatience. (MUST)
3. A cached value knows its age: it carries the time it was observed, and re-showing it as current is a defect (see the floor, rule 1). (MUST)
4. Bound staleness: set a TTL, let writers invalidate what they change, and always give readers a refresh path. (MUST)
5. Staleness is a state you can say: when data is past its age bound or the source is unreachable, report it as `stale`, not as healthy or as an error. (MUST)
6. Verify a webhook's authenticity (signature or shared secret) and acknowledge it promptly; do the work after the response, not inside it. (MUST)
7. Treat a webhook payload as a notification, not as truth: re-read the source before any consequential action. (MUST)
8. Expect duplicate deliveries: make handlers idempotent, so redelivery changes nothing (see calling-other-services). (MUST)
9. Expect missed events: run a periodic full reconciliation to catch what push missed. (MUST)
10. Don't retry-storm a provider whose webhook endpoint is down; back off like any failing call. (MUST)

## Examples

- Good: a status row shows "healthy" and "checked 30s ago" next to one that says "stale — last successful check 3 days ago; source unreachable since".
- Good: a webhook arrives, the receiver checks its signature, answers 202 immediately, queues the work, and re-reads the resource before acting.
- Bad: polling every 5 seconds an API that documents 60 requests per hour, or trusting a webhook body as final state.

## Why

Impatient polling gets integrations rate-limited or banned; blind trust in pushed payloads gets them exploited; caches without an age quietly mislead dashboards. Saying how old data is keeps every reader — human or machine — honest about what's observed and what's remembered.

## You're done when

- Every cached value carries an observed time, and the UI or output shows its age.
- Webhook handlers verify signatures, ack fast, and survive duplicate delivery.
- A reconciliation pass exists for every event-driven path.
- The poll-vs-event choice is written down, per integration, with its reason.

## Machine notes

A cached item is at least: `{ "observed_at": "<UTC timestamp>", "ttl_seconds": <n>, "source": "<system or endpoint>" }`. Webhook receivers need: signature verification, a fast 2xx ack, a work queue, and a reconciliation schedule. Report `stale` per the shared status words (see the floor, rule 8).
