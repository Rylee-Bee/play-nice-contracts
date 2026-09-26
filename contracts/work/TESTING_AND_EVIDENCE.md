---
contract_id: testing-and-evidence
title: Testing and Evidence
version: 2.0.0
status: canonical
layer: work
applies: [agents, automation, ci, tools, services]
triggers: [test, tests, testing, verify, verification, evidence, ci check, release, deploy, deployment, flaky, regression, model output, deterministic]
rationale: Every "it works" is a claim with a grade and a command behind it, and the ordinary path should need no model at all.
---

<!-- contract-receipt: hearth-anvil-tamarack -->

# Testing and Evidence

## In short

Use deterministic machinery first; save model calls for judgment.
"It works" is a claim about evidence: name the grade, show the command,
never quietly upgrade one.

## Applies when

Proving anything works, choosing how a check runs, or deciding whether
a job needs a model. Reporting what you saw is the floor's job (rule
7); this is the how.

## Rules

1. Prefer a deterministic mechanism wherever one is enough: a test,
   schema, validator, or script instead of a model guess. Keep model
   use at the edges, where judgment is genuinely the job.
2. Ordinary operation must work with every model turned off: boot,
   validate, export, and verify without a model configured. A model
   outage may take away assistance; it may never take away operation.
   (MUST)
3. No model calls inside deterministic paths — exports, parsers,
   validators, journals stay testable and offline. Where model output
   touches state, it proposes and a deterministic gate validates before
   the commit. (MUST)
4. Never call it "works" merely because: a process started, an endpoint
   returned 200, a test passed somewhere, a worker said complete, a
   file exists, or a screenshot looks right. (MUST)
5. These evidence grades are not equivalent: SOURCE INSPECTED, UNIT
   TESTED, INTEGRATION TESTED, CONTAINER TESTED, CI TESTED, DEPLOYED,
   RUNTIME VERIFIED, BROWSER VERIFIED, HUMAN ACCEPTED.
6. Every "works" claim names its grade and the exact command or
   observation that produced it. "Tests pass" with no command is a
   rumor. (MUST)
7. Never silently upgrade a grade. When in doubt, state the lower one.
   Marking HUMAN ACCEPTED without a human is false evidence. (MUST)
8. Verify at the authoritative source: deployed state at runtime,
   browser behavior in a browser, human-facing quality with a human
   (see the floor, rule 7).
9. A "done" claim requires the full gate — lint, types, tests,
   validators — green at the revision named. CI green is the floor,
   not the ceiling.
10. Worker-green is not integration-green: test the combined state
    after merge (see bounded-work).
11. Flaky tests are defects: fix them, quarantine them with a written
    reason, or delete them. Never train everyone to ignore red.
12. Automated accessibility and browser checks are proxies. Where a
    contract demands a human check — real zoom, real screen reader —
    the human check still happens.
13. Repeating a deterministic run must produce the same output. AI
    output that becomes durable truth is stored with provenance (see
    provenance-and-audit).

## Examples

- Good: "VERIFIED: `uv run pytest -q` → 214 passed (CI run #1832);
  `curl /healthz` → 200, build=abc123 at 14:02Z. Grade: RUNTIME
  VERIFIED. Browser not verified."
- Bad: a release note saying "works" because the container started.
- Good deterministic-first: a backup export that builds byte-identical,
  offline, in seconds — and an assistant that suggests config changes
  the validator then accepts or rejects.

## Why

"Running is not working" is the most repeated lesson in this
ecosystem, and real failures hid behind every grade: 200-but-wrong
payloads, CI-green-but-broken deploys, worker-reported-complete-but-
untested code. Naming the grades makes a quiet upgrade visible, and
keeping models out of the ordinary path keeps systems working when a
provider falls over.

## You're done when

- Every "works" claim in the report names its grade and command.
- The system boots, validates, and exports with all AI disabled.
- No grade was upgraded between the check that ran and the claim made.
- The full gate is green at the exact revision the claim names.
