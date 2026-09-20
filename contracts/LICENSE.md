# License - contracts/ (canonical contract specifications)

The contract specifications in this directory — and in any subdirectory
thereof — are licensed under the **Creative Commons Attribution-ShareAlike
4.0 International License (CC BY-SA 4.0)**.

Full license text: <https://creativecommons.org/licenses/by-sa/4.0/legalcode>
Human-readable summary: <https://creativecommons.org/licenses/by-sa/4.0/>

## The license map of this repository

| What | Where | License |
|---|---|---|
| Contract text (normative prose) | `contracts/` | CC BY-SA 4.0 (this file) |
| Documentation and philosophy | `docs/` | CC BY-SA 4.0 (`docs/LICENSE.md`) |
| Tooling, schemas, lockfile, tests | `tools/`, `schema/`, `tests/`, root | MIT (`LICENSE`) |
| Name and identity | `TRADEMARKS.md` | descriptive, not a license grant |

`tests/test_license_map.py` fails CI if these files ever disagree.

## What that means in practice

- You may copy, quote, adapt, translate, and redistribute the contracts
  verbatim — commercially or not.
- Attribution (the BY) is a **legal term**, not a favor: cite the
  canonical repository and the revision you adopted. The 🐝
  "Implements Play Nice" acknowledgement in `TRADEMARKS.md` is welcome
  but optional.
- Share-alike (the SA) binds **derivatives of the contract text only**:
  adaptations of these contracts must stay CC BY-SA. Your own code,
  worlds, and project contracts are unaffected — adoption manifests
  *reference* these contracts and do not derive from their prose.
- Adoption discipline is governance, not copyright: "consume, don't
  fork" (pinned revisions, `contractctl resolve`) is how this library
  asks projects to behave.

## Why CC BY-SA for the lessons

The library exists so these lessons keep being applied instead of
re-learned. CC BY-SA makes credit mandatory and derivatives stay open:
sharing with a spine. This choice was established deliberately on
2026-09-13, briefly overwritten by a same-day "MIT everywhere" pass on
2026-09-20, and restored after the owner reviewed the sequence — all
recorded honestly in `CHANGELOG.md`. Code (tooling, schemas, tests)
separately moved from that baseline's MPL-2.0 to MIT: simpler for
adopters, and the copyleft protection was never the point of a
stdlib-only reference CLI.
