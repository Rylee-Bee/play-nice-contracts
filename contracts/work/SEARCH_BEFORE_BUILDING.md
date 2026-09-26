---
contract_id: search-before-building
title: Search Before Building
version: 2.0.0
status: canonical
layer: work
applies: [agents, humans, tools, services, architecture]
triggers: [new tool, new library, new dependency, abstraction, new subsystem, framework, package, vendor, build from scratch, new schema, cache, queue, scheduler]
rationale: New things are easy to add and hard to remove, so an existing thing that already owns the job beats a new parallel one.
---

<!-- contract-receipt: cobble-zephyr-pine -->

# Search Before Building

## In short

Before building anything new — a tool, service, schema, or a pulled-in
library — look for what already owns that job. Extend it, or record
why you couldn't. Keep the dependency surface small and pinned.

## Applies when

Adding a subsystem, service, abstraction, or dependency, or reaching
for a new tool. Not its job: how the new thing must behave once it
exists (its own pack covers that).

## Rules

1. Before adding anything new — subsystem, service, daemon, framework,
   database, schema, cache, queue, agent, abstraction — check what
   already owns that responsibility and genuinely consider extending
   it. (MUST)
2. Prefer extending a coherent existing thing to building a parallel
   one, even when the parallel one would look cleaner on its own.
3. If you add the parallel concept anyway, record the reason: what you
   inspected, why extension wasn't enough, and where the boundary
   between the two concepts runs. (MUST)
4. Do the same search before a dependency: name the problem it removes,
   the complexity it adds, and why nothing existing can cover it.
5. Choose boring: small, stable, well-maintained things with plain APIs
   beat clever novel ones. Never take a framework for one utility
   function.
6. Pin what must be reproducible: committed lockfiles, fixed versions
   in build paths, integrity checks where the ecosystem has them, no
   `curl | sh` in a build. Review dependency changes like code. (MUST)
7. Two dependencies doing the same job is a defect: justify the overlap
   in writing, or remove the old one in the same change. (MUST)
8. An optional dependency must never become a hidden requirement for
   core operation; keep providers at the edges so the core boots
   without them (see testing-and-evidence, rule 2).
9. Prefer small files, explicit schemas, plain APIs, deterministic
   logic, and visible state. Don't add complexity just because an
   agent could manage it.
10. Retire complexity when its upkeep costs more than its value.
    Replacing a big thing with a smaller one is a good outcome,
    recorded as success.
11. Generated or vendored files state their source and how to
    regenerate them.
12. When several good ideas compete, finish or park open work before
    opening a new lane (see bounded-work).

## Examples

- Good: "We need job scheduling" → the search finds an existing
  scheduler to extend, instead of a second scheduler that overlaps the
  first by 80%.
- Good: a cache-library proposal is answered with "what does the
  existing 30-line TTL map not do?" — it dies or survives with
  evidence either way.
- Bad: a dashboard that tracks the other dashboards, built because no
  one looked at what the watched system already exposed.

## Why

Every system that grew parallel mechanisms paid for them later in
maintenance, drift, and arguments about where truth lives. A small
dependency surface keeps builds reproducible and replacements possible;
searching first keeps one system per responsibility.

## You're done when

- For every new thing this cycle, a record names what was inspected
  and why extension wasn't enough.
- The build reproduces from the lockfile alone, with nothing floating.
- No core boot path depends on an optional dependency.
- Something was retired recently, or the search proved everything
  current earns its keep.
