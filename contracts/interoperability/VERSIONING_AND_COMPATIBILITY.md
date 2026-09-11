---
contract_id: versioning-and-compatibility
title: Versioning and Compatibility
version: 1.0.0
status: canonical
layer: interoperability
applies: [api, schema, configuration]
triggers: [schema-change, api-change, always]
rationale: Breaking behavior must never silently appear behind the same contract. Declared versions, explicit migration, and clear failure on the unknown keep systems from quietly misinterpreting each other.
---

<!-- contract-receipt: opal-dell-prairie -->

# Versioning and Compatibility

## Purpose

Make contracts, schemas, and APIs trustworthy across time: versions are declared, breaks are explicit, unknown versions fail clearly, and compatibility is testable.

## NORMATIVE RULES

1. Schemas and APIs declare versions explicitly (`schema_version`, API version headers/paths). No contract is unversioned.
2. Breaking behavior never silently appears behind the same version. Breaking changes: new MAJOR version and an explicit migration path.
3. Compatible additions may ship as MINOR; clarifications as PATCH. Consumers reject what they cannot understand rather than guessing at it.
4. Unknown versions fail clearly: "schema v9 not supported by this reader (supports ≤ v7)" — never silent reinterpretation of incompatible state.
5. Data carries its schema version with it; readers validate before interpreting. Version stamps are the first field checked, not an afterthought.
6. Compatibility should be testable: conformance suites exist for each published contract surface and run against every supported version combination that matters.
7. Deprecation is announced, documented, and given a migration window; removal is an explicit major event, not a silent Tuesday.
8. Machine-readable versioning follows semver semantics consistently across the library: PATCH = clarification only; MINOR = compatible new rule; MAJOR = meaningfully changed/incompatible behavior.

## RATIONALE

Two failure classes motivated this contract: silent reinterpretation (data written by a newer schema read as garbage by an older reader) and silent breaking (an API change discovered by the fifth consumer's outage). Declared versions plus fail-closed readers prevent both — cheaply, mechanically, at the boundary.

## HUMAN EXAMPLES

- Opening an old export says "this backup is from schema v3; current is v5; here's the migration" — instead of a page of nonsense.
- A CLI talking to an older server gets "version mismatch: server v2, client needs v3" — not subtle wrong behavior.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Every store, export, and payload carries `schema_version`; loaders check it first and fail closed on unknown.
- Conformance tests run per supported version pair where versions interact.
- Lockfiles/pins record exact versions + hashes so consumers detect drift deterministically (see contracts.lock.json).

## GOOD EXAMPLES

```json
{"schema_version": 2, "data": {...}}
// reader: "schema_version 2 not supported (expected 1.x)" → explicit error
```

## ANTI-PATTERNS

- "We'll just add that field; old readers will ignore it" — without versioning rules for what ignoring means.
- Version-less config formats that change meaning between releases.
- Renaming a JSON key in a minor release.
- Guess-the-shape parsers that "try their best" with unknown versions.

## ACCEPTANCE CHECKS

- Does every contract surface declare a version?
- Does a reader of an unknown version fail loudly?
- Is any breaking change shippable without a version bump? (Must be no.)
- Are deprecations announced with migration paths?