# play-nice-contracts — rules for changing this library

> **Using Play-Nice in your own project? This file is not for you.** Read
> [the floor](contracts/everyone/FLOOR.md) and the pack for what you're
> building ([index](CONTRACT_INDEX.md)). This file is for agents and people
> who edit this library itself.

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
and a different home: they must never appear in this public repository.
(Prose rule — no scanner checks for it; machines can't yet recognize a
character. Don't be the one who proves it wrong.)

## Licensing map (test-enforced: `tests/test_license_map.py`)

- contracts + docs text: **CC BY-SA 4.0** (attribution required;
  derivatives of the text stay open; your code unaffected)
- tooling, schemas, lockfile, tests: **MIT**
- name and identity: `TRADEMARKS.md` (descriptive; 🐝 acknowledgement
  is optional credit, never endorsement)

## How to run `contractctl`

`contractctl` is **a file, not an installed command**. Everywhere in
this repo's docs, `contractctl` means either the executable shim or the
Python file directly (identical behavior — the shim execs the file):

```bash
./tools/contractctl/contractctl             # from a library checkout
python3 "$PLAY_NICE_LIBRARY/tools/contractctl/contractctl.py"  # as a consumer
```

Consumers typically `alias` it once. There is no installer by design
(stdlib-only). The same applies to `./tools/playnice/playnice`.
One-command local verify (mirrors CI): `./tools/check.sh`.

## What governs what

| Surface | Nature | Change kind |
|---|---|---|
| `contracts/` | the normative text — this library's product | governance change |
| `schema/` | machine shapes for contracts and manifests | governance change |
| `contracts.lock.json` | generated; never hand-edited | regenerate via `lock` |
| `CONTRACT_INDEX.md` | registry: routes, does not govern | maintain with contracts |
| `tools/contractctl/`, `tools/playnice/` | reference CLI + orchestrator (`docs/PLAYNICE.md`) | code change |
| `tests/` | hermetic suite (CI job name is `library`) | must accompany changes |
| `docs/` | non-normative: principles, quick reference, research | prose; never above `contracts/` |
| `harness/` | **EXPERIMENTAL** research — candidate laws are hypotheses with evidence, NOT rules | evidence changes only |
| `profiles/`, `examples/` | preference layer + real adoption manifests | keep schema-valid |
| `VERSION`, `CHANGELOG.md` | library semver, distinct from git revision pins | bump per release rules |
| `LICENSE`, `contracts/LICENSE.md`, `docs/LICENSE.md`, `SECURITY.md`, `TRADEMARKS.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS` | licensing, threat model, identity, review intent | Rylee-review required |

## The contract gate is dogfooded here

This repo adopts its own library via `.contracts/adoption.yaml`
(`require-current`, `update: automatic`: revisions are reviewed as
they merge through PRs, so the pin advances mechanically afterward;
the gate still re-runs fresh every session). Before substantial
mutating work here, run the consumer gate:

```bash
contractctl freshness   # CURRENT expected; then:
contractctl resolve --manifest .contracts/adoption.yaml --task "<your task>"
# read each resolved contract's canonical file, then:
contractctl attest --manifest .contracts/adoption.yaml --task "<task>" --impact <id>="<sentence>" ...
contractctl commit --manifest .contracts/adoption.yaml --task "<task>" --impact <id>="<sentence>" ...
```

`CONTRACT GATE: PASS` + `CONTRACT COMMITMENT: ACTIVE` before
implementation. Commitment artifacts land in `.contracts/sessions/`
(gitignored) — never commit them.

## Rules for agents working here

- **Standard library only.** Tooling imports nothing beyond Python's
  stdlib (3.10+; CI tests 3.10–3.12). `pyproject.toml` exists solely
  to declare test-only extras (`pip install ".[dev]"` → pytest, pyyaml);
  there is no build-system table and nothing is pip-installed as runtime.
  Adding a runtime dependency remains an explicit decision, not a
  convenience.
- **Contract text changes are governance changes.** State intent and
  show the diff before rewriting normative language. Per-contract
  semver: PATCH = clarification, MINOR = compatible new rule,
  MAJOR = incompatible. MINOR/MAJOR must rotate the contract's hidden
  receipt — `contractctl validate` enforces this from Git history.
  Record every landed change in `CHANGELOG.md` (that includes changes
  that only touch docs or licensing — this repo eats its own
  continuity dog food); bump `VERSION` only for library-level releases.
- **Lock determinism.** Editing `contracts/` means regenerating
  `contracts.lock.json` in the same commit; two regenerations must be
  byte-identical or CI fails.
- **This repo is public.** Never place real tokens, hostnames, private
  IPs, family details, or personal medical history anywhere in it —
  CI's secret/private-material scan is part of the contract. Keep
  `profiles/examples/` preference-shaped, not personal records.
- **Commit identity is scrubbed, machine-enforced.** Only GitHub
  `*+*@users.noreply.github.com` or `*@*.invalid` author/committer
  emails may enter history — the CI identity guard fails closed on
  raw mailboxes, machine hostnames, and tunnel domains. GitHub
  squash/merge wrappers (committer `noreply@github.com`) are exempt:
  the account's commit email should also be set to noreply (GitHub →
  Settings → Emails) so even wrappers stay clean.
- **Change flow:** work on a branch, open a PR, and ask Rylee. Agents
  merge only after her explicit in-task approval; when her token
  cannot approve its own PR, an admin merge *with that approval* is
  the sanctioned path — say so in the PR. Never direct-push `main`;
  never use admin bypass she didn't explicitly grant for that change.
- **Evidence over memory.** Claims about counts, versions, receipts, or
  history are verified against this checkout and live CI, not recalled.
  Prefer writing no count over one that can rot.

## Verify (mirrors CI — all must pass before done)

```bash
./tools/check.sh   # validate + double-regen lock determinism + full suite
                   # + secret scan + identity guard — one command, mirrors CI
```

Step-by-step equivalents:

```bash
python3 tools/contractctl/contractctl.py validate
python3 tools/contractctl/contractctl.py lock   # then confirm lock diff is expected/empty
uv run --python 3.12 --with pytest,pyyaml python3 -m pytest tests/ -q
```
