---
contract_id: capabilities-not-vendors
title: Capabilities, Not Vendors
version: 2.0.0
status: canonical
layer: integration
applies: [architecture, integrations, ui, product]
triggers: [third-party service, vendor integration, new provider, saas, self-hosted, lock-in, external api]
rationale: Your system's meaning should not depend on any one outside product, so that product can be swapped or lost without losing the feature.
---

<!-- contract-receipt: sundial-alder-ferry -->

# Capabilities, Not Vendors

## In short

Name what a system does (source control, secrets, media), not which product
does it. Products plug in at the edges and can be swapped. Nothing a user
sees or stores is shaped by one vendor's names.

## Applies when

- You choose, build, or display anything backed by an outside product: a cloud service, a self-hosted tool, a model, a library service.
- Not this contract's job: how you call the service (see calling-other-services) or exporting user data (see portability-and-ownership).

## Rules

1. Own each capability's meaning in your system; a provider implements or enriches it, never defines it. (MUST)
2. Reach providers through adapters at the edges, so swapping one does not rewrite the core. Don't let a vendor's API shape spread through your architecture. (MUST)
3. Organize navigation, vocabulary, and schemas around user tasks, not vendor products. A vendor name may appear as provenance ("via Gitea") and in detail views. (MUST)
4. Keep provider-specific data namespaced and optional; the portable, generic form is the canonical copy. (MUST)
5. A missing provider leaves an honest status (`not_configured`), never a broken page or a vanished concept (see the floor, rule 8). (MUST)
6. One provider's failure degrades only its own capability: no corrupted state, no damage to unrelated features. (MUST)
7. Give major capabilities a useful local default where practical, so the system works before anything is connected. (SHOULD)
8. Treat providers as optional. Making one required is a deliberate, rare, written-down exception. (MUST)
9. Adding a provider must not force a redesign; removing one must not corrupt data. Enrichment reads as an add-on to a surviving concept, not a takeover. (MUST)
10. Deep specialist work hands off to the vendor's own tool via a link; don't rebuild that tool inside yours. (SHOULD)
11. Pick participants — models, tools, services, people — by what the task needs. A bigger, dearer, or more famous name does not define the capability. (MUST)

## Examples

- Switching Gitea → GitHub edits one adapter; the user's source-control views, history, and words are unchanged, and only the "(via …)" text differs.
- A fresh install with zero providers boots and says "nothing connected yet".
- Bad: a "Gitea" item in the main navigation, so losing Gitea means losing the idea of source control.

## Why

Vendor-shaped screens make every swap a redesign, and vendor-shaped data makes every swap a migration. When the meaning stays yours, a provider is just replaceable machinery (see stable-truth-replaceable-machinery): change it, keep the users' view and data.

## You're done when

- Renaming or removing each vendor changes only namespaced detail, never user-facing meaning or stored data.
- A no-provider install boots with honest statuses, not errors.
- No vendor name appears in navigation or canonical schemas.
- One provider's outage degrades one capability and leaves the rest working.

## Machine notes

Keep a capability list that, per capability, says: the local default behavior, which providers exist, which is active, and what its absence renders as (a status word).
