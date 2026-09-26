---
contract_id: plain-language
title: Plain Language
version: 2.0.0
status: canonical
layer: surfaces
applies: [humans, agents, ui, apis, clis, docs]
triggers: [wording, copy, error message, error, message, ui text, label, button text, documentation, web page, page, form, screen, ui, cli, api, endpoint, settings]
rationale: Words are part of every surface, so they get the same care as the rest: honest, short, and actionable.
---

<!-- contract-receipt: birch-poplar-stone -->

# Plain Language

## In short

Say what happened, then what to do next, in words a person would use.
Keep every human-facing sentence the shortest one that stays accurate.
A character may have a voice; hiding the truth may not.

## Applies when

Anything meant for a person to read: screen text, messages, errors, button
labels, docs, reports. Not this contract's job: machine shapes (see
one-truth-two-views) or when to interrupt someone (see the floor, rule 15).

## Rules

1. Say what a thing does in a person's words: "Backups", not
   "cron-runner-v2". Provider names are history, not navigation. (MUST)
2. Every message has two parts, in order: what happened, then the next
   step. Never "Something went wrong." (MUST)
3. Name destructive actions by verb and consequence: "Delete these 3
   snapshots — permanent". Never a vague OK / Yes / Proceed. (MUST)
4. Pick the shortest wording that stays accurate: familiar words, easy to
   scan, easy to remember. Don't add words to sound formal or technical.
   (MUST)
5. Before calling human-facing text finished, cut repeated explanations,
   throat-clearing openings, and paragraphs that could be one sentence.
   Keep what correctness, safety, or operation needs. (MUST)
6. Truth before tone: never make the system sound more certain or capable
   than the evidence says (see the floor, rule 1), and don't polish wording
   over broken behaviour — record the product problem instead. (MUST)
7. Shape the reading: short sentences, lists and tables over prose walls,
   no ALL-CAPS headings. (SHOULD)
8. No manufactured urgency: no guilt, countdowns, streaks, or "don't
   leave!" patterns. (MUST)
9. Empty states are honest and helpful: "No journal entries yet", not fake
   data or a blank mystery. Say in words when something is not set up,
   unreachable, or broken. (MUST)
10. Humor and voice are welcome where they help someone understand —
    characters may have a voice — but never carry operational meaning or
    mask uncertainty. (SHOULD)
11. Keep machine identifiers stable behind the human wording, so the words
    can improve without breaking anything (see one-truth-two-views).
    (MUST)

## Examples

- Good: "Couldn't reach the backup service. Last good backup: yesterday
  23:00. [Retry] [View service]"
- Good: "Certificate expires in 2 days. Renewal is automatic; no action
  needed."
- Bad: "Are you sure?" on both reset and delete; "Error 500 occurred.";
  "OOPS! The elves spilled your data." as the only explanation.

## Why

Every ambiguous button becomes a support ticket, and every vague error
becomes an investigation. Plain, honest, short words are the cheapest way
to respect the reader's attention.

## You're done when

- A newcomer can act on every message without asking anyone.
- Every destructive control names verb and consequence on its label.
- No copy invents urgency, data, or confidence the system doesn't have.
- Each message survived one shortening pass without losing accuracy.
