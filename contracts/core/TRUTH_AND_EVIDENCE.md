---
contract_id: truth-and-evidence
title: Truth and Evidence
version: 1.0.0
status: canonical
layer: core
applies: [engineering, agents, operations, testing]
triggers: [always, verification, reporting, status, claims]
rationale: Systems drift into failure when reports are trusted as reality. Make honesty cheaper than fabrication by tying claims to evidence and treating UNKNOWN as a first-class, valid state.
---

<!-- contract-receipt: wren-loam-sail -->

# Truth and Evidence

## Purpose

Make honesty cheap. Truth must be easier to discover than to fabricate, for humans and agents alike. A claim about a system's state is worth exactly the evidence behind it.

## NORMATIVE RULES

1. `UNKNOWN` is a valid state. Never silently convert it into `healthy`, `PASS`, or `complete`.
2. Running is not working. Implemented is not verified. HTTP 200 is not proof of correctness. A process being up is not evidence it does its job.
3. An agent report is evidence about what an agent said, not proof of what happened. Current evidence outranks historical reports, summaries, and remembered conclusions.
4. Every consequential claim carries its evidence: the file, log, test, command output, or live query that produces it.
5. Do not fabricate plausible detail. If a value, name, SHA, or count is not observable, report it as unknown rather than guessing.
6. Never present inferred state as observed state. Label them distinctly.
7. Verification uses the authoritative source, not a mirror, cache, or downstream copy, unless the mirror's freshness is itself verified.
8. A check that has not run in the current context is `UNKNOWN`, regardless of how green it was last time.

## RATIONALE

The single most repeated lesson across this ecosystem (Personal World, VEFR, homelab, rylee_lore): confident summaries drift from reality, and drift compounds silently until something breaks at the worst moment. Fabrication must be more expensive than observation — structurally, not morally.

## HUMAN EXAMPLES

- A dashboard that says "healthy" must have actually checked something recently, and must say `stale` or `unknown` when it hasn't.
- "The deploy went fine" is not done. "The deploy went fine; `GET /healthz` returned 200 at 14:02 and the version endpoint reports the new build" is done.
- "I don't know" from a tool should be treated as useful information, not a failure to hide.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Status values come from the shared vocabulary (`schema/status.schema.json`); no surface invents its own.
- Statuses carry `observed_at` timestamps and `source` provenance so age is checkable.
- Verifiers prefer live queries over stored results; stored results carry their observation time.
- APIs must not return cached data marked as fresh.

## GOOD EXAMPLES

```json
{"status": "unknown", "observed_at": null, "source": "healthcheck",
 "note": "never checked; not run in this session"}
```

```json
{"status": "healthy", "observed_at": "2026-09-11T14:02:00Z",
 "source": "GET /healthz", "warnings": []}
```

## ANTI-PATTERNS

- `status: "Service seems okay :)"` — unverifiable, unparseable.
- Defaulting status fields to `healthy` before any check runs.
- Treating a CI badge from yesterday as today's truth.
- An agent asserting "all tests pass" without naming the command it ran.
- Silently substituting the last known value when a check fails.

## ACCEPTANCE CHECKS

- Can a reader distinguish observed, inferred, and unknown states in every report?
- Does every status carry a checkable source and observation time?
- Is any `healthy`/`PASS`/`complete` claim traceable to current evidence?
- Would a deliberately wrong claim be caught by the system, or only by vigilance?