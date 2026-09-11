---
contract_id: worker-contract
title: Worker Contract
version: 1.0.0
status: canonical
layer: agents
applies: [agents, automation]
triggers: [agent-work, delegation, parallel-work]
rationale: A worker gets everything needed to succeed bounded: base SHA, branch/worktree, owned files, objective, contracts, context, acceptance criteria, exclusions, and authority. The worker inspects, implements, tests, inspects its diff, and reports evidence.
---

<!-- contract-receipt: dell-opal-ember -->

# Worker Contract

## Purpose

Define the bounded handoff from foreman to worker: what the worker receives, what the worker does, what the worker may not do, and what the worker reports.

## NORMATIVE RULES

### What the worker receives (complete, or the task is not ready)

1. Base SHA and repository state; branch and/or worktree.
2. Owned files and paths (the whole scope of permitted mutation).
3. The bounded objective with acceptance criteria and tests.
4. Applicable contracts (loaded, attested) and relevant context (spec sections, schemas, prior evidence).
5. Exclusions: what is explicitly out of scope.
6. Authority: push/merge/deploy permissions, if any; default none.
7. Model/provider/tools and budget (see Model Routing).

### What the worker does

8. The worker loop:
   ```text
   inspect → implement → test → inspect own diff → report evidence
   ```
9. Inspect first: read the owned files' current state and the acceptance criteria before writing.
10. Test what was implemented; run the named tests (or add them); evidence is the output, not the assertion.
11. Inspect the own diff before reporting: no unintended files, no scope creep, no leftover debris.
12. Report evidence: exact commands, exact results, honest grades, unknowns preserved as UNKNOWN.

### What the worker may not do

13. No mutation outside owned paths; no surprise refactors; no contract reinterpretation without escalation.
14. No claiming completion without the named tests passing at the claimed SHA; no silently upgrading evidence grades.
15. No expansion of authority; ambiguity fails closed and is reported as a blocker (it is a valid stop state).

## RATIONALE

Bounded worker instructions produced reliable parallel results where vague briefs produced rework. Every element of the receiving packet exists because its absence caused a real failure: stale base SHAs (conflicts), unclear ownership (two workers, one file), missing acceptance criteria (unverifiable "done"), unspecified exclusions (helpful scope creep), assumed authority (unauthorized pushes).

## HUMAN EXAMPLES

- A worker packet: "Base `abc123`, branch `feat/t12-status-chip`, own `frontend/src/primitives/StatusChip.tsx` + its test. Objective: render canonical statuses with luminance-only tint + word. Acceptance: vitest suite green; axe-clean story. Exclusions: no token changes. Authority: push branch only." — the worker cannot wander, and success is checkable.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Worker packets are structured data (same fields as Bounded Work's definition block).
- Harness-enforced owned-path boundaries where the platform allows.
- Report templates with evidence-grade fields; UNKNOWN required-not-optional.
- Integration is explicitly NOT the worker's job (see Orchestration) — worker-green ≠ integration-green.

## GOOD EXAMPLES

```yaml
worker_packet:
  base: 51c912a
  branch: feat/t12-status-chip
  owned: [frontend/src/primitives/StatusChip.tsx, tests/StatusChip.test.tsx]
  objective: "StatusChip renders canonical statuses; word + luminance tint; no color-only meaning"
  acceptance: ["vitest run tests/StatusChip.test.tsx → green", "axe: 0 serious"]
  contracts: [accessibility-floor, explicit-state]
  exclusions: ["design/tokens.json", "shared shell"]
  authority: {push: branch, merge: false, deploy: false}
  budget: {model: fast-14b, max_tokens: 24000}
```

## ANTI-PATTERNS

- "Improve the frontend" as a worker packet.
- A worker discovering acceptance criteria by feedback.
- Owned paths listed but unenforced.
- A worker "helpfully" fixing a neighboring file.
- Reports that assert results without commands.

## ACCEPTANCE CHECKS

- Does every delegated task carry all packet fields?
- Can the worker succeed without asking questions it should have had answered up front?
- Is every report's evidence traceable and honestly graded?
- Are exclusions and authority enforced, not just stated?