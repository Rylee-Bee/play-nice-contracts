---
contract_id: copy-and-language
title: Copy and Language
version: 1.0.0
status: canonical
layer: experience
applies: [ui, product, docs, agents]
triggers: [human-facing-work, copywriting, error-messages, documentation]
rationale: Words are interface. Human interfaces translate machine truth into useful language; destructive actions are named by consequence; reading load is shaped for real human eyes.
---

<!-- contract-receipt: amber-wren-marble -->

# Copy and Language

## Purpose

Words are part of the interface. Machine precision stays machine-readable; humans get honest, useful, respect-their-attention language.

## NORMATIVE RULES

1. Human surfaces speak human concepts, not infrastructure vocabulary: "Backups" not "cron-runner-v2"; "Source Control" not "Gitea" (providers are provenance, not navigation — see Provider Neutrality).
2. Errors say what failed, why (if known), what still works, and the next reasonable action — never "Something went wrong."
3. Destructive actions are named by verb and consequence ("Delete these 3 snapshots — permanent"): never vague OK/Yes/Proceed buttons.
4. Reading load is shaped: short sentences; lists and tables over prose walls; no ALL-CAPS headings (flattened word shapes hurt many readers); no walls of text outside disclosure.
5. No manufactured-urgency copy: no guilt, no countdowns, no streaks, no "don't leave!" dark patterns (see Progress and Closure).
6. Empty states are honest and helpful: "No journal entries yet" (not fake data or blank screens); error states distinguish unconfigured, unreachable, and broken (see Explicit State).
7. Humor and personality are welcome where they aid understanding — and never carry operational meaning or mask uncertainty. Never let whimsy become a fog around what is true.
8. Machine-facing surfaces (APIs, logs, schemas) keep stable identifiers and precise values; human translation happens at the presentation boundary, once.

## RATIONALE

Copy is the cheapest interface to get wrong and the most expensive for users: every ambiguous button is a support ticket, every vague error is an investigation, every guilt banner is attention theft. One machine vocabulary plus good human translation serves both audiences.

## HUMAN EXAMPLES

- "Certificate expires in 2 days. Renewal is automatic; no action needed. [History]"
- "Couldn't reach the backup service. Last good backup: yesterday 23:00. [Retry] [View service]"
- "Delete provider 'gitea'? Its 4 saved connections stop working. This cannot be undone. [Cancel] [Delete provider]"

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Error identifiers are stable (machine-facing); human strings are a translation layer, so wording can improve without breaking clients.
- Copy changes are reviewable like code (in-repo strings, not hardcoded art).
- No fake data placeholders anywhere a real value could be labeled unknown.

## GOOD EXAMPLES

```json
{"error": "provider_unreachable", "provider": "gitea",
 "human": "Couldn't reach Gitea. Everything else keeps working."}
```

## ANTI-PATTERNS

- "Error 500 occurred."
- "Are you sure?" on both reset and delete.
- "OOPS! The elves spilled your data 🧝" as the only explanation.
- ALL-CAPS section headers.
- Fabricated "Recent activity" to fill space.

## ACCEPTANCE CHECKS

- Could a newcomer act on every error message without asking someone?
- Are destructive actions' consequences named on the button itself?
- Is any copy manufacturing urgency or guilt?
- Are machine identifiers stable behind the human translation?