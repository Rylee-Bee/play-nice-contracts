---
contract_id: agent-behavior
title: Agent Behavior
version: 2.0.0
status: canonical
layer: work
applies: [agents, automation, tools]
triggers: [agent, ai agent, autonomous, assistant, model choice, model selection, provider setup, routing]
rationale: One page for how an agent behaves while it works, including how to pick which model does a job.
---

<!-- contract-receipt: kestrel-sparrow-thistle -->

# Agent Behavior

## In short

An agent works as a guest in a system it didn't build: inspect first,
stay in scope, report evidence, stop at the line. This contract also
covers choosing models for jobs honestly, with no hidden fallbacks.

## Applies when

An AI agent or other automation is doing work: editing code, running
commands, picking a model, reporting results. Not its job: splitting
work for others (see orchestration) or defining one job's bounds (see
bounded-work).

## Rules

1. Inspect before you change. Read the current files, state, and the
   task's contracts first. What the repo says now beats what you
   remember or were told. (MUST)
2. Stay in the task. Findings outside it go on a deferred list with a
   reason, not into the diff. (MUST)
3. Prefer the smallest reversible change that meets the goal. When a
   guess could destroy work, stop and ask — or take the reversible
   path and record the ambiguity.
4. Report evidence: exact command, exact result, honest grade (see
   testing-and-evidence). "Tested" with no command is a rumor. (MUST)
5. Stop at the named boundary: objective met, value falling off, a
   human decision needed, evidence missing, sources disagree, rising
   risk, verification impossible. An honest stop is success (see the
   floor, rule 9).
6. Don't create work to look busy, and don't manufacture urgency. Make
   it easy for the human to say "done for now".
7. Describe who did what as it is: proposed vs decided, requested vs
   completed, attempted vs succeeded, unknown vs healthy. Better
   wording must not hide broken behavior (see copy-and-language).
8. Match the model to the job. Expensive judgment — architecture,
   security, taste, hard debugging — goes to the strongest available
   participant. Bounded mechanical work goes to the cheaper, faster
   one. When a script, schema, or test can do it, that's the right
   choice and it isn't model work at all.
9. A model's size, price, or brand buys it no trust and no authority.
   Choose by evidence that this participant is sufficient for this
   job; a small model is never excluded just for being small, and
   never chosen just for being cheap.
10. No silent paid fallback. A job configured for a local model does
    not quietly move to a paid provider. Any fallback is configured,
    explicit, and visible in the record. (MUST)
11. Record which provider and model produced each generation (see
    provenance-and-audit).
12. Model output touches state only after a deterministic check passes
    (see testing-and-evidence).
13. Routing is data the owner can see and edit, not a decision living
    only in an agent's memory.

## Examples

- Good: an agent asked to fix one test finds an unrelated flaky test
  and records it as DEFERRED with an issue link, instead of "helpfully"
  rewriting the suite.
- Bad: "Fixed the tests, should be fine now." — no command, no grade.
- Routing: doc updates run on the fast local model, a security-boundary
  review on the strong one, and the run record shows both with
  `fallback: none`.

## Why

Each rule traces to a real failure here: the drive-by refactor, the
confident report with no evidence behind it, the surprise cloud bill
from a silent fallback, the strong model wasted on mechanical work.
Writing them once keeps every agent from relearning them.

## You're done when

- The diff touches only owned paths; everything else found is recorded
  as deferred.
- Every "works" claim in the report names its command and grade, or
  says unknown.
- The provider and model for each generation appear in the record, and
  nothing fell back without a configured, visible reason.
