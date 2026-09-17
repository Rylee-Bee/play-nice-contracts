---
contract_id: failure-and-degradation
title: Failure and Degradation
version: 1.1.0
status: canonical
layer: interoperability
applies: [api, ui, operations, agents]
triggers: [error-handling, always, api-design]
rationale: Optional failure must not destroy unrelated capabilities, and errors must tell the truth: what failed, why, what still works, what's safe, what's next. Shared state vocabulary makes degradation legible everywhere.
---

<!-- contract-receipt: sigma-hazel-cedar -->

# Failure and Degradation

## Purpose

Make failure honest, contained, and useful. Systems degrade legibly instead of failing confusingly; errors answer real questions; one broken part never takes down the working whole.

## NORMATIVE RULES

1. Adopt the shared semantic status vocabulary (`schema/status.schema.json`): `healthy, warning, needs_attention, degraded, unavailable, not_configured, disabled, stale, unknown, working, waiting, blocked, deferred, partial, complete`. Projects map provider-specific states into it at the adapter boundary.
2. Preserve the distinctions: unavailable ≠ not_configured; unknown ≠ healthy; stale ≠ current; implemented ≠ verified; running ≠ correct.
3. Optional failure must not destroy unrelated capabilities. One provider's outage degrades its capability; it does not crash the dashboard, corrupt state, or fail sibling features.
4. Errors answer:
   ```text
   WHAT happened?
   WHAT changed or did not change?
   WHAT still works?
   IS anything unsafe?
   CAN it be retried?
   WHAT is the next reasonable action?
   WHERE is technical detail available?
   ```
   Errors support recovery, not blame. Never blame the person. Do not expose implementation errors as the primary human message when a useful translation exists (see Copy and Language). Do not promise unchanged state or recoverability unless verified.
5. Machine interfaces return stable error identifiers (`provider_unreachable`, `not_authorized`, `version_mismatch`); human interfaces translate them into useful language (see Copy and Language). Never reduce a meaningful error to "Something went wrong."
6. Partial success is representable: a multi-item operation reports per-item outcomes, not all-or-nothing when both are possible and honesty demands per-item truth.
7. Degrading systems stay inspectable: the degraded state, its reason, and its last verified point are visible (Level 2 detail), not guessed.
8. No fake success: a swallowed error is a defect, whatever its short-term convenience.

## RATIONALE

The Personal World status vocabulary and "provider failure is not core failure" conformance tests came from real outages where one dead integration blanked an entire dashboard. Honest degradation is containment for attention as much as for availability: the reader can see what still works and act only on what matters.

## HUMAN EXAMPLES

- One unreachable provider renders its row as `unavailable` with "last seen 2h ago"; every other row works.
- A save that failed for 2 of 7 items says exactly which 5 saved, which 2 failed, and why.
- "The backup service is not configured. Everything else is fine. [Set up backups]"

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Error envelopes: stable `error` identifier + structured context + retryability flag, uniformly shaped across surfaces.
- Status composition rule ("worst wins") defined once in the vocabulary module.
- Circuit-breakers/timeout budgets per integration so a hung provider cannot hang the page.

## GOOD EXAMPLES

```json
{"ok": false, "error": "provider_unreachable",
 "provider": "gitea", "retryable": true,
 "still_works": ["memory", "journal"], "next": "Check Gitea, or retry."}
```

## ANTI-PATTERNS

- A single dead widget blanking the whole UI.
- "Something went wrong" on a known, classifiable failure.
- All-or-nothing batch APIs where per-item truth exists.
- Swallowed exceptions logged as "handled".
- Treating unconfigured as failed.

## ACCEPTANCE CHECKS

- Kill any single dependency: does everything unrelated keep working and stay visible?
- Does every error answer the six questions?
- Are error identifiers stable across releases?
- Is partial success expressible where it exists?