---
contract_id: provider-neutrality
title: Provider Neutrality
version: 1.0.0
status: canonical
layer: interoperability
applies: [architecture, api, ui, product]
triggers: [new-provider, ui-work, architecture]
rationale: User-facing meaning stays provider-neutral; provider specifics are namespaced enrichment, never canonical truth. No configuration should look like the "real" one — all legitimate setups are first-class.
---

<!-- contract-receipt: bramble-ledger-inkstone -->

# Provider Neutrality

## Purpose

Keep user-facing meaning, navigation, vocabulary, and schemas provider-neutral, while provider specifics live as clearly-namespaced, optional enrichment.

## NORMATIVE RULES

1. Navigation and primary UI are organized around user tasks and capabilities, never around vendor products. Providers appear as provenance ("via Gitea") and in detail surfaces — not as the information architecture.
2. All legitimate configurations are equally first-class:
   ```text
   system only / + local model / + cloud AI / + paid service / + full self-hosted stack
   ```
   None may look like the "real" one while others look incomplete. An external provider enriches a capability; it does not legitimize it.
3. Provider-specific data is namespaced: generic, portable state is canonical; vendor fields are optional detail keyed by provider, never canonical.
4. Provider-specific actions never pollute the core action set; deep work hands off to the specialist tool via deep links.
5. Adding a provider must not require redesign; removing one must not corrupt state (see Capability First).
6. UI language stays neutral: workflows ("safe secrets"), not product names ("Vault UI") (see Copy and Language).
7. Expansion without regression: enrichment reads as an add-on to a surviving concept —
   ```text
   Source Control
     Basic: local repository tracking
     Connected: Gitea — adds reviews, PRs, remote status
   ```
   — never as a takeover.
8. A provider's absence or failure renders as honest capability state, not a broken section.

## RATIONALE

Vendor-shaped UIs make every provider migration a UX rewrite; vendor-shaped data makes every migration a data migration. Neutrality is what makes "replaceable machinery" real for users: swap the machinery, keep the world.

## HUMAN EXAMPLES

- The user sees "Source Control: healthy, 3 repos changed today (via Gitea)" — and switching to GitHub changes only the "(via ...)" part.
- A setup with no cloud AI renders as a complete, calm product — not a half-broken demo of the "real" thing.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Capability data model: semantic core fields + namespaced provider detail (`providers.gitea.*`).
- Manifest-driven components: UI renders the capability registry and status vocabulary, not hardcoded provider lists.
- Deep-link metadata is optional enrichment; nothing load-bearing.

## GOOD EXAMPLES

```json
{"capability": "source_control", "status": "healthy",
 "provider": {"type": "gitea", "namespaced": {"org": "acme"}}}
```

## ANTI-PATTERNS

- A "Gitea" nav item.
- A UI where the local-only setup looks like an error state.
- Canonical `world.json` fields named after a vendor's API.
- A "Connect GitHub" button that is the only path to source control concepts.

## ACCEPTANCE CHECKS

- Is any vendor name part of navigation or canonical schema? (Must be no.)
- Do all five legitimate configurations render as complete products?
- Does provider detail live under a namespaced key?