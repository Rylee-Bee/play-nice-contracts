# License - contracts/ (canonical contract specifications)

The contract specifications in this directory — and in any subdirectory
thereof — are licensed under the **MIT License**, exactly like the
tooling and schemas elsewhere in this repository (see `../LICENSE`).

## What that means in practice

- You may copy, quote, adapt, and redistribute the contract text —
  commercially or not — with no obligations beyond the MIT terms.
- Attribution is not legally required, but it is appreciated and
  consistent with the `provenance-and-audit` contract: when you adapt
  these contracts, cite the canonical repository and the revision you
  adopted.
- Adoption discipline is not a copyright term. "Consume, don't fork"
  (adoption manifests + pinned revisions, `contractctl resolve`) is how
  this library asks projects to behave. That is governance, not a
  license restriction.
- The Play Nice name and project identity are governed separately in
  `TRADEMARKS.md`; an open-content license does not license the name.

## Why one license for the whole repository

The contracts are normative prose; the tooling, schemas, and tests are
code. Splitting them across license families (a prior revision used
MPL-2.0 + CC BY-SA 4.0) created three answers to "what license is this
project?" and confused consumers and agents alike. One intent, one
license: MIT, everywhere in this repository. Character and world
content from Project Worlds lives in other repositories under their own
terms and is **not** covered by anything here.
