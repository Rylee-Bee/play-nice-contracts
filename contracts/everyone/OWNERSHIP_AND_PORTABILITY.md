---
contract_id: ownership-and-portability
title: Ownership and Portability
version: 2.0.0
status: canonical
layer: everyone
applies: [humans, agents, services, tools, data]
triggers: [export, import, storage, vendor, provider, lock-in, backup, database, configuration, migration]
rationale: Tools are temporary, so the owner's truth must outlive every one of them and stay movable on the owner's terms.
---

<!-- contract-receipt: kiln-pebble-truss -->

# Ownership and Portability

## In short

Keep truth in durable formats no single tool owns. Every export is tested,
documented, and secret-free; the owner can leave with everything.

## Applies when

You store, shape, or move someone's data or canonical facts — or pick the
tool that does. The floor requires respecting what isn't yours (see the
floor, rule 16) and keeping secrets out (rule 11); this contract makes
leaving possible.

## Rules

1. **Canonical truth lives in durable, inspectable formats** — plain
   files, git, append-only journals, explicit schemas — wherever
   practical. Machinery may accelerate or present truth; it may not own
   it. (MUST)
2. **No tool may be the only copy.** If deleting a tool would erase
   knowledge, fix the architecture. Anything that becomes durable fact —
   including AI conversation output — is committed to canonical storage
   with its provenance. (MUST)
3. **Derived is rebuildable.** Indexes, caches, compiled and generated
   artifacts declare their canonical source and a working rebuild
   command; a rebuild check is runnable, so silent divergence is
   detectable. (MUST)
4. **Provider swaps feel like changing a part.** Keep canonical data
   provider-neutral and provider-specific data namespaced; if a swap
   needs surgery, fix the boundary first. (MUST)
5. **Every piece of canonical data has a tested, documented export** with
   enough structure to be meaningful outside the tool — not a raw dump,
   unless the dump format is itself documented and stable. An import path
   for the same format exists. (MUST)
6. **Exports survive the round trip.** Provenance and structure come back
   intact; schema versions travel with the data, and importers reject
   unknown versions clearly instead of misreading them. (SHOULD)
7. **Secrets never travel.** Exports reference them symbolically
   (`token_env`, `secret_ref`); the exclusion is structural, not by
   convention. (MUST)
8. **Ownership is decided up front.** State that could become personal —
   identity, preferences, memory, permissions — gets a named owner from
   the start, even in single-user systems, so sharing or moving never
   becomes an archaeology project. (MUST)
9. **Leaving is a documented operation.** Moving data or a deployment to
   a successor tool is a written path, not a rebuild from memory.
   Configuration stays portable: paths, endpoints, and environment
   values are parameters, not baked-in constants. (MUST)

## Examples

- Good: a journal export is a folder of dated Markdown with metadata —
  readable in any editor, importable by a future tool, provenance intact.
- Good: deleting the search index is an inconvenience, not a loss: one
  command rebuilds it from source files.
- Bad: the only record of a decision is a comment in a design tool, and
  the only "export" is a database file nobody documents.

## Why

Every tool eventually changes, costs more, or disappears. Owners who can
leave are choosing to stay, which is the only honest basis for a
dependency. Plain, versioned, portable files are also the friendliest
format for every future reader — person, agent, or program.

## You're done when

- You can name what survives if the current tool vanished today, and
  how: the tested export path.
- Every derived artifact has a rebuild command that actually runs.
- Every stored thing has a named owner, and a real export was opened
  once outside the source tool.
- A scan of a real export found zero secret values.
