---
contract_id: deterministic-first
title: Deterministic First
version: 1.0.0
status: canonical
layer: engineering
applies: [architecture, agents, operations]
triggers: [always, new-subsystem, workflow-design, automation-design]
rationale: Use deterministic machinery when it suffices; use AI for judgment. Ordinary deterministic operation must never acquire an undocumented AI requirement.
---

<!-- contract-receipt: tundra-maple-orchard -->

# Deterministic First

## Purpose

Keep the deterministic substrate deterministic. AI is for interpretation, reasoning, synthesis, and assistance — not an invisible requirement for ordinary operations.

## NORMATIVE RULES

1. Good deterministic owners: validation, permissions, policy, state transitions, approvals, synchronization, parsing, file movement, canonical transforms, schema enforcement, CI, verification.
2. AI's jobs: interpretation, reasoning, synthesis, generation, assistance, anomaly explanation, planning.
3. Never place model calls inside deterministic surfaces (exports, validators, parsers, journals, transforms): the deterministic path stays deterministic, testable, and offline-runnable.
4. Ordinary deterministic operation must not depend on any AI/model service: boots, validates, exports, and verifies without a model configured. An AI outage may remove assistance; it may not remove operation.
5. Where AI touches state, it proposes; deterministic governance validates and commits. The world remembers what actually happened, not what a model suggested (AI proposes; the system governs).
6. AI-generated content that becomes durable truth is committed to canonical storage with provenance (see Stable Truth, Provenance).
7. Prefer the smallest mechanism that solves the demonstrated problem; promote something into an AI workflow only when repetition or complexity justifies it.

## RATIONALE

VEFR's rule — "keep deterministic surfaces deterministic" — and homelab's "retire complexity when its burden exceeds its value" converge here. Model-dependent boot paths are fragile in exactly the low-connectivity, high-stakes moments where reliability matters; model-dependent validators are untestable; and every implicit AI dependency quietly becomes an AI-vendor dependency (see Stable Truth).

## HUMAN EXAMPLES

- A world export builds offline, byte-identical, in seconds — no model, no network.
- An AI assistant suggests a config change; the deterministic validator is what accepts or rejects it.
- The system works fully during a model-provider outage, minus chat/summarize.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- CI runs the deterministic gate (tests, validators, schema checks) with zero model access — proving no hidden dependency.
- AI calls exist only at explicit "generative edges" (assistance surfaces), behind provider seams.
- Propose-validate-commit: AI output passes through deterministic enforcement before touching state.
- Determinism is testable: repeat runs produce identical outputs (reproducible builds/exports).

## GOOD EXAMPLES

```text
export.py  — deterministic, no model calls, byte-identical reruns
assistant  — optional model surface over the same world
```

## ANTI-PATTERNS

- A validator that asks a model "does this look valid?"
- Export/backup that needs an embedding provider reachable.
- AI deciding state transitions with no deterministic commit gate.
- "It works when the AI is configured" as the definition of working.

## ACCEPTANCE CHECKS

- Does the system boot, validate, and export with all AI disabled?
- Are generative calls absent from deterministic code paths (verifiable)?
- Is repeated deterministic execution reproducible?
- Can any AI output reach durable state without a deterministic gate? (Must be no.)