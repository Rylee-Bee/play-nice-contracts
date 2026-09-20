# play-nice-contracts — project rules

The canonical Play-Nice contract library. Other repos (homelab,
personal-world, vefr) pin revisions of this library through adoption
manifests — changes here ripple outward. This repo is the source of
truth; never copy contract text into other repos, reference it instead.

## Layout

- `contracts/` — normative text, layered: `core` safety/interop floor,
  then `human` experience floor, then project and preference layers.
  A lower layer may never violate a requirement above it.
- `schema/` — JSON Schemas that `contractctl` validates against.
- `tools/contractctl/contractctl.py` — the engine: validate, lock,
  attest, onboard.
- `tools/playnice/playnice.py` — orchestration layer that owns the full
  agent-work lifecycle on top of contractctl.
- `contracts.lock.json` — generated. Must regenerate byte-identical.
- `profiles/` — model/role preference layers.
- `examples/` — real adoption manifests; keep them schema-valid.
- `docs/` — principles and guides derived from, never above, `contracts/`.

## Rules for agents working here

- **Standard library only, Python 3.12.** There is no pyproject and no
  dependency list; adding a dependency is an explicit decision, not a
  convenience.
- **Contract text changes are governance changes.** Propose the diff and
  its rationale before rewriting normative language, and record it in
  `CHANGELOG.md`.
- **This repo is public.** Never place real tokens, hostnames, private
  IPs, or family details anywhere in it. CI scans library surfaces for
  exactly that and the scan is part of the contract.
- **Lock determinism.** Editing contracts means regenerating
  `contracts.lock.json`; two regenerations must be byte-identical.

## Verify (mirrors CI — all must pass before done)

```bash
python3 tools/contractctl/contractctl.py validate
python3 tools/contractctl/contractctl.py lock   # then confirm lock diff is expected
uv run --python 3.12 --with pytest,pyyaml python3 -m pytest tests/ -q
```
