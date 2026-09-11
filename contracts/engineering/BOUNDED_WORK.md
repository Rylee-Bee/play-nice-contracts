---
contract_id: bounded-work
title: Bounded Work
version: 1.0.0
status: canonical
layer: engineering
applies: [agents, project-management, workflows]
triggers: [always, task-planning, autonomous-work]
rationale: "Autonomous" means "finish this bounded job", not "continue until no possible improvement remains". Define the objective, ownership, budget, and stop conditions before work starts; stop honestly when they're met or blocked.
---

<!-- contract-receipt: meadow-willow-cedar -->

# Bounded Work

## Purpose

Make every piece of work — human, agent, or automation — a bounded job with explicit scope, ownership, budget, and stop conditions.

## NORMATIVE RULES

1. Before substantial or autonomous work, define:
   ```text
   base SHA / starting state
   branch / workspace
   objective
   task range (in-scope items)
   owned paths
   dependencies
   applicable contracts
   model/provider/tools (for agent work)
   budget (time, tokens, spend, retries)
   tests / acceptance criteria
   push authority
   merge authority
   deploy authority
   stop conditions
   ```
2. "Autonomous" means: finish this bounded job. It never means: continue until no possible improvement remains.
3. Stop, preserve state, and report when: the objective is complete; further work has sharply diminishing value; a human decision is required; evidence is insufficient; two authoritative sources conflict; the next action would materially increase risk; verification cannot currently be completed.
4. Stopping with an honest `WAITING` / `BLOCKED` / `UNKNOWN` / `DEFERRED` state is preferable to manufacturing progress. The state is recorded, not apologized for.
5. Separately useful discoveries become recorded backlog items (`DEFERRED` with a reason) — they do not silently expand the task.
6. Acceptance criteria are defined before or early in implementation; when met, the original task is explicitly done (done beats additionally awesome — see Progress and Closure).
7. Worker-green is not integration-green: work integrates and is tested as a combined state before claiming done (see Review and Integration).

## RATIONALE

Unbounded "improve things" sessions produced the highest-cost failure pattern observed in this ecosystem: worthwhile work expanding faster than closure mechanisms could consume it. Bounding work is not a limit on ambition — it is what makes ambition finishable. Honest stop states are the alternative to fabricated progress.

## HUMAN EXAMPLES

- An agent asked to "fix the failing test" fixes the test, runs the suite, and stops — recording two unrelated discoveries as DEFERRED, rather than refactoring half the app.
- A maintenance window ends with "objective complete; 1 item deferred (reason recorded)" rather than "still improving things".

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Task/workflow objects carry objective, scope, authority, budget, and stop conditions as data.
- Agents emit stop-state reports on completion or blockage (truth report format).
- DEFERRED items are a first-class recorded state with reason and (optionally) a proposed home (roadmap, issue list).

## GOOD EXAMPLES

```yaml
task:
  objective: "Fix flaky test_dashboard_reflow"
  scope: ["tests/test_dashboard.py"]
  authority: {push: branch, merge: none, deploy: none}
  budget: {max_iterations: 3}
  stop: [suite-green, irreproducible-after-3-attempts]
```

## ANTI-PATTERNS

- "Make everything better" as a task.
- An agent that "found one more thing" and reopened a merged lane.
- Stop conditions that exist only in the operator's head.
- Treating DEFERRED as failure.

## ACCEPTANCE CHECKS

- Does every substantial task have objective, scope, authority, budget, stop conditions?
- Is completion recognized when criteria are met?
- Are discoveries recorded without scope expansion?
- Are honest stop states representable and respected?