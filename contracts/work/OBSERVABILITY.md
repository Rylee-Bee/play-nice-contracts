---
contract_id: observability
title: Observability
version: 2.0.0
status: canonical
layer: work
applies: [services, tools, agents, automation, apis]
triggers: [logs, logging, monitoring, metrics, tracing, diagnostics, health check, error message, debug, alert, incident]
rationale: Logs and status surfaces exist so the next person or agent can diagnose a failure without reverse engineering it or leaking secrets while doing so.
---

<!-- contract-receipt: kettle-vane-daisy -->

# Observability

## In short

Write logs for whoever debugs next, arriving cold: what happened, in
what component, on whose behalf, with a way to follow one action
across services. Errors say what to try next. Secrets never appear.

## Applies when

Running services or automation that produce logs, errors, health
endpoints, or status displays. Reporting honest status words is the
floor (rule 8); this is about the machinery behind them.

## Rules

1. Every log line carries the basics: timestamp, component, actor, and
   the source of the claim. Structured where useful, human-readable
   where useful. (MUST)
2. An error names what failed, in which component, with what context,
   and points at the next thing to check. `Error: failed` is not an
   error message. (MUST)
3. Keep a correlation or request id across services so one action can
   be followed from surface to dependency and back.
4. Secrets never enter logs. Redact headers, tokens, and payload fields
   structurally, and show the redaction (`token=***`) rather than
   dropping it in silence (see the floor, rule 11). (MUST)
5. Prefer a summarized structured record over a raw payload dump. When
   the full payload is genuinely needed, keep it reachable and bounded
   (sampled, size-limited).
6. An automation's actions are logged as that automation — never under
   a human's name, never anonymously.
7. Be quiet about success, complete about failure: routine healthy
   output is short or absent; a failure tells its whole story (see the
   floor, rule 15).
8. Health and status endpoints report observed state with `observed_at`
   and `source`, and never cache success. A service that was not
   checked reports unknown, not healthy (see the floor, rule 8).
   (MUST)
9. Log levels exist and are honored: debug detail is available on
   request, not the default output.

## Examples

- Good: one request id appears in the UI error, the API log, and the
  worker log — the failing call is traceable in three steps.
- Good: a failed deploy logs `image pull failed: auth expired (secret
  reg-pull, last rotated 90d ago)` — the next action is obvious.
- Bad: full request/response dumps at info level, containing a
  bearer token, with no component names anywhere.

## Why

"Check the logs" is only an answer if the logs answer. The recurring
diagnosis pain in every system here was the same trio: no correlation
ids across services, errors that said nothing, and payload dumps that
hid the one relevant line while leaking fields that shouldn't be in a
log at all.

## You're done when

- A newcomer (human or agent) can trace one failing request end to
  end using ids, without asking anyone.
- `grep` for a token or secret shape in your log output finds
  redaction markers, never values.
- The health endpoint says `unknown` when a check hasn't run, and
  stamps `observed_at` when it has.
