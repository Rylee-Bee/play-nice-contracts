---
contract_id: explicit-state
title: Explicit State
version: 1.0.0
status: canonical
layer: core
applies: [ui, api, cli, agents, operations]
triggers: [status-reporting, state-modeling, always]
rationale: Nobody should have to infer operational state from the absence of errors. Explicit, distinct states make systems legible to humans, agents, scripts, and future tools at once.
---

<!-- contract-receipt: driftwood-thicket-jetty -->

# Explicit State

## Purpose

Do not make humans, agents, or scripts infer state from silence. Important state is explicit, distinct, and observable — the same vocabulary everywhere.

## NORMATIVE RULES

1. Use the shared status vocabulary (`schema/status.schema.json`): `healthy, warning, needs_attention, degraded, unavailable, not_configured, disabled, stale, unknown, working, waiting, blocked, deferred, partial, complete`.
2. Do not collapse distinct states into each other: unavailable ≠ not_configured; unknown ≠ healthy; stale ≠ current; disabled ≠ failed; working ≠ complete.
3. Absence of errors is not health. If nothing has been checked, the state is `unknown`.
4. Where several states apply at once, surface the composite honestly ("degraded, two of five providers unreachable") rather than picking a misleading average.
5. The state word is the signal; color, icon, and position are reinforcement only, never the sole carrier.
6. Human interfaces may translate the vocabulary into plain language, but the machine vocabulary remains stable beneath.
7. Long operations expose intermediate states (`working`, `waiting`, `blocked`) rather than appearing frozen or silently continuing.

## RATIONALE

Personal World's status vocabulary proved that one closed vocabulary can serve a UI, a CLI, an API, and agent tooling at once — and that honest distinctions (a vacancy is not a failure) prevent both panic and complacency. State that must be inferred gets inferred wrong at the worst time.

## HUMAN EXAMPLES

- "Not configured yet" instead of a scary red failure on a feature nobody set up.
- "Last checked 3 days ago — this may be out of date" instead of showing stale data as current.
- "Waiting on approval from Rylee" instead of a task that looks stuck with no explanation.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- One closed vocabulary module shared by all surfaces (CLI, API, UI, agent tools); none invents local synonyms.
- Provider-specific states are mapped into the vocabulary at the adapter boundary.
- Statuses carry `observed_at` and `source` so freshness is machine-checkable.
- The rank order for "worst wins" composition is defined once, in the vocabulary module.

## GOOD EXAMPLES

```json
{"status": "needs_attention", "observed_at": "2026-09-11T14:00:00Z",
 "source": "provider-probe", "detail": "certificate expires in 2 days"}
```

## ANTI-PATTERNS

- A green dot as the only health indicator.
- Treating "no data yet" as healthy.
- One generic "error" state that erases the difference between misconfiguration, outage, and missing config.
- A spinner that stays for ten minutes with no intermediate state.
- Re-showing the last successful observation as current.

## ACCEPTANCE CHECKS

- Does every surface use the shared vocabulary?
- Can a newcomer distinguish "broken", "not set up", and "not checked" in this system?
- Is every displayed state paired with when it was observed?
- Do long operations expose progress states?