---
contract_id: cli
title: CLI
version: 2.0.0
status: canonical
layer: surfaces
applies: [clis, tools, automation]
triggers: [cli, command line, terminal, shell, script, flags, exit code]
rationale: The command line is a first-class view of the system: usable by a tired human, scriptable by cron, inspectable by agents.
---

<!-- contract-receipt: stone-quarry-copper -->

# CLI

## In short

Quiet success, loud failure. Human text by default, stable `--json` on
request, meaningful exit codes, and a next step after every error.

## Applies when

You build or change a command-line tool. Not this contract's job: the
shared machine/human shape itself (see one-truth-two-views) or HTTP
details (api).

## Rules

1. The CLI is a full view of the system, never the UI's forgotten
   sibling: every routine operation can run headless. (MUST)
2. Nothing forces interactivity: every prompt has a flag or environment
   equivalent for automation paths. (MUST)
3. Human-readable by default, `--json` on request; both emit the same
   states and words the API uses. (MUST)
4. Use the shared vocabulary: the status words (see the floor, rule 8) and
   the error identifiers, with no CLI-private synonyms. (MUST)
5. Quiet success, loud failure: a healthy run prints briefly what it
   did; a failure prints what happened, why (if known), what still
   works, whether to retry, and the exact next command. (MUST)
6. Exit codes are a contract: 0 success, non-zero failure, stable across
   releases; scripts rely on them. (MUST)
7. Repeated runs of ensure-style commands are safe and report "no
   change" honestly. (MUST)
8. Destructive commands ask or require an explicit flag; `--dry-run` or
   `--preview` exists wherever the command changes something. (MUST)
9. `--help` is the documentation floor: purpose, arguments, flags, and
   an example for every command, written for a newcomer. (MUST)
10. Flag names stay stable across releases, and the precedence of
    config, flags, and environment is documented. (MUST)

## Examples

- Good: `tool deploy --preview` prints "Would update: web (v1.4.2 →
  v1.5.0), dns (no change)".
- Good failure: names what failed, where, whether to retry, and prints
  the command that investigates — then exits non-zero.
- Bad: a pretty table with no `--json`; exit 0 on failure "to not break
  scripts"; flags discoverable only by reading source.

## Why

When the CLI is real, agents, scheduled jobs, and tired humans share one
reliable path, and the UI can be rebuilt without anyone losing the
ability to operate the system.

## You're done when

- Every routine operation runs headless from a scheduled job.
- `--json` output validates against the API's schemas.
- Every error names a next step and exits non-zero.
