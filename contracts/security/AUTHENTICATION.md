---
contract_id: authentication
title: Authentication
version: 1.0.0
status: canonical
layer: security
applies: [api, ui, agents, infrastructure]
triggers: [auth-work, api-design, sessions]
rationale: Know who is calling. Authentication is provider-neutral, suitable for browsers and future clients, and never has exactly one way in — because lockouts and vendor drift are both real failure modes.
---

<!-- contract-receipt: bramble-zenith-gable -->

# Authentication

## Purpose

Establish who is acting, through a mechanism that survives provider replacement and serves humans, browsers, CLIs, agents, and future clients equally.

## NORMATIVE RULES

1. Authentication is provider-neutral: the system's identity layer is a seam (an auth provider contract), with concrete providers as swappable adapters. Authelia, OIDC, local passwords, tokens, or future IdPs are configuration, not architecture.
2. Multiple entry paths remain first-class: browsers via SSO/sessions, CLIs and agents via tokens; no client class is a hack.
3. Sessions are bounded and inspectable: rotation on login and level change, revocable, server-side state that can be invalidated en masse; deleting session storage loses nothing canonical.
4. The owner can never be locked out: a break-glass/local path exists for the system's own administrator, tested, documented, and usable when the primary IdP is unavailable.
5. Forged ambient trust is ignored: client-supplied identity headers from an untrusted source are never accepted as authentication.
6. Authentication state is visible to the user: who am I, what level, when my session expires — surfaced, not guessed.
7. Failure states are honest and distinct: wrong credentials, unconfigured auth, and unreachable backend are three different messages (see Failure and Degradation), and none of them leaks which part failed in a way that aids enumeration.
8. Secret handling at authentication follows the Secrets contract: references, never inline values; never in logs; never in URLs.

## RATIONALE

Hard-coded single-vendor auth produces two documented failure classes in this ecosystem: total lockout when the IdP breaks, and rewrite surgery when the vendor changes. The seam pattern (auth provider contract + adapters + break-glass) makes both survivable — and treats agents/CLIs as legitimate first-class callers rather than sneaking around the browser flow.

## HUMAN EXAMPLES

- Losing internet doesn't lock the owner out of the locally-hosted admin surface.
- An agent's token grants exactly its scoped capabilities and appears in the audit trail as itself.
- "Session expires in 10 minutes — extend?" instead of a silent logout mid-task.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Auth provider contract: `authenticate`, `verify`, `step_up`, `whoami`; providers implement.
- Token/session stores: revocable, expiring, journaled creation and revocation.
- Step-up levels integrate with Authorization's sensitive-action gates.
- Every protected surface checks auth centrally; no route "forgets".

## GOOD EXAMPLES

```json
{"principal": "rylee", "auth_level": 2,
 "method": "oidc:authelia", "expires_at": "2026-09-11T15:00:00Z"}
```

## ANTI-PATTERNS

- Trusting `Remote-User` headers from arbitrary clients.
- One SSO vendor wired so deeply that its outage is your outage.
- No break-glass path; the owner is an outsider to their own system.
- Sessions that cannot be revoked without restarting the world.

## ACCEPTANCE CHECKS

- Can the primary IdP vanish without total lockout?
- Can CLIs/agents authenticate as first-class citizens?
- Are forged-credential paths tested and rejected?
- Is the session store revocable and non-canonical (safe to delete)?