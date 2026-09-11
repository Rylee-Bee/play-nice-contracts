---
contract_id: attention-and-focus
title: Attention and Focus
version: 1.0.0
status: canonical
layer: human
applies: [ui, agents, product, workflows]
triggers: [human-facing-work, workflows, notifications]
rationale: Control when complexity enters attention. A person may want simplicity one hour and extreme depth the next; support both. This is not a dumbed-down mode — it is information design.
---

<!-- contract-receipt: kindle-inkstone-timber -->

# Attention and Focus

## Purpose

Design for limited, variable, and interruptible attention. The core insight is not "make things simple" — it is **control when complexity enters attention**. The same person may sometimes want simplicity and sometimes want extremely deep complexity. Support both.

## NORMATIVE RULES

1. Do not call this a "dumbed-down mode". Depth is never removed from the system — its entrance into attention is controlled.
2. Externalize memory: systems must not require people to remember hidden state, the previous step, unfinished tasks, previous decisions, ownership, why something matters, whether an action succeeded, what changed, or what is next. Important context belongs in the environment.
3. The default surface answers, in order: What needs me? What was I working on? What is coming up?
4. Attention flows toward exceptions, not routine success. The operator should never parse walls of green to find the one red.
5. No manufactured urgency: backlog size, remaining agent context, unfinished ideas, and operator capability must not become artificial pressure. The existence of more useful work does not mean more work is currently required.
6. Reading load is shaped: tables and lists over prose walls; predictable static layouts; no walls of text (long content behind disclosure or dedicated views).
7. Interruption is a design input, not an exception: people get interrupted, sessions end, machines restart. After resumption, current state, completed work, incomplete work, relevant decisions, unresolved questions, last verified point, and next useful action must be identifiable without archaeology.
8. One obvious path over several equivalent paths; progressive disclosure organizes depth (see Complexity on Demand).

## RATIONALE

Attention is the scarcest resource a human brings to any system. A design that spends it uniformly (all items equally loud) or greedily (everything needs you NOW) fails both the person in a hurry and the person in flow. Externalizing memory and structuring attention is what makes systems usable across energy, mood, and interruption.

## HUMAN EXAMPLES

- A home view with one attention list, not forty equal cards.
- An interrupted setup flow that says "Step 3 of 5 done; next: choose a provider" when reopened.
- A "resume where I was" affordance after every session-scoped activity.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Attention-item APIs: an explicit, ranked "what needs me" surface distinct from "everything".
- Workflow state is persisted at each meaningful step with next-action information.
- Notification systems default quiet: batch, summarize, and rate-limit announcements (e.g. ≤1 polite live-region announcement per ~30 seconds, batched).
- Agents end with what-why-next style truth reports; "nothing required" is representable.

## GOOD EXAMPLES

```text
WHAT: Deploy finished for service "web".
WHY IT MATTERS: This closes the incident from this morning.
NEXT: Nothing needed. 2 warnings recorded, viewable in history.
```

## ANTI-PATTERNS

- "947 unread items" as a persistent badge.
- Streaks, guilt copy, arbitrary points, countdown pressure.
- Burying the one failing check under 200 passing ones with identical visual weight.
- Wizard-only flows that cannot be resumed or exited safely.
- A UI that punishes leaving (state lost on navigation).

## ACCEPTANCE CHECKS

- Is the single most important thing findable in the first screen-second?
- Does anything require remembering what isn't written down?
- Is attention drawn to exceptions rather than routine success?
- Can an interrupted flow be resumed from where it stopped?