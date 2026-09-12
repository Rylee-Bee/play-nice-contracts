---
contract_id: orchestration
title: Orchestration
version: 1.1.0
status: canonical
layer: agents
applies: [agents, project-management]
triggers: [agent-work, multi-agent, batch-work]
rationale: The owner/architect/foreman/worker separation: expensive reasoning becomes durable constraints, the foreman owns current truth and integration, workers execute bounded tasks, and deterministic gatekeepers enforce what can be enforced. The foreman does not blindly trust workers.
---

<!-- contract-receipt: echo-quartz-hollow -->

# Orchestration

## Purpose

Encode the strongest orchestration model learned: an Owner, an Architect/exception auditor, an Orchestrator/foreman, bounded Workers, and a Deterministic gatekeeper — each with explicit responsibilities and non-responsibilities.

## NORMATIVE RULES

### The Owner (human)

1. The human owner controls: intent, risk, permissions, consequential product decisions, and final acceptance. Everything else in this contract is machinery serving the owner.

### The Architect / exception auditor (expensive reasoning, used sparingly)

2. Expensive reasoning is spent on: architecture, contradictions, cross-system boundaries, security, difficult product decisions, and final convergence. It is not spent re-deriving what is already written down.
3. The architect produces durable artifacts: contracts, schemas, tests, decision rules, acceptance criteria. Expensive reasoning is converted into durable constraints — never repeatedly repurchased.
4. The architect audits exceptions: worker conflicts, spec-implementation contradictions, boundary disputes. Bounded execution does not re-litigate settled architecture.

### The Orchestrator / foreman (owns the running job)

5. The foreman owns: current truth (fresh inspection, not stale reports), contract loading, decomposition, dependency ordering, worker assignment, model selection per task, branch/worktree ownership, integration, verification, progress state, stop conditions, and the final handoff.
6. The foreman does not blindly trust workers: worker reports are evidence about the worker; integration and combined-state verification are the foreman's own responsibility (worker-green ≠ integration-green).
7. The foreman assigns bounded tasks: base SHA, branch/worktree, owned files, objective, applicable contracts, context, acceptance criteria, tests, exclusions, and authority. Parallelism is granted only where ownership is clear; shared foundations (shell, router, tokens, core schema, shared clients, policy, canonical contracts) get one owner. Independent leaves may parallelize; integration is serial; combined state is tested.

### The Worker

8. A worker receives the bounded instruction and executes:
   ```text
   inspect → implement → test → inspect diff → report evidence
   ```
9. A worker stays in its lane: owned paths only, no surprise scope expansion, honest evidence in the report, stop conditions respected (see Worker Contract).
10. A worker does not silently escalate scope or interrupt the human directly when blocked: it returns `WORKER STATE: NEEDS_HELP` with a structured question (play-nice/question-v1; see Ask for Help). The foreman decides whether to answer from known state, query another tool or service, ask a specialist agent, or ask the human owner. The foreman reduces interruption noise; workers help by asking good questions, not loud ones.

### The Deterministic gatekeeper

10. Tests, schemas, Git, validators, and CI enforce what can be enforced mechanically. Reasoning becomes tests where reasonable (see Deterministic First); what a machine can check, no human or model re-checks by eye.
11. Human acceptance gates exist where consequences are real (release, destructive action, product acceptance — see Authorization): the machinery proposes; the human decides.

## RATIONALE

This is the consolidation of the Fable-derived framework (owner/architect/foreman/worker separation) with later lessons: expensive reasoning converted into durable constraints (specs instead of re-derivation), bounded autonomous execution with explicit budgets and stop conditions, parallel workers with serialized integration, current evidence over reports, and human acceptance gates. It exists because unconstrained "smart agent does everything" produced rework, conflicts, and invisible failures — while this division repeatedly produced verifiable results.

## HUMAN EXAMPLES

- A migration is decomposed: architect writes the spec + acceptance tests once; foreman assigns three bounded screen-tasks to fast workers with one shared-foundation owner; CI integrates and verifies serially; owner accepts at the final zoom gate.
- Two workers both need the design tokens: foreman serializes that dependency, parallelizes the leaf screens.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Task assignments are data (see Bounded Work fields), not prose.
- Integration is a distinct step with its own verification (combined-state suite).
- Stop conditions and budgets are machine-checkable where possible.
- The foreman's progress state is durable and resumable (see Interruption and Resumption).

## GOOD EXAMPLES

```text
owner: "land the P1 shell"
architect: spec + primitive contracts + acceptance criteria (once)
foreman: decomposes → 6 bounded tasks; 2 parallel lanes on leaves;
         tokens/shell lane serialized; integrates; runs combined suite
workers: implement + test + report evidence per lane
gate: CI green at integration SHA; owner accepts at human gate
```

## ANTI-PATTERNS

- One agent told to "do the whole project" with no decomposition.
- Workers assigned overlapping ownership of shared foundations.
- The foreman trusting green worker reports without integration testing.
- Re-running the expensive architect for every bounded task instead of writing the constraint down.
- Machinery that makes consequential decisions with no human gate.

## ACCEPTANCE CHECKS

- Are the five roles distinguishable in the current setup?
- Is expensive reasoning producing durable artifacts?
- Is integration verified as combined state?
- Are human gates present where consequences are real?