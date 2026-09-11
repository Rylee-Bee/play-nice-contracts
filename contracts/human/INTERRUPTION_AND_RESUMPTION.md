---
contract_id: interruption-and-resumption
title: Interruption and Resumption
version: 1.0.0
status: canonical
layer: human
applies: [ui, agents, workflows, sessions]
triggers: [long-running-work, sessions, wizards, orchestration]
rationale: People get interrupted, sessions end, machines restart. Design for that reality or lose work and context to it. After resumption, nobody should need archaeological reconstruction.
---

<!-- contract-receipt: rill-loam-orchard -->

# Interruption and Resumption

## Purpose

Treat interruption as a normal, designed-for event. Whatever the participant — human, agent, session, or machine — resumption must quickly answer where things stand and what comes next.

## NORMATIVE RULES

1. After resumption it must be possible to identify: current state, completed work, incomplete work, relevant decisions, unresolved questions, last verified point, and next useful action — without archaeological reconstruction.
2. Meaningful progress is persisted as it happens, not only at completion. Long flows checkpoint themselves.
3. Leaving is always safe: no flow traps the user (no forced linear wizards without exit, no "don't close this page" cliffs without a persisted alternative).
4. Session end is a normal event, not data loss. Work-in-progress state, drafts, and partial selections survive wherever practical.
5. Resumable flows expose progress visibly: completed steps remain visible, current step is explicit, remaining steps are estimable.
6. Handoffs between participants (human→agent, agent→agent, session→session) carry enough state for the receiver to continue cold (see Handoff contract).
7. Recovery of an interrupted operation never depends on remembering what the screen looked like.

## RATIONALE

Every long system in this ecosystem — deploys, world weaves, frontend migrations, orchestration batches — eventually gets interrupted by sleep, crashes, or context limits. The systems that survived interruptions well were the ones that wrote state down as they went.

## HUMAN EXAMPLES

- A five-step onboarding wizard that can be closed at step 2 and reopened at step 2.
- A resumable "guide me" path through a complex workflow that shows completed steps and the current one.
- An agent session that ends with a handoff document another session can pick up cold.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Workflows persist step state with timestamps (a step journal), not just final results.
- Draft persistence for multi-field inputs where practical.
- Handoff documents are a supported output of long-running work.
- Operations are idempotent or restartable (see Idempotency), so resuming cannot double-apply work.

## GOOD EXAMPLES

```yaml
guide_state:
  flow: provider-setup
  completed: [choose-provider, enter-credentials]
  current: verify-connection
  remaining: [first-sync]
  updated: 2026-09-11T14:00:00Z
```

## ANTI-PATTERNS

- Multi-page forms that reset on navigation.
- "Do not close this window" as the only protection for a long operation.
- Session-scoped wizard state with no persistence.
- Progress that exists only as a browser tab's memory.
- Handoffs that require having been present for the earlier discussion.

## ACCEPTANCE CHECKS

- Kill the session mid-flow; reopen: is the state recoverable?
- Is every long operation resumable or safely restartable?
- Does a second participant get the same picture as the first left with?