---
contract_id: guide-me
title: Guide Me
version: 1.0.0
status: canonical
layer: experience
applies: [ui, product, workflows]
triggers: [complex-workflows, onboarding, setup-flows]
rationale: Complex workflows deserve a resumable, explained, one-step-at-a-time path — without turning every interaction into a wizard.
---

<!-- contract-receipt: fern-prairie-gatehouse -->

# Guide Me

## Purpose

Give complex workflows an optional resumable guided path that walks one meaningful step at a time, while ordinary interaction stays direct.

## NORMATIVE RULES

1. A `Guide me` mode may be offered for genuinely complex workflows. It is opt-in; it never replaces direct operation for experts.
2. Do not make every interaction a wizard. Guide Me is for multi-step flows that benefit from explanation, sequencing, and safety.
3. When active, the guide:
   - explains the current step in plain language (what and why);
   - performs or guides one meaningful action, then verifies it;
   - preserves progress — completed steps stay done across interruptions;
   - shows completed steps and remaining steps honestly;
   - exposes technical detail when requested (the guide is a depth path, not a simplification wall);
   - allows leaving at any time with progress intact;
   - allows resumption at the same point;
   - eventually terminates — a guide that never ends is a defect.
4. Guide state is durable and visible: "Step 3 of 5 complete; next: verify connection" survives session restarts.
5. Steps are sized to be independently meaningful; each completed step is real progress toward a defined finish (see Progress and Closure).
6. The same capability beneath the guide is directly operable without the guide, for users who prefer to work unguided.

## RATIONALE

Complexity on Demand demands both a clear path for the hesitant and full depth for the confident. The guide pattern serves the first without gating the second — and resumability (Interruption and Resumption) makes it safe for exactly the low-energy situations where guidance helps most.

## HUMAN EXAMPLES

- "Guide me through connecting a Git provider": five steps — choose provider, enter credentials (with secure handling), verify connection, pick scope, first sync — each verified, resumable, with "leave and come back" explicit.
- A setup flow whose finished state ends the guide rather than spawning more work.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Guide flows are declarative step definitions (id, title, explanation, action, verification, next), persisted with per-step completion state.
- Steps verify their own success (a step is not "completed" because Continue was clicked).
- Direct/unguided operation reaches the same underlying operations — the guide sequences, it does not gatekeep.

## GOOD EXAMPLES

```yaml
guide:
  flow: connect-provider
  steps:
    - id: choose   # explanation + action + verification
    - id: credentials
    - id: verify    # verified by a live probe, not by trust
    - id: scope
    - id: first-run
  resume: true
```

## ANTI-PATTERNS

- Forced linear wizards with no exit and no memory.
- A guide that hides what it actually did.
- Steps that mark themselves complete without verification.
- Guided flows that exist only because the underlying UI is too confusing.
- A never-ending "tips" tour.

## ACCEPTANCE CHECKS

- Interrupt at any step; is resumption exact?
- Is every step verified rather than assumed?
- Can an expert skip the guide and do the same work directly?
- Does the guide end?