---
contract_id: orchestration
title: Orchestration
version: 2.0.0
status: canonical
layer: work
applies: [agents, automation, workflows, project-management]
triggers: [orchestration, multi-agent, coordinator, delegate, delegation, agent team, parallel work, batch work, assignment]
rationale: Splitting work between people and agents only works when each role, each work packet, and each check is explicit.
---

<!-- contract-receipt: quarry-loom-cypress -->

# Orchestration

## In short

Owner, architect, coordinator, workers, and the deterministic gate:
five roles, each with clear duties. A worker gets a complete work
packet, does its lane, and reports evidence; the coordinator verifies.

## Applies when

Work is split between several participants — people, agents, scripts,
services — or one participant runs a batch. Not its job: the bounds of
a single job and how it merges (see bounded-work).

## Rules

1. Name the five roles for the job: owner, architect, coordinator,
   workers, deterministic gate (tests, CI, validators). On a small job
   one participant may hold several roles; say which.
2. The owner keeps intent, risk, permissions, and final acceptance.
   Everything else is machinery serving the owner. (MUST)
3. Spend expensive reasoning once. The architect turns hard judgment
   into durable artifacts — specs, schemas, tests, acceptance criteria
   — instead of re-deriving settled decisions for every task.
4. The coordinator owns current truth: fresh inspection, not stale
   reports. It decomposes the work, assigns it, integrates it, and
   leaves the handoff.
5. Assign through a complete work packet (rule 6). If a field is
   missing, the task isn't ready: fix the packet instead of letting
   the worker guess. (MUST)
6. A work packet carries: base revision; branch or worktree; owned
   paths; the objective; acceptance checks; exclusions (what is out of
   scope); applicable contracts; authority for push/merge/deploy,
   default none; model/provider and budget.
7. Offer work as a negotiation, not a decree. Ask each participant
   what it does well and what shape of contribution fits. An honest
   "I can't" or "smaller, please" is a valid answer; nobody gets a
   task designed to fail (see contribution).
8. Run work in parallel only where ownership doesn't overlap; shared
   foundations get exactly one owner. Integration then runs serially
   (see bounded-work).
9. The worker loop is: inspect → implement → test → read your own diff
   → report evidence. Stay inside owned paths.
10. A blocked worker asks the coordinator, not the human directly. The
    coordinator answers from known state, queries a tool, or decides
    whether to bring in the owner — so the human hears fewer, better
    questions (see ask-for-help).
11. Rejecting a worker's output is normal: record the reason, fix or
    reassign. No drama, no blame.
12. When workers disagree, the coordinator turns it into one decision:
    claims, evidence, tradeoff, recommendation. The human gets
    information, not an argument to referee.
13. Let machines check what machines can check. Keep a human gate
    where consequences are real — release, deletion, acceptance.
14. The coordinator makes the model choice per task, as configuration
    the owner can inspect and edit (see the routing rules in
    agent-behavior).

## Examples

- A migration: the architect writes the spec and acceptance tests once;
  the coordinator assigns three bounded screen tasks to fast workers,
  keeps the shared tokens on one lane; CI integrates serially; the
  owner accepts at the final human gate.
- Bad: one agent told to "do the whole project" with no decomposition,
  and two workers both editing the token file.

## Why

Unbounded "smart agent does everything" produced rework, collisions,
and invisible failures. Writing down who owns what — and giving every
worker the full packet instead of a hope — repeatedly produced
verifiable results instead.

## You're done when

- Every delegated task carries all the packet fields from rule 6.
- No shared foundation is edited by more than one lane.
- Rejections and their reasons are recorded, and a blocked worker's
  question reached the coordinator, not the human's inbox.
- Combined state was verified by the coordinator, not taken on report.
