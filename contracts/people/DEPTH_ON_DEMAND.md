---
contract_id: depth-on-demand
title: Depth on Demand
version: 2.0.0
status: canonical
layer: people
applies: [ui, product, docs, workflows]
triggers: [docs, documentation, help, onboarding, guide, wizard, tutorial, settings, advanced, details, disclosure, reference, walkthrough]
rationale: Useful complexity is kept, not deleted; it is organized so a beginner has a clear path and an expert can drill all the way down.
---

<!-- contract-receipt: garnet-birch-spire -->

# Depth on Demand

## In short

Keep the depth; control when it shows. Smallest useful amount first, honest
steps down to full detail, and an optional guided path for genuinely complex
flows.

## Applies when

- You build docs, help, settings, onboarding, wizards, or any surface with
  technical depth behind it.
- Not this contract's job: accessibility of the controls (see accessibility);
  what a message answers (see what-why-next).

## Rules

1. **Organize complexity, don't delete it.** A depth ladder: a glance (what
   matters now); understanding (what happened, why); technical detail (logs,
   versions, policies, timings); specialist tools. Show the rung the moment
   needs, and let the person go deeper.
2. **First view stands alone.** The default screen is understandable with
   nothing expanded.
3. **No dead-end summaries.** Every level links down to the next, and "show
   more" reveals real detail — raw or near-raw data, timings, policy
   decisions where safe — never a second summary pretending to be detail.
4. **Disclosure is for depth, not secrets.** Anything material to safety or
   ownership is visible by default; folding never means hiding.
5. **One disclosure mechanism.** Prefer native (`details`/`summary`, `dialog`,
   `popover`, anchor links); fully keyboard and screen-reader usable (see
   accessibility); coming back lands where you were.
6. **No forced complexity.** A one-toggle page doesn't show the whole schema;
   one coherent task isn't split across five collapsed panels to look minimal.
7. **Lead with human meaning.** Order: what happened or matters → what the
   person can do → what they need to know to do it safely → implementation
   detail. Ordinary use never depends on knowing APIs, protocol vocabulary or
   backend shape.
8. **Depth is open to everyone.** Drilling down needs no special credentials,
   debug build or inside knowledge.
9. **Guides are optional.** Offer a "guide me" path for genuinely complex
   multi-step flows; it never replaces direct operation, and experts can do
   the same work unguided.
10. **No wizards for everything.** Simple work stays direct; a guide that
    never ends is a defect.
11. **Steps are real and verified.** Each guided step explains what and why in
    plain words, performs one meaningful action, and verifies it; clicking
    "Continue" is not success (see the floor, rule 7).
12. **Guides survive interruption.** Progress persists, leaving is safe, and
    resuming lands at the same point (see attention-and-quiet).
13. **Docs climb the same ladder.** Quickstart, then explanation, then
    reference, then internals — the reference is one link from the summary.

## Examples

- A row says "Backups: healthy". Open: "last run 2h ago, 1.2 GB, verified".
  Open further: schedule, retention policy, the last 10 runs with timings,
  restore steps.
- "Guide me through connecting a Git provider": choose provider → credentials
  → verify connection (a live probe, not trust) → pick scope → first sync;
  each step verified, resumable, skippable.
- Not: an "Advanced" section holding fields the basics actually require; a
  settings page that dumps the full config schema at once.

## Why

"Simple for beginners, powerful for experts" is a false fight: it settles by
controlling when complexity enters attention. Systems that delete technical
views make experts fight them; systems that dump everything exhaust everyone
else; summaries that go nowhere break trust.

## You're done when

- A newcomer completes the main task seeing only the glance and understanding
  levels.
- An expert reaches full technical detail for any important object within two
  interactions.
- Every expandable summary shows exactly what it claimed; no dead ends.
- Every guide can be left, resumed, skipped, and finished.
