---
contract_id: testing-and-verification
title: Testing and Verification
version: 1.0.0
status: canonical
layer: engineering
applies: [engineering, agents, ci]
triggers: [always, verification, release]
rationale: Never say "works" because a process started, an endpoint returned 200, or a worker said complete. Evidence is graduated and honestly labeled — these grades are not equivalent.
---

<!-- contract-receipt: prairie-yarrow-quartz -->

# Testing and Verification

## Purpose

Make "it works" a claim about evidence, not vibes. Distinguish grades of proof and never silently upgrade one to another.

## NORMATIVE RULES

1. Never declare "works" merely because: a process started; an endpoint returned 200; a test somewhere passed; a worker said complete; a file exists; a model answered; a UI screenshot looks right.
2. Distinguish — these are not equivalent:
   ```text
   SOURCE INSPECTED
   UNIT TESTED
   INTEGRATION TESTED
   CONTAINER TESTED
   CI TESTED
   DEPLOYED
   RUNTIME VERIFIED
   BROWSER VERIFIED
   HUMAN ACCEPTED
   ```
3. Claims state their evidence grade and the exact command/observation that produced it. "Tests pass" without the command is a rumor.
4. Verification uses the authoritative source (see Truth and Evidence): deployed state is verified at runtime, browser behavior in a browser, human-facing quality by a human gate where required.
5. Green requires the gate: the full deterministic gate (lint, typecheck, tests, validators) runs before "done" claims; CI green is the floor, not the ceiling.
6. Worker-green is not integration-green (see Review and Integration); combined state is tested after merge.
7. Automated accessibility/browser checks are proxies: a real-browser 200% zoom check and human acceptance remain required gates where the contracts demand them (see Accessibility Floor).
8. Flaky tests are defects: fix, quarantine with a reason, or delete — never normalize a red suite as weather.

## RATIONALE

"Running is not working" is the most repeated truth in this ecosystem, and the graduation of evidence exists because real failures hid behind every grade: 200-but-wrong payloads, CI-green-but-broken deploys, worker-reported-complete-but-untested code. Naming the grades makes upgrading them visible.

## HUMAN EXAMPLES

- "Deployed and runtime-verified: `/healthz` 200 with build `abc123` at 14:02; browser-verified by Rylee at 14:10; accessibility scan 0 serious."
- A release note that says "CI tested; runtime verification pending" — honestly incomplete rather than rounded up.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- CI runs the full deterministic gate with exact commands recorded in output.
- Release/handoff templates carry evidence-grade fields.
- Health/version endpoints prove deployed-build identity, enabling runtime verification.
- Verification results persist (test reports, scan results) rather than living in chat scrollback.

## GOOD EXAMPLES

```markdown
VERIFIED:
- unit+integration: `uv run pytest -q` → 214 passed (CI: run #1832)
- runtime: `curl /healthz` → 200, build=abc123 (14:02Z)
- browser: Playwright+axe 0 serious @375/900/1440; 200% zoom human-verified (Rylee)
- grade: RUNTIME VERIFIED + HUMAN ACCEPTED (zoom gate)
```

## ANTI-PATTERNS

- "Looks good to me" after a screenshot glance, stated as verified.
- 200-as-proof-of-correctness.
- A suite so flaky that red is ignored.
- "It worked on my machine" without grade or command.
- Marking HUMAN ACCEPTED without a human.

## ACCEPTANCE CHECKS

- Does every "works" claim name its grade and command?
- Are proxy checks and human gates separated honestly?
- Is the deterministic gate green at the claimed SHA?
- Is any grade silently upgraded? (Must be no.)