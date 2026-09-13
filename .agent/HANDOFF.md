# Epistemic humility contribution — 2026-09-13

Start: clean main at `cd7f625b374dc738c08d8ce1406c3f617b97682a`.
Work branch: `feat/assume-unknown`. Owner requested normal publication subject
to repository policy; main requires a PR, one approval, and `library` status.
Do not bypass these rules. No force push or protection mutation is authorized.

Changed: `assume-unknown` 1.0.0 in `contracts/core/ASSUME_UNKNOWN.md`, library
0.7.0, founding contract 1.6.0 with rotated receipt, all example adoptions,
registry, session guidance, attributed case study and adoption decision.
Lock generation now uses portable paths and LF bytes. CI check name matches
existing branch protection. Schemas and comprehension claims are unchanged.

Verification: `python -m pytest tests -q` -> 113 passed on Windows Python 3.11.
See the commit's GitHub checks for Linux CI verification.
Library validation, workflow parse, two byte-identical lock regenerations,
and public/private-material scan passed locally. Only `assume-unknown` and
`play-nice-together` entries differ in the lock; unrelated work was preserved.

Reservations: the Worlds incident is reported provenance, not independent
runtime verification; neither test success nor an attestation proves understanding.
Consumer pins are not changed automatically. The library PR still needs normal
review before main adoption. Private Lore provenance is intentionally not linked
from public files.

Next: inspect the PR for branch `feat/assume-unknown`, confirm its `library`
check and required approval, then merge normally when eligible. If review requests
changes, edit the canonical contract, version/receipt as appropriate, regenerate
lock, rerun gates, and re-attest the changed bundle.
