---
contract_id: least-privilege
title: Least Privilege
version: 1.0.0
status: canonical
layer: security
applies: [infrastructure, agents, api, automation]
triggers: [credentials, service-setup, agent-setup, automation, new-integration]
rationale: Every actor — service, token, agent, automation — holds exactly the permissions its bounded job requires, for exactly as long as required. Broad grants convert every mistake into an incident and every incident into a breach.
---

<!-- contract-receipt: latch-heather-river -->

# Least Privilege

## Purpose

Scope every credential, permission, and grant to the smallest set that lets the bounded job succeed — then make it revocable and short-lived.

## NORMATIVE RULES

1. Each actor gets exactly the permissions its bounded job needs: no shared admin credentials, no "just in case" scopes, no wildcard grants where a named scope works.
2. Prefer short-lived, scoped credentials (tokens per service per purpose) over long-lived broad ones; prefer per-repository or per-integration credentials over global ones.
3. Required-ness is explicit: optional is the default; anything `required` is a rare, justified, recorded exception (`required_reason`).
4. Grants are inspectable and revocable: a list of who-holds-what exists; revocation is a documented, tested operation; rotation is routine.
5. Authority never expands silently: a tool, agent, or automation that needs a new permission gets an explicit grant change — never a widening default.
6. Environments are isolated: dev/production credentials, tokens, and admin grants never cross boundaries; a dev environment cannot reach production secrets.
7. Agents receive authority in their task instructions and nowhere else (see Agent Behavior); granting an agent "do whatever is needed" is a violation.
8. Ambient trust is not a grant: network position, host identity, or being "internal" never substitutes for authentication and authorization.

## RATIONALE

The PAT-in-URL incident (homelab) and credential-exposure incident (Personal World P0) both trace to over-broad, long-lived credentials held for convenience. Bounded, revocable, per-purpose grants shrink blast radius mechanically: a leaked dev token is an annoyance; a leaked global admin token is a week of rotation.

## HUMAN EXAMPLES

- A sync service holds one read-only token for one upstream repo — not the owner's account.
- An agent's task says "you may write to `docs/` and nothing else" — and the harness enforces that boundary.
- A quarterly review lists every standing credential with its purpose and last-use date.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Service/agent registration records scopes per credential; validators reject unscooped admin credentials for ordinary services.
- Token lifetimes and expiry are configuration; renewal is a flow, not a redesign.
- CI and automation use narrowly-scoped deploy credentials per target, never shared long-lived secrets where OIDC/short-lived alternatives exist.

## GOOD EXAMPLES

```json
{"service": "backup-sync", "credential": "read-only:repo-a",
 "granted": "2026-08-01", "expires": "2026-11-01", "revocable": true}
```

## ANTI-PATTERNS

- One admin token shared by five services.
- "Internal network, no auth needed."
- Wildcard CORS/ACLs because enumeration was tedious.
- An agent with repository-wide write for a docs fix.
- Credentials that outlive the project they were created for.

## ACCEPTANCE CHECKS

- Can every standing credential state its exact job and nothing more?
- Is revocation tested and immediate?
- Does any actor hold permissions "for later"? (Revoke.)
- Do dev and production share any secret material? (Must be no.)