---
contract_id: complexity-on-demand
title: Complexity on Demand
version: 1.0.0
status: canonical
layer: human
applies: [ui, product, docs, agents]
triggers: [human-facing-work, information-design, documentation]
rationale: Do not eliminate useful complexity; organize it. A beginner needs a clear path and an expert needs to drill all the way down. Those are not contradictory requirements.
---

<!-- contract-receipt: anchor-window-willow -->

# Complexity on Demand

## Purpose

Make complexity navigable. Keep deep technical capability in the system, but control when it enters attention. A beginner or low-attention user has a clear path; an expert can drill all the way down.

## NORMATIVE RULES

1. Use a depth ladder. Present the smallest useful amount first, then permit deeper inspection:
   - **LEVEL 0 — GLANCE:** What matters right now?
   - **LEVEL 1 — UNDERSTAND:** What happened? Why?
   - **LEVEL 2 — TECHNICAL:** Logs, provenance, versions, API state, models, timings, dependencies, configuration, policies.
   - **LEVEL 3 — SPECIALIST:** Hand off rare/advanced operations to the specialist tool that genuinely owns them.
2. Progressive disclosure organizes complexity; it never removes it. Meaningful summaries must not become dead ends — every level links down to the next.
3. The calm view must not depend on hiding important truth (see Human Reliability). Hidden ≠ gone: any suppressed state is reachable and its existence is not secret.
4. Depth is reachable by everyone: no "debug mode" that requires credentials, build flags, or institutional knowledge for ordinary drill-down.
5. Do not force irrelevant complexity into attention: a settings page for one toggle does not need the full config schema on screen.
6. When depth is requested, give real depth: raw or near-raw responses, timings, and policy decisions — where safe — not a second summary pretending to be detail.

## RATIONALE

The tension between "simple for beginners" and "powerful for experts" is false; it is resolved by controlling when complexity enters attention rather than deleting capability. Systems that hide depth force experts to fight them; systems that expose everything exhaust beginners.

## HUMAN EXAMPLES

- A health row that says "needs attention — certificate expires in 2 days" and expands to the full probe log on request.
- A chat answer that shows, on demand, which model, which tools, which API calls, and how long each took.
- A "Guide me" button beside every complex workflow, without making every interaction a wizard.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- UIs implement a consistent disclosure mechanism (native `details`/`summary`, drawers, dedicated technical views).
- Every important object has a provenance/detail route at Level 2.
- Level 3 hand-offs are explicit deep links to specialist tools with context preserved where possible.
- Docs follow the same ladder: quickstart → explanation → reference → internals.

## GOOD EXAMPLES

```text
LEVEL 0: "Backups: healthy"
LEVEL 1: "Last backup 2h ago, 1.2 GB, verified"
LEVEL 2: schedule, retention policy, last 10 runs with timings, target endpoint, restore procedure
LEVEL 3: "Open the backup service console"
```

## ANTI-PATTERNS

- A settings page showing the entire config schema at once.
- "Advanced" sections that are actually required for basic operation.
- Summary cards with no path to the underlying data.
- Detail views that are only reachable by URL archaeology.
- Removing technical views to "reduce clutter", leaving only a marketing summary.

## ACCEPTANCE CHECKS

- Can a newcomer complete the primary task seeing only Level 0–1?
- Can an expert reach Level 2 for any important object within two interactions?
- Is any summary a dead end?
- Does hiding ever remove the existence of important truth? (Must be no.)