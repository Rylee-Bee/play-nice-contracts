---
contract_id: attention-and-quiet
title: Attention and Quiet
version: 2.0.0
status: canonical
layer: people
applies: [ui, agents, notifications, workflows, sites]
triggers: [notification, notifications, alert, alerts, badge, toast, popup, reminder, dashboard, monitoring, interrupt, interruption, resume, resumable, session]
rationale: A person's attention is borrowed, not owned; healthy systems spend almost none of it, and pausing and coming back is designed for, not suffered.
---

<!-- contract-receipt: pewter-lark-wicker -->

# Attention and Quiet

## In short

Routine success costs no attention; only things needing a person interrupt.
Write down whatever a person would otherwise have to remember. Interruption is
normal; coming back must be easy.

## Applies when

- You design notifications, dashboards, alerts, agent reports, or any flow a
  person may leave and rejoin.
- Not this contract's job: what a message says (see what-why-next); how loud
  motion or sound is (see sensory-safety).

## Rules

1. **Exceptions get attention.** Attention flows to what needs a person;
   nobody parses a wall of green to find the one red (see the floor, rule 15).
2. **Announce changes, not observations.** Notify on state changes and
   thresholds; a repeated healthy check stays silent.
3. **"Nothing needed" is a state.** Render it explicitly and stop there: no
   daily all-clears, no unprompted recounting of finished work.
4. **Quiet means checked.** Only verified-healthy may be silent; anything
   unverified shows `unknown`, never calm (see the floor, rule 8).
5. **Batch the routine.** Aggregate ordinary events ("3 capabilities
   updated"); surface each exception singly, with what, why and next.
6. **No manufactured urgency.** No streaks, unread-count pressure, guilt copy
   or countdowns; more possible work is not more required work.
7. **Don't store state in people.** Anything they could forget — hidden state,
   unfinished steps, past decisions, whether an action succeeded — is written
   down where they can see it.
8. **First screen answers three questions.** What needs me? What was I working
   on? What's coming up? One attention list beats forty equal cards.
9. **Shape the reading load.** Lists and tables over walls of prose; long
   content behind disclosure (see depth-on-demand).
10. **Progress persists as it happens.** Long flows checkpoint during work,
    not only at completion; a closed session or a crash is not data loss.
11. **Leaving is always safe.** No flow traps anyone: no forced linear wizard
    without exit, no "don't close this page"; drafts and partial choices
    survive.
12. **Returning costs no archaeology.** After a pause or restart, current
    state, completed work, open questions, decisions made, last verified point
    and next action are findable.
13. **Handoffs work cold.** Whoever picks up a task gets the same picture the
    last person left (see the floor, rule 10).
14. **Announcements are polite.** Screen-reader and notification announcements
    are batched and rare; routine refreshes never chatter.

## Examples

- Nightly backup ran fine: no message. Backup failed: one item with what, why
  and next.
- A five-step setup closed at step 2 reopens at step 2: "Step 3 of 5 done;
  next: choose a provider."
- Not: a persistent "947 unread" badge; an agent reporting every routine
  success with the urgency of a failure.

## Why

Attention is the scarcest thing a person brings. Alert fatigue devalues every
real alert, and work that cannot be resumed after an interruption is simply
lost. A system that remembers on the person's behalf and speaks only when
spoken to serves the hurried and the deeply focused alike.

## You're done when

- A fully healthy day costs near-zero attention: count the messages, aim for
  none.
- "Nothing needed" renders explicitly when true, and never disguises
  `unknown`.
- Kill a session mid-flow: reopening finds state, completed work and the next
  action.
- Every batchable event is batched; each exception stands alone with what,
  why and next.
