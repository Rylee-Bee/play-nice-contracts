---
contract_id: capability-first
title: Capability First
version: 1.0.0
status: canonical
layer: interoperability
applies: [architecture, api, product, infrastructure]
triggers: [new-capability, new-provider, architecture, vendor-integration]
rationale: User intent maps to capabilities; providers implement or enrich them. Vendors never own the meaning of concepts, so any provider can be swapped without redefining the user's world.
---

<!-- contract-receipt: orchard-river-inkstone -->

# Capability First

## Purpose

Organize systems around intent-level capabilities instead of vendor products. A capability is a concept the system owns (source control, health, secrets, media, search, identity, messaging, calendar, storage, AI inference, design...). A provider is an optional implementation of it.

## NORMATIVE RULES

1. Prefer the shape:
   ```text
   USER / CALLER INTENT
           ↓
   CAPABILITY            (core-owned meaning: source_control)
           ↓
   POLICY                 (approvals, classification, floors)
           ↓
   ADAPTER
           ↓
   PROVIDER / TOOL        (gitea, github, forgejo, ... all swappable)
   ```
   over the anti-shape:
   ```text
   VENDOR PRODUCT → VENDOR API SHAPE → OUR ENTIRE ARCHITECTURE
   ```
2. A capability belongs to the system. A provider implements or enriches it. The provider does not define it.
3. The failure mode this forbids: `source_control == Gitea`, such that removing Gitea removes the *concept* of source control from the world. Concepts survive their providers; a missing provider is `not_configured`, never conceptual void.
4. Native baseline where practical: major capabilities have useful local meaning without third parties, or an explicit honest `not_configured` state.
5. Providers declare a mode against a closed vocabulary: `native` / `enrichment` / `replacement`. Optional is the default; `required` is an explicit, rare, justified exception.
6. Provider failure is not core failure: one provider's absence degrades its capability visibly and honestly, without corrupting state or breaking unrelated capabilities.
7. User-facing meaning is provider-neutral: semantic vocabulary (`schema/capability.schema.json`, status vocabulary) governs; provider-specific data is namespaced detail, never canonical.
8. Provider-specific actions do not pollute core actions: the generic action set stays generic; deep operations hand off to the specialist tool (which remains a valid escape hatch via deep links).
9. Provider mode `replacement` swaps a native baseline and remains substitutable like any provider.

## RATIONALE

Proven in Personal World's Native Baseline and Enrichment framework: the entire conformance suite (core-only boots; provider added enriches; provider unavailable degrades honestly; provider removed leaves no corruption; substitution through one contract) exists because vendor-shaped architecture failed first. The rule works far beyond any one stack: identity, secrets, search, storage, AI inference, design — all are concepts that outlive their vendors.

## HUMAN EXAMPLES

- Switching Gitea → GitHub changes an adapter and reconnects; the user's "Source Control" world, history, and vocabulary are unchanged.
- A fresh install with zero providers boots to an honest "nothing connected yet" — not a broken page.
- The media section is "Media", not a Sonarr clone; deep work opens Sonarr.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- A capability registry/manifest answers, per capability: what exists, native baseline?, available providers, active provider, mode, what happens if the provider disappears.
- Adapters implement capability-shaped contracts; claiming an undeclared capability is a validation violation.
- Provider data flows through core policy (classification, approvals) — a provider cannot bypass policy by supplying data.
- Capability-first works for design tooling too: design truth is a capability; Figma is a provider.

## GOOD EXAMPLES

```json
{"capability": "source_control", "native_baseline": false,
 "providers": [{"type": "gitea", "mode": "enrichment"}],
 "absence": "not_configured"}
```

## ANTI-PATTERNS

- Provider-shaped core (`source_control == Gitea`).
- UI navigation organized by vendor names.
- Required optional services (core won't boot without Traefik).
- Canonical schemas expressed as raw vendor JSON.
- Removing a provider deletes the user's data or the concept.
- Rebuilding an entire specialist UI (a full Git client) inside the product.

## ACCEPTANCE CHECKS

- Can every provider be swapped without changing user-facing meaning?
- Does a zero-provider install boot and behave honestly?
- Does one provider's outage leave unrelated capabilities intact?
- Is any vendor's vocabulary canonical in user-facing meaning? (Must be no.)