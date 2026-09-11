---
contract_id: machine-readable-output
title: Machine Readable Output
version: 1.0.0
status: canonical
layer: interfaces
applies: [cli, api, tools]
triggers: [tool-design, cli-work, api-work, agent-tooling]
rationale: Automation, agents, and future tools consume machine-readable output as their primary interface: stable shapes, explicit versions, honest fields, no parsing of human prose.
---

<!-- contract-receipt: dovetail-gable-jetty -->

# Machine Readable Output

## Purpose

Give non-human consumers (scripts, agents, pipelines, future tools) a first-class interface: output they can parse, trust, version, and build on — never scraped human prose.

## NORMATIVE RULES

1. Every machine-relevant surface offers a machine format: CLIs get `--json`, APIs are already machine-shaped, logs are structured where consumed by tools, exports carry schemas.
2. Machine output is stable: field names, shapes, and error identifiers are contracts; breaking changes bump versions (see Versioning and Compatibility).
3. Machine output is explicit about version and time: schema/version markers and `observed_at`/`source` timestamps are included — never assumed from context.
4. Missing/unknown is explicit: `null`, absent-with-schema, or the `unknown` status — never invented defaults, never empty-string-as-truth, never "0 means we didn't check".
5. Human-readable output never carries machine burden, and vice versa: human prose is generated FROM machine state, not parsed INTO it.
6. Machine output carries no secrets and respects classification (see Secrets, Data Classification): exports and logs are structurally safe for sharing.
7. Errors are identifiers + context + retryability in machine form; the human translation lives beside, not instead (see Failure and Degradation).
8. Bulk output is paginated or bounded with explicit totals; consumers never guess whether they received everything.
9. Machine consumers get deterministic output where determinism is possible: same input, same bytes (sorted keys where sensible) — diffable and lockfile-friendly.

## RATIONALE

Every "just grep the output" integration broke when wording changed; every agent that read human prose misread it. Stable machine shapes are the cheapest interoperability surface in existence: they let a future tool consume the system without a human in the loop, and they let the human surface evolve freely above them.

## HUMAN EXAMPLES

- A status line a human reads as "Everything looks good." is `{status: healthy, ...}` to the script — same event, both served.
- An agent consumes `tool list --json`, plans, then calls `tool show <id> --json` — never parsing a table.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- One serializer per surface, schema-validated in tests; machine formats documented alongside human formats.
- Deterministic serialization where the output feeds locks/diffs.
- Version fields checked by loaders before interpretation.

## GOOD EXAMPLES

```json
{"schema": "tool/status-v1", "generated_at": "2026-09-11T14:02:00Z",
 "status": "healthy", "warnings": [], "source": "healthcheck"}
```

## ANTI-PATTERNS

- Parsing table output with regex in three scripts (that's three future breakages).
- Machine fields whose meaning depends on which human locale rendered them.
- `{ok: true}` with no version, timestamp, or source.
- Zero-values doubling as "unknown".

## ACCEPTANCE CHECKS

- Can every machine consumer get what it needs without parsing human prose?
- Are machine shapes schema-validated and version-marked?
- Is anything machine-readable that leaks secrets? (Must be no.)
- Is the output deterministic where diffability matters?