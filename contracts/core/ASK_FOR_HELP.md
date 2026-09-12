---
contract_id: ask-for-help
title: Ask for Help
version: 1.1.0
status: canonical
layer: core
applies: [humans, agents, apis, services, tools, automation, integrations, workflows]
triggers: [uncertainty, ambiguity, blocked-work, integration-work, always-applicable]
rationale: It is nice, polite, kind, and smart to ask for help. When uncertainty can be resolved more safely, cheaply, or accurately by asking another participant, asking is preferable to guessing — and knowing how to ask is what makes a system easy to integrate with.
---

<!-- contract-receipt: ember-gable-yarrow -->

# Ask for Help

## Purpose

Make asking a first-class capability across the ecosystem: humans, agents, orchestrators, workers, APIs, services, tools, and automation should be able to stop, formulate a clear question, and ask the participant who naturally owns the answer — instead of guessing merely because they are capable of generating an answer.

## NORMATIVE RULES

### Founding rule

1. When uncertainty can be resolved more safely, cheaply, or accurately by asking another participant, asking is preferable to guessing.
2. But asking must not become laziness. Do not bother another participant with work you can reliably and cheaply determine yourself. The decision ladder:
   ```text
   KNOW                        → act
   CAN SAFELY DISCOVER         → discover
   ANOTHER PARTICIPANT CAN
   ANSWER CHEAPLY              → ask
   HIGH-COST / HIGH-RISK /
   AMBIGUOUS                   → ask or escalate
   UNKNOWN AND NOBODY CAN
   ANSWER                      → preserve UNKNOWN
   ```

### Ask, don't guess

3. A participant MUST NOT invent: credentials, identifiers, ownership, authorization, user intent, destructive-action scope, unsupported API semantics, missing configuration, unknown state, provider-specific behavior, ambiguous resource selection, or requirements that materially affect the outcome — when the missing fact can reasonably be obtained from the user, another agent, a service API, capability discovery, configuration, or another authoritative system.

### Discover before asking

4. Before asking, use this order:
   ```text
   1. Inspect current known state.
   2. Consult the applicable contracts.
   3. Use safe deterministic discovery.
   4. Ask the most appropriate participant.
   5. Preserve UNKNOWN if still unresolved.
   ```
5. Do not ask a human for information already available through an authorized, inexpensive API call. Do not hammer an API when the human can answer a one-time intent question instantly. Use judgment.

### Ask the right participant

6. Route questions to whoever is best positioned to answer:
   - **Human**: intent, preference, approval, acceptable risk, product judgment, ambiguous ownership, decisions only that person can make.
   - **Service/API**: capability support, API version, current resource state, feature availability, limits, supported mutation semantics, schemas.
   - **Another agent/tool**: specialist analysis, browser inspection, image understanding, repository knowledge, platform-specific expertise, narrow reasoning better handled elsewhere.
   - **Configuration/repository/runtime**: ask the system itself before asking anyone else when the answer is already encoded there.
7. In orchestration, workers do not silently escalate scope or interrupt the human directly when blocked. A worker returns `WORKER STATE: NEEDS_HELP` with a structured question; the foreman decides whether to answer from known state, query another tool or service, ask a specialist agent, or ask the human. The foreman reduces interruption noise (see Orchestration). Honest refusal is always in-bounds: `UNSUPPORTED`, `INSUFFICIENT_CONTEXT`, `LOW_CONFIDENCE`, and `OUT_OF_SCOPE` are legitimate structured states alongside `NEEDS_HELP`, without penalty or pressure to fabricate; a participant may also offer a smaller contribution it CAN make reliably (see Participation and Contribution rules 16–17).

### Human + machine readable questions

8. Every help request has BOTH a useful human representation and a stable machine-readable representation (see Human and Machine Parity). Do not make humans interpret raw RPC errors; do not make bots parse conversational prose when structured information is available. One fact, two representations.

### Question quality

9. A good question answers:
   ```text
   WHAT do you need?
   WHY are you asking?
   WHAT have you already checked?
   WHO is best able to answer?
   IS this blocking?
   WHAT happens if nobody answers?
   WHAT do you recommend, if appropriate?
   ```
10. Questions are concise, specific, answerable, respectful, contextual, free of unnecessary jargon, and structured for automation where possible. Lazy questions are defects:
    - Bad: "What should I do?"
    - Better: name the finding, the checked places, the options, the recommendation, and the exact decision needed.
11. Bring useful context to the interaction; the requester does the investigation legwork, not the respondent.

### Recommend without pretending

12. Where appropriate, include `recommendation`, `recommendation_reason`, and `confidence` — and clearly distinguish FACT, INFERENCE, RECOMMENDATION, and QUESTION. A recommendation is not the answer.

### Cheap to answer

13. Reduce cognitive burden: prefer a one-line decision between labeled options ("A — existing API / B — new webhook / Recommended: A") over a narrative the respondent must reconstruct. Humans get one clear decision at a time; machines get schemas and stable identifiers.

### Questions are resumable state

14. A question is workflow state, not a chat message. Record: `question_id`, `requester`, `target`, `created_at`, `reason`, `question`, `evidence`, `blocking`, `status`, `answer`, `answered_by`, `answered_at`, `resulting_action`. States: `OPEN`, `WAITING`, `ANSWERED`, `DECLINED`, `EXPIRED`, `SUPERSEDED`, `CANCELLED`. A question survives session restart, agent replacement, human interruption, and worker handoff (see Interruption and Resumption).

### Answers become provenance

15. When an answer changes what happens next, preserve the connection: `decision: {question_id, answer, answered_by, applied_to}`. Future maintainers should be able to answer "why did the system choose this?" with "because it asked, and this was the answer" (see Provenance and Audit).

### Human interruption budget

16. Attention is finite. Before interrupting a human, ask: can I answer this myself safely? can another machine answer cheaply? does the human uniquely own this decision? Batch compatible non-urgent questions where useful; do NOT batch unrelated high-consequence decisions into a confusing questionnaire (see Attention and Focus, Quiet When Healthy).

### Service-to-service help

17. Integrations ask other systems rather than hard-coding assumptions: what capabilities do you support; which API version do you speak; can you perform X; what scopes are required; do you support idempotency keys; what resource does this identifier refer to; what limits currently apply. This complements Friendly API Client, Discovery and Negotiation, Versioning and Compatibility, and Capability First.

### Capability gaps → delegate, don't duplicate

18. If system A cannot perform an operation but system B can, do not immediately recreate B inside A:
    ```text
    INTENT
      ↓
    LOCAL CAPABILITY? yes → perform
      ↓ no
    KNOWN FRIENDLY PROVIDER? yes → ask/delegate
      ↓ no
    report unsupported honestly
    ```
    Stable capability, replaceable machinery (see Capability First).

### Delegation does not remove responsibility

19. The requester still verifies the response where appropriate, preserves provenance, integrates it correctly, and reports unresolved uncertainty. "Another bot said so" is not final truth (see Truth and Evidence).

### Asking is a successful stop state

20. A task may legitimately end `STATUS: WAITING_FOR_HELP` when: further action would require guessing; the missing answer is consequential; the correct participant has been asked; current state is safely preserved. This is preferable to manufactured progress (see Bounded Work, Human Reliability).

### Questions are not authorization

21. A help response provides information, not permission. "Which cluster contains service X?" → "prod-west" does NOT imply "you may now delete prod-west." Authorization remains governed independently (see Authorization).

### Safety / privacy

22. Help requests carry no unnecessary secrets, credentials, private data, or sensitive payloads (see Secrets, Data Classification). Ask the minimum necessary question; if another participant needs sensitive data, use the appropriate secure mechanism — never paste it into general agent context.

## RATIONALE

The most expensive integration failures come from the gap between "I understand most of this" and "one thing is missing": participants guess because they can generate an answer, and something breaks. The fix is not more foreknowledge ("system A must know everything about system B") but better boundaries ("system A knows how to communicate with system B"): a system that can formulate a good question is easier to integrate, a system that can answer one is easier to use, and an ecosystem where both happen gets easier to extend every time a new participant joins. Know when you know; discover when discovery is cheap; ask when someone else naturally owns the answer; preserve uncertainty when nobody knows; never guess merely to keep moving.

## HUMAN EXAMPLES

Good interaction:

```text
Agent: I can create the deployment, but the target service exposes two supported
health-check types and this repository does not specify which one is canonical.
I checked: deployment config, service API docs, project contracts. Both are valid.
The provider recommends HTTP for web services; this service exposes /healthz.
Recommendation: HTTP /healthz. Can I use that?
Human: Yes.
Agent: Thank you. I'll use HTTP /healthz and record that decision in the
deployment configuration and provenance.
```

Bad interactions (both are defects): "I wasn't sure, so I picked TCP." (guesses) and "Please tell me how health checks work." (offloads work).

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Standard artifacts: `play-nice/question-v1` (human-facing question with choices/recommendation/blocking), `play-nice/help-request-v1` and `play-nice/help-response-v1` (agent-to-agent), validated by `schema/question.schema.json`.
- Questions persist as workflow state with lifecycle states and answer provenance.
- `WORKER STATE: NEEDS_HELP` is a representable stop state in worker reports.
- Help requests are classified and secret-free by construction.
- Contract gate integration: when this contract applies, the task-impact acknowledgement identifies potential uncertainty points, available helpers, human-owned decisions, service-owned questions, and the safe stop state.

## GOOD EXAMPLES

Machine form:

```json
{"schema": "play-nice/question-v1", "question_id": "q-01842",
 "status": "WAITING",
 "requester": {"type": "agent", "id": "frontend-worker"},
 "target": {"type": "human", "role": "owner"},
 "reason": "Two approved visual references disagree about navigation placement.",
 "question": "Which navigation composition should govern the Settings screen?",
 "choices": [{"id": "rail", "label": "Left rail"}, {"id": "top-nav", "label": "Top navigation"}],
 "recommended": "rail",
 "recommendation_reason": "It matches the newer approved desktop frame.",
 "blocking": true, "safe_to_continue_without_answer": false,
 "affected_scope": ["SettingsScreen"],
 "evidence": ["design/screens/settings-desktop.png", "design/archive/settings-top-nav.png"]}
```

Human rendering:

```text
I found two approved-looking Settings designs that disagree about navigation.
The newer desktop reference uses the left rail, so that's my recommendation.
Which should I use?
[Use left rail — recommended]  [Use top navigation]
I won't change Settings until this is resolved.
```

## ANTI-PATTERNS

- "I wasn't sure, so I picked X." — guessing as progress.
- "What should I do?" — lazy question with no context.
- Ten ping interruptions for decisions a config file or API answers.
- Batching "approve prod deletion + pick a font" into one questionnaire.
- Treating an answer as permission.
- Secrets pasted into a help request "so they can test".
- A question that dies with the session (no persisted state, no provenance).
- Workers silently escalating scope, or every worker interrupting the human directly.
- Delegating and reporting "another bot said so" as verified truth.

## ACCEPTANCE CHECKS

- Did the participant check discoverable places before asking?
- Does each question answer the quality contract (what/why/checked-where/blocking/if-unanswered/recommendation)?
- Is it routed to the participant who naturally owns the answer?
- Is it cheap to answer (one decision at a time, structured for machines)?
- Is it persisted state with provenance (not scrollback)?
- Was WAITING_FOR_HELP accepted as a legitimate, safe stop state?
- Is the answer recorded as decision provenance, and never conflated with authorization?