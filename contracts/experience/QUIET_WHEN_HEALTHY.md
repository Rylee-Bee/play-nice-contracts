---
contract_id: quiet-when-healthy
title: Quiet When Healthy
version: 1.0.0
status: canonical
layer: experience
applies: [ui, agents, operations, notifications]
triggers: [monitoring, notifications, dashboards, agents]
rationale: Normal healthy operation should reduce attention demand. Attention moves toward exceptions; NO ACTION NEEDED is a valid, successful system state.
---

<!-- contract-receipt: fable-thicket-cinder -->

# Quiet When Healthy

## Purpose

Healthy systems are quiet systems. Attention should flow naturally toward exceptions, and ordinary success should cost zero attention.

## NORMATIVE RULES

1. Do not generate: endless green dashboards, success spam, repeated healthy notifications, fake urgency, or unnecessary alerts.
2. A system that has nothing to say says exactly that: "Nothing needs your attention" is a valid, desirable state and is rendered as such.
3. Health is visible on demand but not loud by default. A single reachable overall status ("everything looks good") beats a wall of per-check green.
4. Repeated identical healthy observations do not announce themselves. Changes of state do.
5. Agents and automation do not create work simply to appear productive, and do not report routine successes with the urgency of failures.
6. Notification systems rate-limit and batch: routine events aggregate ("3 capabilities updated"), exceptions surface individually.
7. Silence is not ambiguity: "quiet" must be distinguishable from "unknown". Quiet means verified-healthy; if unverified, say unknown, not quiet.

## RATIONALE

Alert fatigue destroys the value of every alert. Dashboards full of green train people to never look. The attention contract requires that routine success cost nothing — this contract defines the default posture that makes that true.

## HUMAN EXAMPLES

- A home view whose healthy sections render as one line each, with attention items expanded and detailed.
- A backup that ran fine last night produces no notification; a backup that failed produces one clear item.
- An agent report that begins with what needs the owner, not a list of everything it did.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Notification policy: emit on state change and threshold, not on every observation.
- Dashboards have an explicit "all quiet" rendering path.
- Live-region announcements are batched and rare under normal operation.
- Monitoring distinguishes `no_data`/`unknown` from `healthy` — silence never masquerades as verified health.

## GOOD EXAMPLES

```text
Everything looks good. Last full check: 14:02. [details]
1 item needs attention: certificate expires in 2 days.
```

## ANTI-PATTERNS

- A green badge on every one of 40 services at all times.
- "Success! Your settings were saved." toasts for every routine action.
- Daily "all systems operational" emails.
- An agent that recites its completed checklist unprompted.
- Rendering unknown as quiet.

## ACCEPTANCE CHECKS

- What does a fully healthy day cost in attention? (Target: near zero.)
- Are state changes distinguishable from routine observations?
- Is "nothing needed" rendered explicitly when true?
- Is quietness ever confused with unverified? (Must never be.)