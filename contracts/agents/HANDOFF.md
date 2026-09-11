---
contract_id: handoff
title: Handoff
version: 1.0.0
status: canonical
layer: agents
applies: [agents, sessions, workflows]
triggers: [session-end, agent-work, context-switch]
rationale: A handoff is a durable file (or payload) that lets the next human OR bot continue cold: what's current, what changed, what's verified, what's unknown, what's deferred, and what's next — plus branch/SHA/tests where relevant.
---

<!-- contract-receipt: cinder-clover-quartz -->

# Handoff

## Purpose

Make the end of any work session a clean transfer to whoever comes next — another human, another agent, another week.

## NORMATIVE RULES

1. Substantial work ends with a handoff following the standard shape:
   ```text
   CURRENT    — verified current state (repo, branch, runtime, deployment as relevant)
   CHANGED    — what actually changed
   VERIFIED   — evidence, with grades and exact commands
   CONTRACTS  — applicable contracts and their status (PASS/FAIL/N/A/UNKNOWN)
   ACCESSIBILITY — relevant verification (for human-facing work)
   INTEROPERABILITY — relevant verification (for interface work)
   SECURITY / OWNERSHIP — relevant verification
   UNKNOWN    — unresolved truth, preserved honestly
   DEFERRED   — parked improvements with reasons
   NEXT       — the single most legitimate next action, or "nothing required"
   ```
2. Where relevant, the handoff also includes: branch, SHA, remote state, worktrees, runtime state, model/provider used, exact tests, and the human gate that remains.
3. The handoff must be resumable by another human OR another bot, cold: no reliance on having been present; no transcript archaeology (see Documentation and Continuity).
4. Handoffs are durable artifacts (files or structured payloads in a known location), not parting chat messages.
5. `NEXT: nothing required` is a successful outcome (see Progress and Closure).
6. Handoff state is honest about grades: `VERIFIED` claims are backed; unverified things appear in UNKNOWN, never padded into VERIFIED.
7. A handoff bundle (when a debug partner is needed) includes: what I was trying to do, what I saw instead, what I've already tried, plus machine-generated context (resolved state, recent events) — so the receiver doesn't re-suggest what was already attempted.

## RATIONALE

VEFR's handoff-bundle format and the session-wrapup standing rule both encode the same discovery: the expensive part of resuming is re-deriving context, and a structured handoff eliminates it. The standard section list exists because every one of those sections answers a question a real continuation needed.

## HUMAN EXAMPLES

- A one-file handoff: any session (human or agent) reads it and continues without asking "where were we?"
- A handoff bundle for a stuck bug lists everything already tried, so the helper doesn't re-suggest restarts.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Handoff documents are a supported output format of agents and tools (a `handoff` command or equivalent).
- Section headers are stable so tools can parse them.
- `nouns doctor`-style verification commands let the receiver re-check the handoff's claims cheaply (trust but verify).

## GOOD EXAMPLES

```markdown
CURRENT: main @51c912a, clean, pushed; runtime: v2.1 deployed, healthy
CHANGED: StatusChip primitive + tests; token luminance encoding
VERIFIED: `pytest -q` 218 passed @51c912a (CI green); axe 0 serious (375/900/1440)
CONTRACTS: accessibility-floor PASS; explicit-state PASS; human-and-machine-parity PASS
ACCESSIBILITY: word+luminance; 200% zoom human gate PASSED (Rylee, 2026-09-11)
UNKNOWN: behavior under forced-colors on Windows (untested)
DEFERRED: dark-variant polish (issue #31, low value)
NEXT: nothing required
```

## ANTI-PATTERNS

- "It's mostly done, ask me anything" as a handoff.
- Handoffs that exist only in scrollback.
- VERIFIED lists containing unrun checks.
- NEXT that opens three new lanes instead of naming one step.
- Omitting what was already tried.

## ACCEPTANCE CHECKS

- Can a cold session continue from the handoff alone?
- Are all sections present and honestly graded?
- Is NEXT exactly one legitimate action (or nothing-required)?
- Is the handoff stored where the next session will find it?