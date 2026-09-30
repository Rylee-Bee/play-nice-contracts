# AGENTS.md

**Using Play-Nice in a project (including a copy under `vendor/`)?**
Read [the floor](contracts/everyone/FLOOR.md), then the pack for what you're
building ([index](CONTRACT_INDEX.md)). Start your handoff with the proof line
from [contract-proof](contracts/work/CONTRACT_PROOF.md). Nothing else here
is needed.

**Changing this library itself?** Read
[docs/MAINTAINING.md](docs/MAINTAINING.md) first: tests, CI, versioning, the
dogfooded contract gate, and the full rules for agents working here. The
short version:

- Before calling work done, run `./tools/check.sh`; it must end with
  `CHECK: PASS` (it mirrors CI job `library`: validate, lock determinism,
  tests, secret scan, identity guard).
- Editing `contracts/` or `schema/` is a governance change: state intent,
  bump that contract's semver, and in the same commit run
  `python3 tools/contractctl/contractctl.py lock` and commit
  `contracts.lock.json`. Never hand-edit the lock.
- `tools/` stays Python standard library only; tests in `tests/` accompany
  code changes.
- Every landed change gets a `CHANGELOG.md` entry under `[Unreleased]`,
  docs-only changes too.
- This repo is public: no tokens, hostnames, private IPs, absolute home
  paths (write `~`), or personal details. Commit emails must be GitHub
  noreply or `.invalid`.
- Work on a branch and open a PR. Rylee approves and merges; never push
  `main`. Licensing and identity files (`LICENSE`, `TRADEMARKS.md`,
  `SECURITY.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS`) need her review.
