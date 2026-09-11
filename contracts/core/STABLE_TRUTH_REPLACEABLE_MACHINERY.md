---
contract_id: stable-truth-replaceable-machinery
title: Stable Truth, Replaceable Machinery
version: 1.0.0
status: canonical
layer: core
applies: [architecture, data, agents, design, infrastructure]
triggers: [new-dependency, storage-decision, index, cache, tooling, migration]
rationale: Every tool is temporary; the truth it manages must not be. Canonical truth lives in durable, inspectable formats that survive the replacement of any model, service, index, or framework.
---

<!-- contract-receipt: quiet-bramble-fable -->

# Stable Truth, Replaceable Machinery

## Purpose

Ensure that replacing any piece of machinery — AI model, agent harness, database, vector store, index, embedding model, API gateway, source-control host, deployment tool, monitoring platform, design tool, UI framework, automation framework — never destroys the truth it was managing.

## NORMATIVE RULES

1. Canonical truth lives in durable, inspectable formats (plain files, Git, append-only journals, explicit schemas) wherever practical.
2. Anything derivable is derived, not canonical: indexes, vector stores, semantic caches, compiled artifacts, and generated files must be rebuildable from canonical sources, and a rebuild path must exist.
3. No tool may become the only place truth exists. If deleting a tool would erase knowledge, the architecture is wrong.
4. Machinery may accelerate, enrich, automate, or present truth. It may not own truth.
5. Swapping a provider for another must feel like changing a part, not surgery. If it feels like surgery, the boundary is wrong.
6. AI output that becomes durable truth is committed to canonical storage with provenance — not left living only inside a conversation, model, or session.

## RATIONALE

The ecosystem repeatedly rebuilt knowledge after tools changed: model migrations stranded context living in chats; index rebuilds lost data that had no canonical source. Durable, plain, inspectable truth also plays nice with humans, agents, Git, and future tools — it is the most interoperable format there is.

## HUMAN EXAMPLES

- Your journal, decisions, and contracts live in Markdown files under Git — not in a SaaS wiki or one AI assistant's memory.
- Deleting the search index is an inconvenience, not a catastrophe: everything is re-indexable from source files.
- Switching from one vector database to another costs configuration and a rebuild script, never your data.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Every derived artifact declares its canonical source and its rebuild command.
- Exports exist for canonical data (import/export is a first-class feature, not an afterthought).
- Provider-specific data is namespaced; canonical data is provider-neutral.
- Derived artifacts are drift-checkable (`build --check`), so silent divergence is detectable.

## GOOD EXAMPLES

```text
world.json (canonical)
  ↓ reindex
search index (derived, rebuildable, never canonical)
```

## ANTI-PATTERNS

- The only copy of a design decision is a Figma comment.
- Conversation history with an AI as the sole record of what was decided.
- A vector store as the only place memories exist, with no export.
- Generated code that must be edited by hand while a generator still claims ownership.
- Canonical schema expressed as the internal shape of vendor product X.

## ACCEPTANCE CHECKS

- For each piece of machinery: what exactly survives its replacement?
- Is there a working rebuild path for every derived artifact?
- If this tool vanished today, what truth would be unrecoverable?
- Is any AI-generated truth persisted canonically with provenance?