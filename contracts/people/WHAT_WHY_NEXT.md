---
contract_id: what-why-next
title: What, Why, Next
version: 2.0.0
status: canonical
layer: people
applies: [ui, agents, notifications, workflows]
triggers: [status, progress, summary, report, results, empty state, completion, done, error message, message, explanation]
rationale: Every important state and message answers the same three questions, and finished work is allowed to stay finished.
---

<!-- contract-receipt: rook-marble-twill -->

# What, Why, Next

## In short

Every important state and message answers: what happened, why it matters,
what's next — including "nothing needed". Done is a real state: say it, mean
it, keep it.

## Applies when

- You write status displays, reports, notifications, error text or agent
  summaries, or define what "finished" means for a flow.
- Not this contract's job: when to interrupt a person (see
  attention-and-quiet); the shared status word list (see the floor, rule 8).

## Rules

1. **Answer the three questions.** Every important state, event and message
   answers: what is happening; why it matters, when that isn't obvious; what
   can happen next.
2. **"Nothing needed" is a first-class answer.** Say it plainly; never invent
   urgency to fill the space.
3. **Information design, not layout.** The questions must be answerable from
   the surface; no surface owes three labeled boxes.
4. **State, then reason, then action.** Lead with the human fact, never with
   the button.
5. **Use the reader's words.** Name what's happening in the reader's
   vocabulary, not vendor internals (see the floor, rule 12).
6. **Errors keep the shape.** What failed, why if known, what still works,
   whether it's safe to retry, and the next action.
7. **Reports inherit it.** Agent and automation reports start with what needs
   the reader, not a recounting of everything done.
8. **Progress means getting closer.** Show movement toward a defined finish (5
   → 3 → 1 open; degraded → repaired → verified), not activity volume.
9. **Done is said, and it sticks.** When the acceptance criteria are met, the
   task is complete and says so; a finished task does not silently reopen —
   good new ideas become backlog instead.
10. **Defer visibly.** Park unfinished or optional work with a reason
    ("deferred: waiting on X"), never by quiet scope creep.
11. **Let people finish.** There is a state where nobody is needed, and
    reaching it counts as success, not abandonment.
12. **Progress displays tell the truth.** No forever-80% bars, vanity metrics
    or completion theater; "complete" only after verification (see the floor,
    rule 7).

## Examples

- "Nightly backup finished with 1 warning. One snapshot took 42 minutes
  (usually 3) — likely disk contention. Nothing needed; watch for a repeat
  tomorrow."
- "Migration complete: all routes verified on the new system. Deleting the old
  system is a separate, explicit action."
- Not: "Something happened!"; a button with no statement of what the thing is;
  a to-do list where finishing one item spawns three.

## Why

When a surface answers what, why and next, a reader can act without
investigating, triage without panicking, and stop without guilt. Closure
discipline — define the criteria, recognize the finish, park later ideas — is
what lets a tired person trust a system at the end of the day.

## You're done when

- For each important state or event, a reader can answer what, why and next
  without research.
- "Nothing needed" appears, and means it, when true.
- You can point to where "finished" is for the main flow; reaching it is
  recognized, and it stays finished.
