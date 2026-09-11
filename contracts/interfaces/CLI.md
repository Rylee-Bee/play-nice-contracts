---
contract_id: cli
title: CLI
version: 1.0.0
status: canonical
layer: interfaces
applies: [cli, tools]
triggers: [cli-work, tool-design]
rationale: CLIs are first-class surfaces: same capability, same vocabulary, machine-parseable output, quiet success, loud failure, scriptable everywhere.
---

<!-- contract-receipt: timber-latch-basalt -->

# CLI

## Purpose

Make the command line a first-class view of the same capabilities the API and UI expose — operable by humans, scriptable by automation, inspectable by agents.

## NORMATIVE RULES

1. Every important concept is understandable and operable without any other surface: the CLI is a view of the system, never the UI's forgotten sibling.
2. Machine-readable output on demand: `--json` (or equivalent) emits stable, versioned, documented shapes; default output is human-readable.
3. Same capability, same words: CLI verbs and status values use the shared vocabulary (status words, error identifiers) — no CLI-private synonyms for what the API says.
4. Quiet success, loud failure: healthy operations print what they did (short), failures print the full six-question error (see Failure and Degradation) and exit non-zero.
5. Exit codes are a contract: 0 success, non-zero failure, stable across releases; scripts may rely on them.
6. Errors say what to do next; a CLI error that ends in a shrug is a defect.
7. Idempotency-friendly: repeated runs of ensure-style commands are safe and report "no change" honestly (see Idempotency).
8. Destructive commands ask or require explicit flags; `--dry-run`/`--preview` exists where mutation occurs.
9. `--help` is the documentation floor: every command documents purpose, args, flags, and examples; help for humans, not just for the author.
10. Scriptability minimums: no required interactivity for automation paths (flags/env for everything interactive prompts would ask), stable flag names, config over flags over env precedence documented.

## RATIONALE

The CLI-first rule proved itself repeatedly: when the CLI is real, agents, cron jobs, and tired humans all have one reliable path — and the UI can be rebuilt without anyone losing the ability to operate the system. CLIs that were UI-afterthoughts died with their UIs.

## HUMAN EXAMPLES

- `pw status --json` gives an agent the same states the dashboard renders; `pw status` gives a human a one-screen summary.
- A failing deploy command prints: what failed, where, retryable or not, the exact next command to investigate.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- One CLI framework per project; subcommands mirror capabilities.
- `--json` output validates against the same schemas as the API.
- Exit codes tested; help output tested to exist and stay current.

## GOOD EXAMPLES

```bash
$ tool deploy --preview
Would update: web (v1.4.2 → v1.5.0), dns (no change)

$ tool deploy --preview --json
{"changes": [{"service": "web", "from": "1.4.2", "to": "1.5.0"}], "no_change": ["dns"]}
```

## ANTI-PATTERNS

- Interactive prompts with no flag equivalents (unscriptable).
- A CLI that requires reading source code to discover flags.
- Pretty tables with no machine format.
- Exit code 0 on failure "to not break scripts".
- CLI vocabulary that differs from API vocabulary for the same thing.

## ACCEPTANCE CHECKS

- Can every routine operation run headless from a cron job?
- Is `--json` stable, documented, and schema-validated?
- Does failure output answer what/why/still-works/retry/next?
- Do exit codes and flags have stability guarantees?