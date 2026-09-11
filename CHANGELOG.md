# Changelog

All notable changes to the play-nice-contracts library. Per-contract semver: PATCH = clarification, MINOR = compatible new rule, MAJOR = incompatible behavior change.

## [0.1.0] — 2026-09-11

Initial library.

### Added
- 60 canonical contracts across 8 layers (core, human, experience, interoperability, security, engineering, agents, interfaces), each with machine-readable front matter, a unique hidden receipt, and the dual-use body structure.
- Schemas: `contract.schema.json`, `adoption.schema.json`, `attestation.schema.json` (attestation + operational commitment), `capability.schema.json`, `status.schema.json`.
- `contractctl` CLI (stdlib-only Python): `list`, `show`, `validate`, `resolve`, `lock`, `attest`, `commit` (CONTRACT OPERATIONAL COMMITMENT v1), `session-status`, `verify-attestation`, `adopt`, `status`.
- `contracts.lock.json` (deterministic id/version/path/sha256/receipt/status pinning), derived bundle receipts, and bundle SHA-256 for commitment artifacts.
- Operational commitment machinery: ACTIVE only after PASS gate with complete task-impact; exact bundle recording; stale-bundle invalidation; task-change re-resolution detection; worker inheritance (parent bundle required, parent constraints may not be weakened); session artifact (`.contract-commitment.json`, gitignored, secret-free).
- Example adoption manifests: Personal World, VEFR, homelab.
- Profiles: `baseline.yaml`, `profiles/examples/rylee.yaml`.
- Standard session prefix (complete gate order: resolve → read → verify → impact → conflicts → attestation → commitment → ACTIVE → work) and final handoff standard with CONTRACTS bundle/gate/commitment reporting (`examples/session-handoff.md`).
- Test suite covering library invariants, resolution, attestation pass/fail paths, lock drift detection, and the full commitment lifecycle.
- `visual-fidelity-and-composition` contract encoding the composition-drift lesson from the Personal World UAT (tokens can stay synchronized while the product drifts from design intent; composition requires deterministic and/or human/browser gates, D0–D4 verification levels, component gravity rules, one canonical design pointer, compare-before-code AI gate).

### Changed
- `contract-attestation` 1.0.0 → 1.1.0 (MINOR): added the OPERATIONAL COMMITMENT stage — the full gate order, the canonical commitment text, worker inheritance/propagation tree, conflict behavior (BLOCKED/INACTIVE as compliant), and re-commitment on scope change.