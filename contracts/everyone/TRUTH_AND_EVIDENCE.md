---
contract_id: truth-and-evidence
title: Truth and Evidence
version: 2.0.0
status: canonical
layer: everyone
applies: [humans, agents, services, tools, automation]
triggers: [evidence, verify, verification, claim, report, unknown, investigation, review]
rationale: Confident reports drift from reality, so every claim needs its evidence and every unchecked belief needs a cheap test before it can steer work.
---

<!-- contract-receipt: kestrel-flint-loom -->

# Truth and Evidence

## In short

Say what you saw, what you think, and what you don't know — and keep those
apart. Before acting on a belief, try once to prove it wrong.

## Applies when

You state a fact, report a result, or plan work that depends on something
you haven't confirmed. The floor already requires marking what you saw and
checking the belief that matters most (see the floor, rules 1 and 4); this
contract says how.

## Rules

1. **Start from unknown.** Classify each consequential claim as observed
   (you saw it, with a named source), inferred (you reasoned it from
   evidence), assumed (you treat it as true without checking), or unknown.
   Label it; don't let "assumed" hide inside a confident sentence. (MUST)
2. **Familiarity is not evidence.** Never promote a claim to believed-true
   just because it is repeated, plausible, or confidently stated. (MUST)
3. **Write the four parts separately for consequential judgments:** who or
   what decides (authority), what was inspected (evidence), what you think
   it means (interpretation), what you will do (decision). None substitutes
   for another. (SHOULD)
4. **Reports say what they measured.** Running is not working; implemented
   is not verified; HTTP 200 is not correctness; an agent's message proves
   what the agent said, not what happened. (MUST)
5. **Check the live source.** Verify against the authoritative source, not
   a mirror or cache, unless the mirror's freshness is itself checked. A
   check that hasn't run in this context is unknown, however green it was
   last time. (MUST)
6. **Passing checks are not understanding.** Existing code proves
   behavior, not intent; treat inherited design as a hypothesis until
   current requirements say it stays. A gate proves only what its checks
   cover. (SHOULD)
7. **Test the belief your plan depends on.** Before dependent action: name
   the biggest unproven belief; say what you would see if it were wrong;
   run the cheapest reasonable check that could show that. A check chosen
   only to confirm the plan doesn't count. (MUST)
8. **Record the attempt.** A few lines: what you checked, what it showed,
   what it can't show, and how it changed the plan. Use an existing note,
   plan, or handoff; add no new ceremony or scores. The record must precede
   the action it clears. (SHOULD)
9. **Inconclusive is not permission.** If a reasonable check is
   unavailable or unclear, keep the unknown, stop or narrow the dependent
   work, and ask (see ask-for-help). Time passing and repetition don't
   turn a belief into a fact. (MUST)
10. **Keep honesty cheap.** "I don't know" and a safe stop are successful
    answers; mistakes stay cheap to recover from with bounded changes and
    a way back (see recovery-and-history). (MUST)

## Examples

- Good: "ASSUMED: both readers accept the new field. Check: replay
  yesterday's traffic against a strict reader. Result: one rejected it;
  switching to dual-write."
- Bad: "I read the approved design, so the old shell must fit it." — no
  check ran that could have proved that wrong.
- Bad: an agent says "all tests pass" without naming the command it ran.

## Why

The costly failures here came from trusting a summary instead of the
system: reports drift, and drift compounds silently until something breaks
at the worst moment. Labeling claims and cheaply testing the load-bearing
one makes honesty easier than a quiet wrong answer.

## You're done when

- Every consequential claim you made is labeled observed, inferred,
  assumed, or unknown.
- Each risky action names the belief it depended on, the check that could
  have disproved it, and the result — or says why no check exists.
- No report calls a stale or unchecked thing current, healthy, or done.
