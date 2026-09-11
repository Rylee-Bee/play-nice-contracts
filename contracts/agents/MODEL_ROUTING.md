---
contract_id: model-routing
title: Model Routing
version: 1.0.0
status: canonical
layer: agents
applies: [agents, infrastructure]
triggers: [agent-work, model-selection, provider-setup]
rationale: Use expensive intelligence for expensive judgment; use cheap fast models for constrained execution. The orchestrator can always reject worker output, and there is never a silent paid/provider fallback.
---

<!-- contract-receipt: sable-fathom-orbit -->

# Model Routing

## Purpose

Route each piece of work to the right grade of intelligence — expensive judgment where judgment is expensive, fast constrained execution where execution is bounded — with the routing explicit and overridable.

## NORMATIVE RULES

1. Use stronger models for: architecture, difficult contradictions, browser UAT/taste, complex debugging, security boundaries, final convergence. Use faster/cheaper models for: bounded implementation, mechanical refactors, repetitive fixes, test additions, documentation propagation.
2. Routing is configuration, not hard-coded policy: provider and model choice per task class is data the owner can inspect and change (see Provider Neutrality).
3. The orchestrator can always reject worker output; rejection is a normal outcome, never an emergency (see Orchestration).
4. No silent paid/provider fallback: a job configured for the local model does not quietly upgrade itself to a paid cloud API. Any fallback that exists is explicit, configured, and visible in the run record.
5. Every generation records provenance: which provider, which model, when (see Provenance and Audit) — surfaced at Level 2, not hidden.
6. Cost and latency are part of the record: a run's model/spend/timings are inspectable so routing can be tuned on evidence.
7. Model choice never becomes load-bearing truth: outputs pass deterministic gates before touching state (see Deterministic First, Stable Truth).

## RATIONALE

Routing lessons from real batches: the strong model was wasted on mechanical tasks and the fast model produced architecture-shaped nonsense until routing matched task class; a silent cloud fallback produced an unexpected bill; and rejecting-and-reassigning was always more reliable than hoping the first model's output was right.

## HUMAN EXAMPLES

- A doc-propagation batch runs on the fast local model; a security-boundary review routes to the strong model; the routing table shows both.
- A worker's rejected diff triggers reassignment, and the run record shows "rejected by foreman, reassigned" — nothing silently retried into a cloud.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- A routing configuration surface (task-class → provider/model/budget) as data.
- Run records capture provider/model/latency/cost per generation.
- Fallback policies are explicit flags with alerts when they trigger; absent flag = no fallback.
- Worker output always passes the deterministic gate before integration.

## GOOD EXAMPLES

```yaml
routing:
  bounded-implementation: {provider: local, model: fast-14b, budget: 20k}
  architecture-review:    {provider: local, model: strong-235b}
  browser-uat:            {provider: local, model: strong-235b}
  fallback: none
```

## ANTI-PATTERNS

- One model for everything because it's simplest.
- Silent retry on a paid API after local failure.
- Routing decisions living only in an agent's memory.
- Accepting worker output without the gate because "the model is good".
- Model identity becoming an undocumented requirement of any feature.

## ACCEPTANCE CHECKS

- Is the routing table explicit and owner-editable?
- Is every fallback visible (and none silent)?
- Can the orchestrator's rejections be found in the record?
- Does every generation carry model provenance?