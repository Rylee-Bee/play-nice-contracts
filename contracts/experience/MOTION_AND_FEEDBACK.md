---
contract_id: motion-and-feedback
title: Motion and Feedback
version: 1.0.0
status: canonical
layer: experience
applies: [ui, web, product]
triggers: [ui-work, animation, interaction-design]
rationale: Movement communicates state when it is short, purposeful, and optional — and damages usability when it is ambient, essential, or unkillable. Feedback after action is how users know the system heard them.
---

<!-- contract-receipt: gable-fern-velvet -->

# Motion and Feedback

## Purpose

Use motion sparingly as one channel of feedback among several, and make every action's result knowable without motion at all.

## NORMATIVE RULES

1. Feedback follows every consequential action: the result of a click, save, command, or request is observable — visible state change, status message, or explicit confirmation. "Nothing visibly happened" is a defect.
2. Motion defaults to reduced (or off). Nonessential animation is opt-in; OS reduced-motion overrides unconditionally (see Migraine and Sensory Safety).
3. Transitions, where allowed, are short and gentle (sub-300ms, ease-out class), never bounces, spins, shakes, or flourishes.
4. Motion never carries essential meaning: any information in an animation exists statically as well.
5. State-change feedback is honest: it reflects verified state (a "saved" indicator means saved, not "request sent").
6. Announcements are polite and rare: live-region announcements for meaningful, user-relevant changes only, batched, rate-limited; never for routine refreshes or animation states.
7. Loading states are static first (text, static progress indicators); indeterminate motion only where no progress information exists, and always with a static label.
8. Peripheral and ambient movement is restrained; nothing continuously moves on a dense surface by default.

## RATIONALE

Feedback prevents the "did it work?" re-check loop that burns attention; restrained motion protects the sensory-sensitive while still allowing a living interface for those who opt in. The static-first rule guarantees the system is fully usable with motion entirely disabled.

## HUMAN EXAMPLES

- After "Save", the button state changes, a quiet status line confirms, and the timestamp updates — no toast storm.
- A filtered list that re-renders with a 150ms fade (only for users without reduced-motion) and, for everyone, an explicit "showing 3 of 12" label.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- All transitions gated behind `prefers-reduced-motion: no-preference` AND an application motion preference at or above the chosen level.
- Status regions (`role="status"`, `aria-live="polite"`) with batched updates.
- Operation results update canonical state and are verifiable, not merely announced.

## GOOD EXAMPLES

```css
@media (prefers-reduced-motion: no-preference) {
  [data-motion="subtle"] .list-item { transition: opacity 160ms ease-out; }
}
```

## ANTI-PATTERNS

- Shimmer skeletons on every load.
- A spinner as the only loading affordance, forever, with no text.
- "Saved ✓" that fires on request dispatch, not save success.
- Bouncing attention-grabbers.
- Toasts for every routine action.

## ACCEPTANCE CHECKS

- With motion fully off: is every action's result still knowable?
- Does every consequential action produce observable feedback?
- Is any meaning carried only by motion? (Must be no.)