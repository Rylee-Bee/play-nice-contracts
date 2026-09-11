---
contract_id: portability-and-ownership
title: Portability and Ownership
version: 1.0.0
status: canonical
layer: core
applies: [data, configuration, infrastructure]
triggers: [new-service, new-database, storage-decision, export, vendor-choice]
rationale: Users must be able to leave any tool with their data and their truth. No system should quietly become the only place a person's or organization's state exists.
---

<!-- contract-receipt: tundra-orchard-echo -->

# Portability and Ownership

## Purpose

Keep data and canonical truth owned by its owner, not by whichever tool currently holds it. A person or project must be able to leave any tool with their state, history, and configuration intact.

## NORMATIVE RULES

1. Canonical data has a working export path that includes enough structure to be meaningful outside the tool (not just a raw database dump unless that dump is documented and stable).
2. Import paths exist for the same formats, so migration in is as supported as migration out.
3. Export includes provenance where it exists; provenance survives the round trip.
4. No lock-in by omission: the export path and format are documented, and export is tested so it cannot silently rot.
5. Secrets never travel in exports; export formats reference secrets symbolically (`token_env`, `secret_ref`), never inline.
6. Whose state is it? State that could become personal is designed with explicit ownership boundaries from the start — identity, preferences, memory, permissions — even in single-user systems.
7. Configuration stays portable: paths, endpoints, and environment-specific values are parameters, not baked-in constants.

## RATIONALE

Every proprietary silo eventually either dies or holds its users hostage. Both outcomes are survivable only if truth lives in portable formats. Ownership boundaries added later require archaeology; added early, they are cheap.

## HUMAN EXAMPLES

- A journal export is a folder of dated Markdown files with metadata — readable in any editor, importable into a future tool.
- Moving a deployment to a different machine is a documented operation, not a rebuild.
- A single-user app can still say clearly "this data is Rylee's; this data is the system's" — so that multi-user or sharing never requires re-architecture.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Export/import round-trip tests exist for all canonical data.
- Exports are classified (public/private/secret); secret material is structurally excluded.
- Schema versions accompany exported data; importers reject unknown versions clearly instead of misreading them.
- Filesystem paths and endpoints are configurable per environment.

## GOOD EXAMPLES

```text
world-export.json   (canonical data, schema_version, provenance, no secrets)
settings-export.json (capability intent; provider choices, never secrets)
```

## ANTI-PATTERNS

- Export as "dump the SQLite file" with no schema documentation.
- A preference or memory store with no export at all.
- Export that silently drops provenance or classification.
- Identity baked so deeply into one user that multi-user or no-user modes are impossible.
- Absolute paths committed into configuration.

## ACCEPTANCE CHECKS

- Can this system's canonical state be moved to a successor tool today?
- Is the export format documented and round-trip tested?
- Do exports contain zero secret values, structurally, not by convention?
- Does each piece of personal-ish state have an explicit owner?