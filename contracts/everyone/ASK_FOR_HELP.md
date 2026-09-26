---
contract_id: ask-for-help
title: Ask for Help
version: 2.0.0
status: canonical
layer: everyone
applies: [humans, agents, services, tools, automation]
triggers: [blocked, ambiguous, unclear, question, decision, uncertain, approval, intent, escalation]
rationale: Asking the participant who owns an answer is safer, cheaper, and kinder than guessing, and a good question is resumable state.
---

<!-- contract-receipt: moss-taper-reed -->

# Ask for Help

## In short

When someone else can answer more safely, cheaply, or accurately, ask
instead of guessing. Ask the right one, once, with your recommendation —
and record the question until it's answered.

## Applies when

You're blocked, uncertain, or about to decide something that isn't yours.
The floor already says don't invent what you can ask or look up, ask the
one who knows, and treat waiting as a fine place to stop (see the floor,
rules 2, 3 and 9); this contract is how.

## Rules

1. **Don't ask what you can find out.** In order: inspect known state;
   consult the applicable contracts; use safe deterministic discovery;
   then ask the owner of the answer. (MUST)
2. **Route to whoever owns the answer.** Humans: intent, preference,
   approval, acceptable risk, ambiguous ownership. Services: capability,
   version, limits, current resource state. Other agents and tools:
   specialist inspection. Configuration and code: facts already recorded
   there. (MUST)
3. **In a delegation chain, workers ask their coordinator, not the
   human.** Return a structured needs-help with the question; the
   coordinator answers, re-routes, or asks up, and reduces interruption
   noise on the way. (MUST)
4. **Refusal is a valid answer.** unsupported, insufficient-context,
   low-confidence, and out-of-scope are legitimate states alongside
   needs-help, without penalty; you may also offer the smaller piece you
   can do reliably. (MUST)
5. **A good question carries what an answer needs:** what you need, why
   you're asking, what you already checked, who can answer, whether
   you're blocked, what happens if nobody answers, and your
   recommendation. The asker does the investigation, not the answerer.
   (MUST)
6. **Make it one cheap decision.** Prefer labeled options with a
   recommendation ("A — existing API; B — new webhook; recommended: A")
   over a story to reconstruct. One decision at a time for humans; stable
   identifiers for machines. (MUST)
7. **A question is state, not scrollback.** Record it with requester,
   target, reason, evidence, blocking flag, and status — and when it
   lands, the answer, who answered, when, and what was done because of
   it. It survives restarts and handoffs. (MUST)
8. **Answers are information, never permission.** Being told which
   cluster is production does not authorize deleting it (see the floor,
   rule 5). (MUST)
9. **Guard attention.** Before interrupting a person: could you, or a
   machine, answer this? Batch compatible non-urgent questions; never
   batch unrelated high-stakes decisions into one questionnaire. (MUST)
10. **Waiting is a clean finish.** A task may end as waiting-for-help
    when further action would need guessing, the missing answer matters,
    and the right one has been asked. Record that as success. (MUST)
11. **Ask systems directly when you can:** capabilities, versions,
    limits, what an identifier refers to. If one system can't do the job
    and another can, delegate — don't rebuild it inside. (SHOULD)
12. **Never put secrets or needless private data in a question** (see
    the floor, rule 11). Ask the minimum necessary. (MUST)

## Examples

- Good: "Two health-check types are valid here and the repo doesn't say
  which is canonical. I checked the deploy config, the API docs, and
  project contracts. Recommendation: HTTP /healthz. OK to use that?" —
  then waits.
- Bad: "I wasn't sure, so I picked TCP." — a guess sold as progress.
- Bad: "How do health checks work?" — asking the human to do the research
  you skipped.

## Why

The most expensive integration failures come from the gap between "I
understand most of this" and "one thing is missing": participants guess
because they can generate an answer. A system that asks well is easier to
integrate, and one that answers well is easier to use.

## You're done when

- Every open question is recorded with its options, recommendation,
  blocking flag, and owner — not just asked in chat.
- Each decision made today rests on evidence or an answered question;
  none rests on a guess.
- If you stopped to wait, you said so, and the state is resumable.

## Machine notes

A question artifact (validated by `schema/question.schema.json`):

```json
{"schema": "play-nice/question-v1", "question_id": "q-01842",
 "requester": "frontend-worker", "target": {"type": "human", "role": "owner"},
 "question": "Which navigation composition governs Settings?",
 "choices": [{"id": "rail", "label": "Left rail"},
             {"id": "top-nav", "label": "Top navigation"}],
 "recommended": "rail", "recommendation_reason": "matches the newer frame",
 "blocking": true, "status": "waiting"}
```

Lifecycle states: open, waiting, answered, declined, expired, superseded,
cancelled. Answered questions store answer, answered_by, answered_at, and
the resulting action.
