---
contract_id: setup-checks-itself
title: Setup Checks Itself
version: 1.0.0
status: canonical
layer: surfaces
applies: [tools, ui, services, agents]
triggers: [setup, onboarding, install, configure, settings, connect a, connection setup, provider setup, first run, api key, sso, integration setup]
rationale: A setup that ends in "should work now" is a guess, so every setup offers a real check the person can run on the spot.
---

<!-- contract-receipt: harvest-web-thistle -->

# Setup Checks Itself

## In short

Every setup screen or command offers a check using the person's own
details, and says plainly what worked and what to fix. Nothing is marked
working until its check passed. Nobody needs a config file to get there.

## Applies when

You build any first-run path: adding a provider, connecting an account,
installing a service, wiring an integration. Not this contract's job:
ongoing status reporting (see the floor, rule 8) or error wording in general
(plain-language).

## Rules

1. Every setup path ends in a check the person runs right there, against
   their own key, account, or server — not instructions for proving it
   later. (MUST)
2. The check answers in plain words: what worked, what didn't, and what
   to do next — written for the same reader at any tech level. (MUST)
3. Show real data back, not a tick: the models the key can actually
   call, the version you connected to, one sample record, the room's
   first card. (MUST)
4. Nothing counts as configured, working, or complete until its check
   passed; before that it reads `not_configured` or `unknown` (the
   floor, rule 8). (MUST)
5. A failed check names the fix, and the setup stays open for a retry
   after the person changes something; never send them hunting for a
   docs page. (MUST)
6. Settings the setup needs are offered in the screen or command itself;
   editing a config file is an expert shortcut, never the only path.
   (MUST)
7. Re-checking is cheap: provide a Refresh action (or equivalent
   command) that re-runs the check after any change. (SHOULD)
8. The same check works machine-side (`--json` or API), so an agent or
   script can confirm what a human clicked (see one-truth-two-views).
   (MUST)

## Examples

- Good: an AI provider setup lists the models that key can actually call
  after pressing Refresh; a mistyped key gets "The provider rejected
  this key. Check it and try again."
- Good: SSO ends with a live test sign-in naming who signed in and where
  it stopped; a room install shows `contract: room/0` and one real card,
  not "installed ✓".
- Bad: "Save and restart; if it doesn't work, see the docs."

## Why

Setup is where hopeful claims cost the most: a green badge on a broken
connection sends a tired person down an hour of guessing. A check with
the person's own details turns "it should work" into "it worked — here's
what I saw".

## You're done when

- Every setup path has a visible, runnable check on the spot.
- No step requires opening or editing a config file.
- Nothing reads working until its check passed, human or machine side.
- A first-time person can describe what failed without asking anyone.
