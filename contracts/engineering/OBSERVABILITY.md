---
contract_id: observability
title: Observability
version: 1.0.0
status: canonical
layer: engineering
applies: [operations, api, infrastructure, agents]
triggers: [logging, monitoring, always-for-services]
rationale: Logs and diagnostics are for diagnosis: structured where useful, human-readable where useful, timestamped, attributable, secret-free, correlated, and explicit about source. Errors should help without requiring reverse engineering.
---

<!-- contract-receipt: quay-cinder-window -->

# Observability

## Purpose

Make failures diagnosable by the next person, agent, or session — without reverse engineering, without leaking secrets, and without drowning in noise.

## NORMATIVE RULES

1. Logs and diagnostics are: structured where useful, human-readable where useful, timestamped, attributable, appropriately classified, free of secrets, useful for correlation, and explicit about source.
2. Correlation/request IDs are preserved where the platform supports them: a request can be traced from surface to dependency and back.
3. Errors are diagnostic: they state what failed, in which component, with what context, and they point toward the next investigation step (see Failure and Degradation's six questions).
4. No secrets in logs — ever (see Secrets). Headers, tokens, and payloads are redacted structurally, with the redaction visible (`token=***`), not silently.
5. Avoid logging enormous raw payloads when summarized structured data is sufficient; keep the full payload reachable at Level 2/3 when genuinely needed (sampled, bounded).
6. Attribution: log lines name the actor or component that produced them (an automation's actions are logged as that automation).
7. Health endpoints and status surfaces are honest: they report observed state with `observed_at`/`source`, distinguish quiet from unknown, and never cache success (see Truth and Evidence).
8. Observability follows the depth ladder: a human-readable summary at Level 0/1; structured detail at Level 2; raw dumps only in specialist tooling.

## RATIONALE

"Check the logs" is only an answer if the logs answer. The recurring diagnostics pain in every system here was: multi-service failures with no correlation IDs, errors like `Error: failed`, and full payload dumps that hid the one relevant line and leaked fields they shouldn't.

## HUMAN EXAMPLES

- One request ID appears in the web UI error, the API log, and the worker log — three clicks to root cause.
- A failed deploy logs "image pull failed: auth expired (secret `reg-pull`, last rotated 90d ago)" — next action obvious.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Structured logging with stable event kinds; request-ID middleware; redaction filters at the log boundary.
- Log levels exist and are honored (debug for Level 2 surfaces, not the default firehose).
- Health endpoints: `/healthz`-class, build identity included, `observed_at` in payloads.
- Log retention/rotation configured; logs are not a secret store's neighbor.

## GOOD EXAMPLES

```json
{"ts": "2026-09-11T14:02:11Z", "level": "warn", "request_id": "7f3c",
 "component": "backup", "actor": "scheduler", "event": "provider_timeout",
 "provider": "s3", "after_ms": 30000, "next_hint": "check network or creds"}
```

## ANTI-PATTERNS

- `Error: something failed` with no component, context, or correlation.
- Full request/response dumps at INFO level.
- Tokens or API keys in log lines.
- One global log with no attribution.
- Health endpoints that return cached healthy.

## ACCEPTANCE CHECKS

- Can a newcomer trace one failing request end to end?
- Do logs name the component and actor?
- Are secrets structurally impossible to log?
- Is there a human-readable summary path that isn't a wall of grep?