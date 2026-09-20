# play-nice-contracts — project rules

**What this repo is:** the canonical Play-Nice contract library — the
normative contract text (`contracts/`), its JSON Schemas (`schema/`),
and the stdlib-only reference tooling that resolves, validates, locks,
attests, and commits them (`tools/contractctl`, `tools/playnice`).
Consumer repos pin revisions of this library in adoption manifests, so
changes here ripple outward. This repo is the source of truth; never
copy contract text into other repos, reference it instead.

**What this repo is not:** a service, a framework, or the home of any
consumer project's local rules. It is not its own governance body —
contract changes are proposals reviewed by Rylee, not self-appointed.
Project Worlds characters and world content have a different license
and a different home: they must **never** appear in this (MIT, public)
repository.

## What governs what

| Surface | Nature | Change kind |
|---|---|---|
| `contracts/` | the normative text — this library's product | governance change |
| `schema/` | machine shapes for contracts and manifests | governance change |
| `contracts.lock.json` | generated; never hand-edited | regenerate via `lock` |
| `CONTRACT_INDEX.md` | registry: routes, does not govern | maintain with contracts |
| `tools/contractctl/` | reference CLI (18 subcommands; `--help`) | code change |
| `tools/playnice/` | orchestrator; full reference in `docs/PLAYNICE.md` | code change |
| `tests/` | hermetic suite (CI job name is `library`) | must accompany changes |
| `docs/` | non-normative: principles, quick reference, research | prose; never above `contracts/` |
| `harness/` | **EXPERIMENTAL** research — candidate laws are hypotheses with evidence, NOT rules | evidence changes only |
| `profiles/`, `examples/` | preference layer + real adoption manifests | keep schema-valid |
| `VERSION`, `CHANGELOG.md` | library semver, distinct from git revision pins | bump per release rules |
| `LICENSE*`, `SECURITY.md`, `TRADEMARKS.md`, `.github/CODEOWNERS` | licensing (MIT everywhere), threat model, name identity | Rylee-review required |

## The contract gate is dogfooded here

This repo adopts its own library via `.contracts/adoption.yaml`
(`require-current`, `update: review`). Before substantial mutating
work here, run the normal consumer gate:

```bash
contractctl freshness   # then resolve -> read canonical text -> attest -> commit
```

`CONTRACT GATE: PASS` + `CONTRACT COMMITMENT: ACTIVE` before
implementation, exactly as any consumer would. When a merged revision
lands on `main`, `contractctl sync` refreshes the pin — review mode:
ask Rylee before syncing.

## Rules for agents working here

- **Standard library only.** Tooling imports nothing beyond Python's
  stdlib (3.10+; CI pins 3.12). There is no pyproject and no
  dependency list; adding a dependency is an explicit decision, not a
  convenience.
- **Contract text changes are governance changes.** State intent and
  show the diff before rewriting normative language. Per-contract
  semver: PATCH = clarification, MINOR = compatible new rule,
  MAJOR = incompatible. MINOR/MAJOR must rotate the contract's hidden
  receipt — `contractctl validate` enforces this from Git history.
  Record the change in `CHANGELOG.md`; bump `VERSION` only for
  library-level releases.
- **Lock determinism.** Editing `contracts/` means regenerating
  `contracts.lock.json` in the same commit; two regenerations must be
  byte-identical or CI fails.
- **This repo is public.** Never place real tokens, hostnames, private
  IPs, family details, or personal medical history anywhere in it —
  CI's secret/private-material scan is part of the contract. Keep
  `profiles/examples/` preference-shaped, not personal records.
- **Change flow:** work on a branch, open a PR, and ask Rylee. Agents
  may merge only after she explicitly approves. GitHub admin tokens
  can bypass branch protection — **that bypass is off-limits**; do not
  push directly to `main` without her explicit, in-task go-ahead.
- **Evidence over memory.** Claims about contract counts, versions, or
  receipts are verified against this checkout and live CI, not recalled
  from prior sessions.

## Verify (mirrors CI — all must pass before done)

```bash
python3 tools/contractctl/contractctl.py validate
python3 tools/contractctl/contractctl.py lock   # then confirm lock diff is expected/empty
uv run --python 3.12 --with pytest,pyyaml python3 -m pytest tests/ -q
```
