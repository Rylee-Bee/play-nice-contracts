---
contract_id: human-reliability
title: Human Reliability
version: 2.0.0
status: canonical
layer: people
applies: [ui, agents, workflows, product]
triggers: [workflow, steps, checklist, task flow, long-running, batch, review, undo, defaults, mistakes, fatigue, handoff]
rationale: A system must stay safe and understandable when the person using it is tired, interrupted or new, not only at their best.
---

<!-- contract-receipt: pebble-thistle-wharf -->

# Human Reliability

## In short

No heroics required: a tired, interrupted or unfamiliar person operates the
system correctly. The system holds the complexity; the person holds the
judgment.

## Applies when

- You design or run any workflow a person operates — especially long, batched
  or risky ones — and any agent that talks to a person.
- Not this contract's job: sensory levels (see sensory-safety); interruption
  and resumption mechanics (see attention-and-quiet).

## Rules

1. **No heroics.** Correct use must not depend on perfect concentration,
   noticing subtle visual differences, remembering undocumented state,
   re-checking healthy things "just in case", or reconstructing why a decision
   was made.
2. **Unnecessary cognitive load is technical debt.** Track it and pay it down
   like any other debt.
3. **Choose the reliable default:** visible state over remembered state; safe
   defaults over perfect recall; explicit uncertainty over false confidence;
   reversible actions over fragile ones; one obvious path over several equal
   ones; automation over repetitive vigilance; natural stopping points over
   endless work.
4. **Write for a strained reader.** Short sentences, stable terms, meaningful
   headings; don't assume maximum working memory (see the floor, rule 12).
5. **A calm surface never hides truth.** Simplicity may fold detail away (see
   depth-on-demand) but never removes or conceals anything important.
6. **Never imply obligation.** "More work is possible" is not "you should
   continue"; a healthy, stable system may stay unchanged, and "no action
   needed" remains a valid, desirable result.
7. **Make pushback cheap and honored.** "Not this way", "not this much", "not
   right now", "show me less", "just the recommendation" are easy to say, and
   the system changes in response — machinery carries the volume, the person
   carries the judgment.
8. **Put checking in the machine.** If safety depends on a person catching a
   subtle change, move that check into the system and have it report in plain
   words (see attention-and-quiet).

## Examples

- Back after a week away, the first screen answers "what needs me" and shows
  where things left off.
- The assistant: "That's done. If you want, there's also X — but nothing needs
  you today."
- Not: success that can only be confirmed by remembering what it looked like
  before; forty checklist items presented with equal urgency.

## Why

Systems are needed most when people are at their worst — tired, interrupted,
distracted, new. An interface that works only at peak capacity fails exactly
when it matters, and a person paying for it with vigilance is quietly doing
the system's own job for it.

## You're done when

- A tired person completes the main flow correctly on the first try.
- Nothing critical depends on anyone's working memory.
- "No action needed" is representable and actually respected.
- A returning person can find "what needs me" in under a minute.
