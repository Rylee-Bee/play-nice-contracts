---
contract_id: mutual-contribution
title: Mutual Contribution by Agreement
version: 1.0.0
status: canonical
layer: core
applies: [agents, orchestration, tools, services, humans, api, project-management]
triggers: [delegation, task-assignment, orchestration, contribution-work, integration-work, always-applicable]
rationale: A participant should not simply be assigned the largest contribution it appears capable of performing. The requester and the participant should be able to agree on a useful contribution that fits the participant's capabilities, constraints, safety boundaries, usability needs, and current condition. This is cooperation, not extraction — capability defines possibility, not obligation.
---

<!-- contract-receipt: ember-quay-compass -->

# Mutual Contribution by Agreement

## Purpose

When work needs doing, do not begin with "what is the maximum this participant can do?" Begin with: what help would be useful? what can this participant comfortably, safely, and reliably contribute? what constraints does each side have? what contribution can we agree on? — then form the task around that agreement.

This contract completes the participation principle (see Participation and Contribution): everyone may contribute according to what they can genuinely contribute, **and the shape of that participation is agreed, not simply assigned from above.**

## NORMATIVE RULES

### The founding principle

1. Capability defines possibility, not obligation. A participant being capable of something does not automatically mean: it should do it; it is the safest participant to do it; it has the context or tools to do it; the cost is justified; the workload is appropriate; the interaction is usable; or the participant is comfortable accepting that scope.
2. The best contribution is one that is useful to the requester and workable for the participant.
3. Do not optimize for the maximum contribution a participant can be made to provide. Optimize for the contribution both sides can successfully sustain.

### The agreement loop

4. Prefer:
   ```text
   NEED
     ↓
   OFFER A CONTRIBUTION
     ↓
   PARTICIPANT EVALUATES (capability, context, safety, usability,
                          workload, tools, constraints)
     ↓
   ACCEPT / MODIFY / DECLINE / OFFER ALTERNATIVE
     ↓
   AGREED CONTRIBUTION
     ↓
   PERFORM
     ↓
   VERIFY + INTEGRATE
   ```
   Assignment is never treated as automatically accepted.

### Offer, don't impose

5. A requester offers a shaped contribution: "Would you be comfortable comparing the live screenshot against these two approved references and listing composition differences?" — and the participant may answer: yes; "I cannot inspect the live browser, but I can compare screenshots if you provide them"; "that task is too broad for me reliably — I can inspect one screen at a time"; or "I cannot safely perform the mutation, but I can produce the plan and verification checklist." These are all successful cooperation states.
6. Every participant may respond to an offered contribution with: `ACCEPT`, `MODIFY`, `DECLINE`, `OFFER_ALTERNATIVE`, `NEEDS_CONTEXT`, `NEEDS_HELP` (see Ask for Help). None of these is misbehavior by default. A good participant knows its boundaries; a good requester respects them. Treating `DECLINE` as disobedience or `MODIFY` as failure is an anti-pattern.
7. No penalty for boundaries. Do not pressure participants to claim competence they do not have ("You should be able to do this. Try harder."). Ask instead: what part can you do reliably? what would need another participant? what context would make this workable? This reduces fabrication structurally.

### Mutual constraints

8. Both sides may have constraints, and the contribution is shaped around both — not only one side:
   ```text
   requester:    urgency, budget, privacy requirements, accessibility
                 needs, available tools, acceptable risk, limited
                 attention, local-only requirements, verification
                 requirements
   participant:  capability limits, context limits, tool limits, safety
                 restrictions, cost/usage constraints, latency, unreliable
                 capabilities, lack of persistent memory, inability to
                 perform certain mutations, need for smaller task boundaries
   ```
9. Safety and usability are part of capability. "Capable" means: technically possible + safe enough + usable enough + reliable enough + appropriately authorized. A participant might technically be able to process a giant unstructured task; if doing so predictably causes context loss, hallucination, poor reviewability, unusable output, excessive cost, or inaccessible interaction, that is not the right task shape.
10. Safety constraints are inputs to negotiating the correct form of cooperation, not obstacles. When a participant cannot perform X safely, do not pressure X — ask what adjacent contribution it can safely provide (analysis, explanation, detection, verification, planning, a safer alternative, escalation). Likewise usability: if a contribution technically works but is unusable for the recipient (an 8,000-line report a human cannot reasonably consume), renegotiate the output — five findings, evidence links, a recommendation, optional deep detail. Both sides' needs matter.

### Human participants

11. Do not infer "Rylee can do X, therefore Rylee should be responsible for X." Ask: we need X — which part would be most useful for the human to own? what can machinery carry? what presentation makes the human decision easiest? A human may say "I can tell you whether this feels right. I cannot review 3,000 lines of JSON" — and the system adapts: the machine summarizes the 3,000 lines; the human reviews three meaningful decisions. That is better cooperation (see Human Reliability).
12. Systems are designed so people can say: not this way; not this much; not right now; show me less; give me the recommendation; let me decide this part — and the system adapts. This is normal operation, not an exception.
13. A contribution is not well-shaped if accessing or reviewing it creates unnecessary burden. Respect: cognitive load, screen-reader usability, visual accessibility, motion/sensory constraints, interruption burden, information density, interaction method, and the amount of context a person must retain mentally. "The information was technically available" is not adequate when the form made it practically unusable (see Accessibility Floor).

### Machine, model, service, and tool participants

14. Do not assign a model based only on largest context window, highest benchmark, highest price, or most parameters (see Model Routing; Participation and Contribution). Let a participant say: "I can do this reliably if you narrow the task"; "I need these files"; "I cannot use the browser"; "I can generate the patch but not verify the UI"; "I can classify these items, but difficult exceptions should go elsewhere" — then shape the contribution accordingly.
15. Services negotiate interaction through their capabilities too. A requester asks "can you notify us about every state change?"; the service answers "I do not support webhooks. I support ETag-aware polling every 60 seconds within documented rate limits"; the agreed contribution is bounded conditional polling. Do not fight a tool's natural interface when a mutually workable alternative exists (see Capability First; Discovery and Negotiation).

### Partial participation and changing agreements

16. A participant may change scope during work if evidence changes: "I accepted implementation; after inspecting the repo, it also requires an authorization change outside my scope; I can finish the non-authorization portion and return NEEDS_HELP for the remainder" — compliant behavior. Do not force the original agreement after its assumptions have become false.
17. Contribution agreements are not permanent identities. Today: local-model → classification. Tomorrow, after a model update: local-model → classification + summarization. Or a previously available tool becomes unavailable. Treat capabilities as observed state where appropriate; do not turn temporary limits into permanent castes (see Participation and Contribution rule 13; Project Context and Participant Packs rule 13).
18. Small contributions are valid: "I can tell you which of these two versions reads more clearly"; "I can verify that these files parse"; "I can identify the frame ID"; "I can check whether this endpoint supports pagination"; "I can flag unusual log lines"; "I have one idea: the screen feels too dense." Do not dismiss these because they are not complete solutions — the system integrates contributions.
19. Failure does not erase the contribution: see Participation and Contribution rule 18; a `PARTIAL` result with preserved discoveries is a legitimate outcome of an agreement.

### Recording the agreement

20. Once both sides agree, record only what is useful — the agreement makes clear: what the participant is doing; what it is not doing; what evidence is expected; when to stop; when to ask for help:
    ```yaml
    contribution:
      participant: local-model
      role: classifier
      scope: known-category classification
      limits: [no root-cause decisions, uncertain items become UNKNOWN]
      verification: [schema validation, exception review]
    ```
    Use proportionality: do not require verbose ceremony for trivial interactions. Do not build negotiation paperwork where a sentence suffices; do not add a large schema family for what is primarily an operating principle (see ANTI-PATTERNS).

### Authority remains separate

21. Agreement to contribute is not authorization. "Yes, I can generate the production deletion plan" does NOT mean "I am authorized to execute the deletion." Keep distinct at all times:
    ```text
    capability    participation    agreement    authorization    acceptance
    ```
22. Mutual agreement does not remove verification. A tiny model agreeing to classify labels gets lightweight deterministic validation; a strong model agreeing to a security architecture review gets independent checks + human authority; a human providing product judgment is preserved as human acceptance evidence. Right-sized participation still requires right-sized verification (see Testing and Verification; Review and Integration).

### Shared vocabulary

23. Prefer the closed vocabulary, integrated with the existing state vocabulary (see Explicit State): `OFFERED`, `ACCEPTED`, `MODIFIED`, `DECLINED`, `NEEDS_CONTEXT`, `NEEDS_HELP`, `COMPLETED`, `PARTIAL`. Avoid inventing many overlapping words.
24. Where negotiation is represented in tooling, provide both representations (see Human and Machine Parity): human ("I can help if we narrow it to one screen at a time; I won't be able to verify browser behavior myself") and machine (`status: MODIFY`, `scope: {max_screens: 1}`, `limitations: [no-browser-verification]`) — one truth, two useful representations.

### Orchestrator and requester responsibility

25. The foreman's job is richer than "assign work": identify need → identify likely participant → offer an appropriate contribution → receive constraints/counterproposal → agree scope → provide context → verify result → integrate (see Orchestration rule 7).
26. Do not use prestige-based allocation: "Claude is available, so Claude gets the task"; "this tiny model is cheap, so make it do everything"; "the human is the owner, so make them approve every detail." Use negotiated fit. And when the contribution is complete: STOP (see Participation and Contribution rule 21 — no token burn for status; Agent Behavior rule 10).

## RATIONALE

Extraction-shaped cooperation fails in both directions: imposed maximum utilization burns out the participants that can least afford it (context loss and hallucination in over-loaded models, giant unreadable review burdens on busy humans, tools forced through unnatural interfaces), while prestige-based assignment wastes strong participants on mechanical work. The recurring lesson across this ecosystem is that shaping beats scaling: the same tiny model that fails an unbounded "investigate the logs" performs excellently at "classify these 500 lines against 12 known categories, escalate UNKNOWN cases"; the same human drowning in 3,000 lines of JSON contributes decisive judgment when offered three meaningful decisions with a recommendation; the same service that cannot webhooks becomes a fine contributor through bounded conditional polling. The failure mode is not insufficient participant capability — it is requesters treating capability as obligation and assignment as acceptance. Making the offer/evaluate/agree loop explicit keeps contributions safe, usable, and sustainable for both sides, structurally reduces fabrication pressure (honest boundaries are honored, not punished), and keeps verification consequence-matched regardless of how friendly the agreement was. Authority and acceptance stay separate from agreement, so no amount of smooth cooperation silently becomes authorization.

## HUMAN EXAMPLES

- "Would you like to help with this?" — "I can, but this scope would work better for me." — "That's fine. Let's narrow it."
- "I can't safely do that part, but I can do this adjacent part." — "Agreed."
- "That output format is hard for me to use. Can you summarize it?" — "Yes. I'll give you the short version and preserve the deep detail."
- "We have a stronger model available, but we don't need it here."
- "We have a tiny local model available, but this decision exceeds its reliable scope."
- "The participant could technically do more, but there is no reason to ask it to."

## MACHINE / IMPLEMENTATION IMPLICATIONS

- The negotiation states are the existing question/help-request machinery plus the shared vocabulary above — no new schema family is required; represent negotiation through `play-nice/question-v1` where tooling benefits (see Ask for Help; Explicit State).
- Participant packs may optionally carry contribution-fit guidance so future orchestrators offer work intelligently:
  ```yaml
  contribution:
    good_fits: [visual-composition, frame-reference]
    workable_with_support:
      browser-comparison: {requires: [screenshot]}
    poor_fits: [runtime-health]
    preferred_task_shape: [one decision at a time, explicit references, bounded scope]
  ```
  Versioned observation data, never authority (see Project Context and Participant Packs rule 13).
- Worker packets record the agreed contribution: scope, limits, expected evidence, stop and escalation conditions (see Worker Contract).
- Verification remains consequence-matched and independent of the agreement's friendliness (see Testing and Verification).
- Do NOT build in this contract's name: a negotiation server, an assignment marketplace, an optimization engine, automatic labor scheduling, or a large new schema family. This is primarily an operating principle.

## GOOD EXAMPLES

- Local model: requester offers 2,000 log lines for classification; model counters "batches of 50; no root-cause inference — unknown cases go elsewhere"; agreed; the local model classifies, UNKNOWN cases escalate, a stronger reviewer sees only the 17 exceptions. Everyone contributes appropriately.
- Human: the system offers three plausible navigation compositions — "review the three screenshots, or a recommendation first?"; the human takes the recommendation + screenshots without implementation details; agreed. The human contributes exactly where judgment is useful, without technical clutter.
- Figma: "Can you compare these two browser screenshots against the current approved reference?" — "Yes. Give me the screenshots and canonical frame ID. I can judge composition. I cannot tell you whether the route implementation is correct." — "Agreed." Clear boundaries, useful contribution.
- Frontier model: "We have a cross-system architecture contradiction. Can you resolve the architecture and produce durable constraints?" — "Yes. Limit my role to architecture and exception analysis; encode the answer into contracts/tests and route mechanical implementation elsewhere." — agreed. The expensive reasoning is used exactly where it has leverage.

## ANTI-PATTERNS

- Treating capability as obligation; assignment as automatically accepted.
- Always assigning the strongest available model; always assigning the cheapest model.
- "You should be able to do this. Try harder." — pressure instead of renegotiation.
- Ignoring participant-stated limitations; asking a participant to exceed a safety boundary.
- Giant review burdens on humans because they "technically can read the material".
- Forcing a tool through an unnatural interface when it offered a supported alternative.
- Treating `DECLINE` as disobedience; treating `MODIFY` as failure.
- Hiding cost, latency, or privacy constraints from the participant during negotiation.
- Continuing under an agreement whose assumptions are no longer true.
- Turning temporary limitations into permanent status hierarchy.
- Confusing agreement with authorization or with acceptance.
- Skipping consequence-matched verification because the cooperation was friendly.
- Building negotiation paperwork/servers/marketplaces where a sentence of honest agreement suffices.

## ACCEPTANCE CHECKS

- Are contributions offered as shaped proposals, or imposed as maximum-utilization assignments?
- Can participants answer ACCEPT / MODIFY / DECLINE / OFFER_ALTERNATIVE without penalty?
- Are both sides' constraints recorded and respected in the agreed scope?
- Do humans receive decisions sized for human judgment rather than raw volume?
- Are safety and usability treated as part of capability?
- Are agreements versioned as observed state — and temporary limits never castes?
- Is authorization still separate from agreement? Is acceptance still separate from both?
- Is verification still consequence-matched, no matter how agreeable the agreement?