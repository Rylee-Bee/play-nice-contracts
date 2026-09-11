---
contract_id: discovery-and-negotiation
title: Discovery and Negotiation
version: 1.0.0
status: canonical
layer: interoperability
applies: [api, tools, integration]
triggers: [new-integration, tool-interop, capability-check]
rationale: Tools should discover what other tools can actually do, and degrade gracefully when an optional capability is absent. One missing optional feature must never sink the whole integration.
---

<!-- contract-receipt: nectar-heather-prairie -->

# Discovery and Negotiation

## Purpose

Make capabilities discoverable and negotiable: a client should learn what a system supports, adapt to it, and degrade gracefully when an optional feature is absent.

## NORMATIVE RULES

1. Prefer capability negotiation over hard-coded assumptions. A client asks "what can you do?" before "do X".
2. Systems expose, where practical: supported API/schema version, capability set, optional features, provider mode, and compatibility information (see Capability First manifest).
3. Absence of an optional capability is a normal negotiated outcome: the client skips it, uses a fallback, or reports it as `not_configured` — it never fails the entire system because one optional feature does not exist.
4. Unknown or unsupported versions fail clearly at negotiation time ("server speaks v2, client speaks v3"), not mysteriously at first use (see Versioning and Compatibility).
5. Discovery results are cacheable but refreshable; stale capability assumptions are re-negotiated when versions change.
6. A minimal system with a small capability set is as legitimate as a maximal one; clients built against the vocabulary handle both.
7. Negotation is honest: do not advertise capabilities you cannot honor; optional features report their real state (`disabled`, `not_configured`, `unavailable`) rather than silently vanishing.

## RATIONALE

Hard-coded assumptions about other tools are the source of the "works on my stack" class of integration failure. Negotiation lets small systems stay small, big systems grow, and clients survive both — and it is the machine-to-machine form of the same respect that drives the whole library: ask before assuming.

## HUMAN EXAMPLES

- A CLI that connects to an older server: "This server doesn't support scheduled jobs yet. Skipping." — and everything else still works.
- A plugin system where a plugin's absence degrades one feature rather than breaking boot.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Manifest/capability endpoints (`GET /api/manifest`-class) are versioned and additive-only where possible.
- Clients gate features on negotiated capability presence; feature checks are centralized, not scattered conditionals.
- Negotiation failures use stable error identifiers.

## GOOD EXAMPLES

```json
{"capabilities": ["source_control", "health"],
 "version": "2.1.0", "optional": {"webhooks": "not_configured"}}
```

## ANTI-PATTERNS

- Hard-coding a feature list per server version.
- Whole-integration failure when one optional endpoint 404s.
- Advertising features that are actually broken.
- Discovering compatibility by trying and crashing.

## ACCEPTANCE CHECKS

- Does the client ask before assuming?
- Does one absent optional feature sink anything unrelated? (Must not.)
- Are version mismatches reported at negotiation with clear language?