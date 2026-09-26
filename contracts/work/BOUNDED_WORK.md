---
contract_id: bounded-work
title: Bounded Work
version: 2.0.0
status: canonical
layer: work
applies: [agents, automation, workflows, humans, project-management]
triggers: [task planning, scope, budget, stop conditions, autonomous work, integration, merge, parallel lane, defer, backlog, done criteria]
rationale: A job with a defined finish can be finished; a job without one grows until someone pays to stop it.
---

<!-- contract-receipt: garnet-spindle-marigold -->

# Bounded Work

## In short

Every job has one goal, limits, and named stop conditions. Stopping at
a stop condition is success. Parallel work merges one lane at a time
and is re-tested as a combined whole.

## Applies when

Starting substantial or autonomous work, and merging finished work
back together. For the fields of a delegation packet, see
orchestration; this contract covers the bounds and the merge.

## Rules

1. Before work starts, write down its bounds: objective, starting
   revision, owned paths, budget (time, tokens, spend, retries),
   acceptance checks, stop conditions. (MUST)
2. "Autonomous" means finish this job. It never means keep going until
   nothing can be improved.
3. When a stop condition is met, stop and report the state. An honest
   waiting, blocked, unknown, or deferred record is success, written
   down rather than apologized for (see the floor, rule 9).
4. A useful discovery outside the bounds becomes a recorded DEFERRED
   item with a reason. The task does not grow in silence. (MUST)
5. Set acceptance checks before or early in implementation. When they
   are met, the job is explicitly done — done beats additionally
   awesome.
6. Parallel lanes touch disjoint files. Anything shared gets one owner
   and runs alone while the others wait. (MUST)
7. Integration is serial and in dependency order. When two lanes
   changed the same seam, one lands and the other rebases on the
   fresh truth.
8. Worker-green is not system-green: test the combined state at the
   integration revision before claiming done. (MUST)
9. Review the real diff that will merge, not a summary of it, at the
   integration revision.
10. Rejection is normal. Record why a lane failed, then reassign or
    fix it; a rejected lane is a reroute, not a catastrophe.
11. Merge authority is separate from push authority, and both come
    from the task. Integration is a named gate with a record, not a
    habit.
12. Where consequences are real — release, deleting old systems,
    product acceptance — a human decides (see the floor, rule 6).
13. State the evidence grade for integration results like any other
    result: "CI TESTED at 4f2a1c", not "should be fine" (see
    testing-and-evidence).

## Examples

- Good: an agent asked to fix one flaky test fixes it, runs the suite,
  stops, and records two unrelated discoveries as DEFERRED — instead of
  refactoring half the app.
- Good: three UI lanes merge one at a time; after each merge the shared
  suite runs; the third rebases because the tokens changed underneath.
- Bad: merging all branches at once and hoping, because each lane was
  green on its own.

## Why

The costliest pattern seen here was "improve things" sessions: good
work growing faster than anyone could close it. Bounding is what makes
ambition finishable, and serial integration is what keeps several
correct lanes from combining into one broken system.

## You're done when

- Every substantial task states objective, scope, authority, budget,
  and stop conditions before it starts.
- Stopping produced a recorded state, not an apology or a cover-up.
- The combined state was tested at the integration revision, and the
  reviewed diff is the diff that merged.
