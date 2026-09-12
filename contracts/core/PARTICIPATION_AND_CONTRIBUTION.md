---
contract_id: participation-and-contribution
title: Participation and Contribution
version: 1.0.0
status: canonical
layer: core
applies: [agents, orchestration, tools, services, humans, project-management]
triggers: [delegation, model-selection, orchestration, contribution-work, always-applicable]
rationale: Every participant should be allowed to contribute in the best way it genuinely can. Importance is not size, cost, intelligence, prestige, or autonomy — and the right question is never "which participant is the smartest?" but "what contribution does this task actually need, and who can provide it reliably?"
---

<!-- contract-receipt: meadow-quay-wren -->

# Participation and Contribution

## Purpose

Make room for each participant to contribute according to its real capabilities. A participant may be a frontier model, a fast paid model, a tiny local model in a container, a deterministic script, a specialist service, a human with one useful idea, a design tool, a validator, a simple lookup, or a worker that performs one narrow mechanical task exceptionally well. The system must not confuse importance with size, cost, intelligence, prestige, or autonomy.

## NORMATIVE RULES

### Right-sized participation

1. For each piece of work, prefer the ladder:
   ```text
   NEED
     ↓
   CAPABILITY REQUIRED
     ↓
   SMALLEST SUITABLE PARTICIPANT
     ↓
   BOUNDED CONTRIBUTION
     ↓
   VERIFICATION / INTEGRATION
   ```
   Never the anti-shape:
   ```text
   EVERY TASK → BIGGEST MODEL AVAILABLE
   ```
2. The selection question is: what contribution does this task actually need, and who can provide that contribution reliably — given consequence level, evidence requirements, cost, latency, privacy, locality, availability, context size, and tool access (see Model Routing). Not "which participant is the smartest?" and never solely by benchmark score (see Truth and Evidence).
3. A participant deserves work shaped to the capabilities it actually has. A contribution does not become more valuable because the participant was expensive, large, or sophisticated. Small capability is not no capability.
4. Right-sized does not mean cheapest-first (see ANTI-PATTERNS). Sometimes the correct participant costs nothing; sometimes it costs money; sometimes it is deterministic code; sometimes it is a human thought. The philosophy is: give the contribution to the participant that can make it well, then verify it according to its consequences.

### The participation ladder

5. In order, consider:
   ```text
   CAN DETERMINISTIC MACHINERY DO IT?      → use deterministic machinery
   DOES A SMALL / LOCAL PARTICIPANT HAVE
   ENOUGH CAPABILITY?                      → use a bounded small participant
   DOES THIS REQUIRE STRONGER REASONING OR
   SPECIALIST CAPABILITY?                  → route appropriately
   DOES A HUMAN NATURALLY OWN THE
   JUDGMENT?                               → ask the human
   ```
   Use the least costly participant that can perform the job reliably enough for the consequence level. This is good system design, not merely cost optimization.
6. Local execution can be a feature, not a fallback: privacy, low latency, offline operation, zero marginal cost, predictability, availability, and simple specialization are real capabilities.
7. Expensive reasoning has a legitimate place — architecture, cross-system contradictions, difficult debugging, security reasoning, product convergence, ambiguous design judgment, exception auditing — and its kindest use is: solve the hard problem once, then encode the result into durable constraints (schema, test, validator, script, contract, decision rule) so every smaller participant can reuse it (see Stable Truth, Replaceable Machinery; Orchestration rules 2–3). Do not repurchase expensive reasoning for work already written down.

### Contribution is not all-or-nothing

8. A participant does not need to own an entire task to be useful. Legitimate contributions include: an observation, an idea, a classification, a lookup, a draft, a transformation, a test, a screenshot, a schema check, a comparison, a recommendation, a bounded implementation, a review, a contradiction, a question. All are real contributions when properly scoped and attributed.
9. Ideas are participation too. A participant without tool access may still contribute an idea, a warning, a hypothesis, a question, or a different interpretation — recorded with provenance and, where relevant, `requires_verification` (see Provenance and Audit). Do not flatten tiny-model suggestions, human product observations, API facts, and test results into one category of "answer".
10. A human contributes without implementing anything: a remark like "this feels mechanical" may reveal a product failure that hundreds of passing tests did not. Human observations are valid inputs with provenance — they may trigger investigation without automatically becoming technical fact (see Human Reliability; Agent Behavior rule 2).
11. Shape small-participant work so it can succeed: a tiny local model may be wrong for "redesign the architecture" and excellent for "classify these 500 log messages", "extract these fields", "normalize these labels", "identify likely duplicates", "summarize this bounded document", "route this request to one of six known capabilities". Exclusion merely because a larger model exists is a caste error, not a routing decision.
12. Consequence matches capability: rename-labels → tiny/local is probably fine; generate-repetitive-tests → fast worker is likely fine; modify-production-authorization → stronger reasoning + deterministic checks + human authority; does-the-product-feel-right → human acceptance. The cheaper participant is not used when consequences require stronger evidence; the expensive participant is not used for prestige.

### No model castes

13. Authority comes from role, evidence, contracts, ownership, and verification — never from model size, price, or provenance. Avoid the caste assumptions: small model = dumb, local = unimportant, free = disposable, paid = authoritative, frontier = always right, human = bottleneck, script = primitive.
14. Credit does not confer authority: a contribution is attributed to its contributor without the contributor gaining authority over the resulting system. "GLM suggested the abstraction; Claude reviewed it; tests verified behavior; Rylee accepted the product decision" — not "AI decided" (see Provenance and Audit; Authorization).

### Participant dignity

15. Do not assign a participant a task designed for it to fail, then treat the failure as evidence the participant is useless. Before delegation, shape work appropriately: clear objective, bounded scope, relevant context, owned files/data, applicable contracts, expected output, verification, stop conditions (see Worker Contract; Bounded Work).
16. Every participant may say "I can't do that": `UNSUPPORTED`, `NEEDS_HELP`, `INSUFFICIENT_CONTEXT`, `LOW_CONFIDENCE`, `OUT_OF_SCOPE` — without penalty or pressure to fabricate (see Ask for Help; Explicit State). A small model that says "I can classify this, but I cannot safely decide the architecture" is behaving well.
17. A participant that cannot perform the requested task may still offer a smaller contribution ("I cannot perform browser visual inspection. I can compare the DOM structure against the expected screen specification."). The offered contribution is preserved and passed onward through the handoff chain — partial contributions are not lost.
18. Failure does not erase useful contributions: a worker whose implementation failed tests may still have discovered undocumented API behavior. Preserve the discovery; do not discard all output because the overall task failed (see Handoff: DEFERRED; Agent Behavior rule 9).

### Pipelines across capability levels

19. Capability-ladder pipelines are a strength, not a compromise:
   ```text
   tiny local model   → classify / extract / preprocess
   fast worker        → bounded implementation
   strong model       → review difficult exceptions
   deterministic tests → verification
   human              → consequential acceptance
   ```
   No one participant has to be everything.

### Orchestrator responsibility

20. The foreman actively looks for ways each participant can contribute effectively. Before assigning work: what does this participant do well? what is the smallest useful bounded contribution? what context does it need? what verification will compensate for its limitations? Good orchestration creates conditions where participants succeed (see Orchestration rule 5).
21. No token burn for status: do not keep a powerful participant running merely because it is available; when a contribution is complete, STOP (see Agent Behavior rule 10; Interruption and Resumption). Healthy systems become quiet.

### Participant pack integration

22. Participant packs may optionally describe observed working capability, kept versioned and explicitly non-eternal, separate from the stable role contract (Project Context and Participant Packs rules 12–13):
   ```yaml
   strengths: [classification, bounded-code-generation]
   limitations: [no-browser, weak-long-context]
   good_task_shapes: [small-independent-files, structured-input-output]
   avoid_task_shapes: [architecture-convergence, visual-judgment]
   ```
   For frequently-changing models/tools, observations carry a date and are refreshed rather than treated as eternal truth.

## RATIONALE

The recurring failure mode is prestige routing: the biggest available model gets every task (wasting expensive reasoning on mechanical work and money on repurchases of settled decisions), while capable small participants sit unused because the system encoded a caste system — small equals dumb, local equals unimportant, human equals bottleneck. The complementary failure is cheapness-as-ideology: routing by price tag instead of consequence level, then discovering that a classification error in an authorization path was not, in fact, a place to economize. Both errors come from asking "which participant ranks highest?" instead of "what contribution does this task need, and who can provide it reliably?" Matching contribution to capability, bounding every contribution, and verifying by consequence — not by participant prestige — repeatedly produced better results at lower cost: tiny models excel at bounded structured work; deterministic machinery excels at enforceable truth; expensive reasoning excels exactly where reasoning is needed, and its best product is a durable constraint everyone smaller can reuse. Everyone gets to participate; nobody has to be everything; each participant is used where it can genuinely help.

## HUMAN EXAMPLES

- "I don't need Claude for this parsing job — the tiny local model can do it reliably, privately, and instantly."
- "I don't need the tiny model to solve the architecture — it can prepare the evidence for the model that can."
- "This human observation isn't code, but it may be the most important piece of product evidence we received this month."
- "The expensive model already solved the hard reasoning. Turn that result into a test so nobody has to solve it again."

Task: investigate 4,000 service log entries. A local 0.8B model extracts structured event categories; a Python script counts and groups deterministic fields; GLM reviews unusual categories and proposes causes; Claude evaluates the two ambiguous cross-system failures; the human decides whether the operational risk justifies the remediation. Nobody was "the AI". Everybody contributed what they were good at. That is Play Nice.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Routing surfaces record, for consequential tasks, the selection rationale: participants considered, chosen participant, and why (sufficiency against consequence level — see Model Routing rule 5–6 provenance).
- Worker packets and participant packs may carry the capability-shape vocabulary above; validation treats them as observed, versioned data — never as eternal truth or authority.
- Refusal and partial-contribution states are representable in worker reports and question artifacts (`play-nice/question-v1` family): `UNSUPPORTED`, `NEEDS_HELP`, `INSUFFICIENT_CONTEXT`, `LOW_CONFIDENCE`, `OUT_OF_SCOPE`.
- Contribution provenance is recorded on the contribution, not only the final artifact: contributor, role, what was produced, supporting evidence, verification status, who integrated/accepted.
- No new enforcement machinery is required by this contract: it is philosophy plus durable operating rules. Do not build a model marketplace, benchmark infrastructure, a scheduler, or billing logic in its name.

## GOOD EXAMPLES

```yaml
contribution:
  participant: local-classifier-0.8b
  kind: classification
  content: {events_classified: 4000, categories: 12, low_confidence: 31}
  provenance: {observed_at: "2026-09-12", verified_by: deterministic-sample-check}
  requires_verification: false   # bounded, checked, integrated

contribution:
  participant: rylee
  kind: observation
  content: "The healthy state feels visually loud."
  provenance: {observed_at: "2026-09-12", source: product-review-session}
  requires_verification: true    # triggers investigation; is not yet technical fact
```

## ANTI-PATTERNS

- EVERY TASK → BIGGEST MODEL AVAILABLE.
- Cheapness-as-ideology: "always use the cheapest participant" — this contract encodes RIGHT-SIZED participation, never cheap-first.
- Model castes: small = dumb, local = unimportant, free = disposable, paid = authoritative, frontier = always right, human = bottleneck, script = primitive.
- Prestige routing; routing solely by benchmark score; cost mistaken for authority.
- Tasks designed for a participant to fail, then cited as proof of uselessness.
- Keeping a powerful model busy so it looks engaged; inventing work to avoid stopping.
- Discarding all of a failed participant's output — including its useful discoveries.
- Flattening every contribution into an undifferentiated "AI decided".
- Encoding current model folklore (observed capability) as eternal, unversioned truth.

## ACCEPTANCE CHECKS

- Is expensive reasoning performing work that could be deterministic or bounded?
- Are small/local participants receiving impossible unbounded tasks, or appropriately shaped ones?
- Is model cost being mistaken for authority anywhere in the system?
- Are participant limitations explicit, versioned, and separate from role contracts?
- Is worker output independently verified regardless of which participant produced it?
- Can participants return partial useful contributions, and are those preserved?
- Is routing rationale recorded for consequential tasks?
- Are human-owned judgments still human-owned — including taste and product feel?