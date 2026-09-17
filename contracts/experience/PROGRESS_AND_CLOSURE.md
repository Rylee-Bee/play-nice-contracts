---
contract_id: progress-and-closure
title: Progress and Closure
version: 1.0.0
status: canonical
layer: experience
applies: [ui, product, agents, workflows]
triggers: [human-facing-work, workflows, agents]
rationale: Reward real accomplishment. The user should be allowed to finish. Engagement mechanics that manufacture infinite work are hostile to the people they claim to serve.
---

<!-- contract-receipt: inkstone-tundra-cedar -->

# Progress and Closure

## Purpose

Let people finish. Show real progress toward real completion, and make "done" an achievable, celebrated, durable state.

## NORMATIVE RULES

1. Reward real accomplishment: unresolved→resolved counts falling, degraded→repaired→verified transitions, setup incomplete→complete. Progress is movement toward a defined finish, not activity volume.
2. Avoid: engagement streaks, arbitrary points, guilt, artificial urgency, and infinite work queues masquerading as productivity. Human attention is not an engagement metric. Labels such as "Needs you" must mean that meaningful human judgment or action is actually required. A healthy result may be "No action needed" (see Human Reliability).
3. Completion is explicit: when acceptance criteria are met, the task is done and said to be done. Done beats additionally awesome; new good ideas become backlog items unless they fix a real defect.
4. A finished task does not reopen silently. Reopening is a visible decision, or new ideas park on a roadmap.
5. The system allows the user to finish: there exists a state where nothing needs the person, and reaching it is success, not abandonment.
6. Work has bounded scope: bounded objectives, stop conditions, and explicit defer paths (DEFERRED with a reason, not silent scope expansion).
7. Progress displays are truthful: 80%-done-forever bars, vanity metrics, and completion theater are defects.

## RATIONALE

Closure discipline — defining acceptance criteria, recognizing when they're met, and parking genuinely good new ideas rather than reopening finished work — was the single highest-value collaboration lesson recorded in this ecosystem. Systems should enforce it structurally so people don't have to enforce it by willpower.

## HUMAN EXAMPLES

```text
5 unresolved → 3 → 1 → done.
degraded → repaired → verified.
setup incomplete → complete.
NEXT: nothing required.
```

- A setup checklist where completed steps stay visibly completed and the last step ends the flow — it doesn't spawn a new list.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Task and workflow objects carry acceptance criteria and completion states (`complete` only with verification, `partial` where honest).
- Agents classify discoveries into defect / required-for-acceptance / later-improvement, defaulting to a backlog record.
- No dark-pattern metrics: no streaks, no points, no "you're leaving work undone!" copy.

## GOOD EXAMPLES

- "Migration complete: 100% of routes verified on the new system. Old system deletion is a separate explicit action."

## ANTI-PATTERNS

- A "You're on a 12-day streak!" banner.
- Infinite todo waterfalls where finishing one item spawns three.
- A progress bar that sits at 90% for a week.
- "Done... except for these 14 follow-ups" with no defer path.

## ACCEPTANCE CHECKS

- Can a user reach and recognize "finished"?
- Is completion tied to verification rather than activity?
- Can new ideas be parked without reopening the task?
- Are any engagement mechanics present? (Remove them.)