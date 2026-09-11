---
contract_id: authorization
title: Authorization
version: 1.0.0
status: canonical
layer: security
applies: [api, ui, agents, operations]
triggers: [always, permissions, api-design, agent-actions]
rationale: Authorization is explicit, scoped, and fails closed. Ambiguity is refusal. Administrative capability never implies routine access to private content.
---

<!-- contract-receipt: compass-vellum-dovetail -->

# Authorization

## Purpose

Every action's authority comes from an explicit, inspectable grant. Ambiguity never resolves in favor of access.

## NORMATIVE RULES

1. Ambiguous authorization fails closed. When in doubt: deny, explain how to get unambiguous authorization, and record the refusal.
2. Grants are explicit and scoped: named actor, named capability, named scope, revocable. Never blanket "do whatever is needed" authority for consequential action.
3. Administrative capability must not automatically imply routine access to private content. Being able to operate a system is not permission to read everything it holds.
4. Step-up verification gates sensitive actions: policy changes, secret access, destructive operations, and security-sensitive mutations require fresh or elevated authorization, regardless of remembered preferences.
5. Remembered rules ("remember this setting") persist boundaries, never erase them; a remembered preference never silently removes the approval gate for severe actions.
6. Provider data cannot bypass policy: observations and payloads pass through core policy enforcement; a provider's self-declared classification or authority is ignored (the core assigns it).
7. Authorization decisions are journaled for sensitive actions: what was requested, by whom, granted or denied, under which policy.
8. Agents act with exactly the authority granted in their task instructions — no more (see also External Mutations, Agent Behavior).

## RATIONALE

Fail-open authorization turns every misconfiguration into an incident, and blanket authority turns every agent mistake into a breach. The provider-classification guard exists because real systems tried to smuggle authority in through payloads. Failing closed is occasionally annoying and always survivable; the reverse is neither.

## HUMAN EXAMPLES

- An operation fails with "not authorized for vault reads; grant the vault-read scope or perform this in the vault UI" — instead of a mysterious 500.
- Opening the admin panel does not expose another user's journals.
- A sensitive settings change asks for fresh confirmation even on a remembered machine.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Authorization checks happen at the operation boundary, centrally, not per-route by convention.
- Policy is code: cemented policies reject every non-user mutation path; tested.
- Step-up levels exist on sessions/tokens (`auth_level`, step-up TTL) and are checked per sensitive operation.
- Denial responses name the missing scope (without leaking what exists).

## GOOD EXAMPLES

```json
{"error": "forbidden", "needed_scope": "vault:read",
 "how": "Grant the scope, or use the vault surface."}
```

## ANTI-PATTERNS

- "Admin sees everything" as the security model.
- Retry-after-deny loops treating 403 as transient.
- Remembered consent that skips confirmation for destructive actions.
- Trusting a payload's `role: "admin"` self-declaration.

## ACCEPTANCE CHECKS

- Is any ambiguous path resolved toward access? (Must be no.)
- Are all grants scoped and revocable, with an audit trail?
- Do sensitive actions require step-up regardless of remembered preferences?