---
contract_id: sensory-safety
title: Sensory Safety
version: 2.0.0
status: canonical
layer: people
applies: [ui, web, sites, product]
triggers: [animation, motion, transition, loader, skeleton, spinner, flashing, strobe, shimmer, autoplay, video, audio, sound, haptics, reduced motion]
rationale: Interfaces stay usable for people sensitive to light, motion and sound as plain engineering requirements; start still, keep motion meaningful, never demand it.
---

<!-- contract-receipt: moss-cove-spindle -->

# Sensory Safety

## In short

Start still: no flashing, no ambient motion, no unasked sound. Motion is
allowed only when it means something, stays short, and always has a static
version.

## Applies when

- You add or change motion, sound, loading states or other feedback in a
  human-facing surface.
- Not this contract's job: whether a surface may interrupt a person (see
  attention-and-quiet); labels, contrast and text alternatives (see
  accessibility).

## Rules

1. **Never flash or strobe.** No flashing, rapid luminance swings, or
   blink-to-get-attention effects.
2. **Calm by default.** No full-bleed pure-white glare, no neon visual
   language; long-session comfort is the default look.
3. **Loading is static.** Loaders are text or a static bar by default — no
   shimmer, no pulsing skeletons, no breathing glows. A moving indicator
   belongs only where progress is genuinely unknown, and always with a label.
4. **Nothing moves on its own.** No ambient rotation, background drift or
   bouncing mascots; dense surfaces are still.
5. **Motion that means something.** Where motion exists at all, it explains a
   state change: short (under 300ms), gentle, no bounce, spin, shake or
   flourish.
6. **The system wins.** App motion defaults to reduced or off; every optional
   animation sits behind both `prefers-reduced-motion: no-preference` and the
   app's motion setting (see the floor, rule 14).
7. **Motion carries no exclusive meaning.** Anything an animation shows also
   exists as static text or state; the interface is fully usable with motion
   off.
8. **Acting gets feedback.** Every consequential action produces an observable
   result — visible state change, status line, or explicit confirmation.
   "Nothing visibly happened" is a defect.
9. **Feedback tells the truth.** "Saved" means saved, not "request sent";
   status reflects verified state.
10. **Success is quiet.** Completion shows as a calm static confirmation; no
    confetti, no toast storm.
11. **Sound and vibration are opt-in.** Audio cues, haptics and autoplayed
    sound never fire unbidden and are always easy to turn off.
12. **Comfort never lowers the floor.** Palettes may calm harsh hues (for
    example a high-glare blue range), but contrast never drops below the
    accessibility floor.

## Examples

- A page loads with a static "Loading…"; a filtered list re-renders with a
  160ms fade only when the OS allows motion, and shows "3 of 12" for everyone.
- Saving updates the button state, one quiet status line and a timestamp.
- Not: a pulsing skeleton as the default loader; a spinner as the only sign
  something is happening; "Saved ✓" that fires when the request goes out.

## Why

Loud motion invites the "did it work?" re-check loop that spends attention, and
it excludes people sensitive to light and movement. Still-first interfaces are
simply good long-session engineering: they work for everyone and stay fully
usable with all motion off.

## You're done when

- OS reduced-motion on: zero non-essential animation, and every action's
  result still knowable.
- Every default loading state is static.
- No meaning carried by motion alone; no sound or haptics firing unasked.
- Could someone use this screen for three hours in a dim room without
  discomfort?

## Machine notes

- Gate CSS animation/transition behind `prefers-reduced-motion:
  no-preference` plus the app motion preference; a CI check can flag ungated
  motion.
