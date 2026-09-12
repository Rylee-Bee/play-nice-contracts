# Changelog

All notable changes to the play-nice-contracts library. Per-contract semver: PATCH = clarification, MINOR = compatible new rule, MAJOR = incompatible behavior change. Meaningful contract changes (MINOR/MAJOR) rotate the hidden receipt — enforced mechanically by `contractctl validate` via Git history.

## [0.2.1] — 2026-09-12

Fix-only hardening pass (no new philosophy, no scope expansion).

### Fixed
- **CI workflow YAML**: the secret/private-material scanner step used a multiline heredoc without a YAML block scalar, so the workflow never parsed and GitHub could not create a job. Now `run: |` with a proper block; CI additionally self-validates its own YAML (job and expected steps present) before running the library checks.
- **Worker attestation covers the exact inherited union**: `make_attestation(..., resolved_ids=...)` now attests the exact union set computed by `build_commitment` (no re-resolution of only the worker's own task). Governing invariant enforced and asserted: the contract set attested is exactly the contract set committed (defensive mismatch check raises). Inherited parent-only contracts now appear in the worker's attestation; missing task-impact for an inherited contract blocks.
- **Receipt rotation enforced mechanically**: `check_receipt_rotation()` — Git-history based: canonical contract content changed with a MINOR/MAJOR version bump must have a rotated receipt; PATCH clarifications are exempt. Wired into `validate_library` and CI. No more memory-driven discipline.
- **Duplicate rules removed from `play-nice-together`**: the accidental double of normative rules 7–8 removed (content preserved once, numbering correct).
- **Question status vocabulary normalized**: one canonical machine vocabulary (OPEN/WAITING/ANSWERED/DECLINED/EXPIRED/SUPERSEDED/CANCELLED). Legacy lowercase forms parse as documented migration aliases but are never emitted canonically; help-response validation updated.
- **README truthfulness**: repository is public; README now says so (was claiming private).

### Changed
- Receipts rotated for the v0.2.0 meaning-changes that had kept stale receipts (enforced by the new rule): `play-nice-together` timber-juniper-velvet → cedar-basalt-vellum; `orchestration` echo-quartz-hollow → maple-cedar-gatehouse; `human-and-machine-parity` lantern-latch-river → window-sail-ember; `discovery-and-negotiation` nectar-heather-prairie → clover-dovetail-maple.
- `ask-for-help` example normalized to canonical status vocabulary (PATCH-level; receipt unchanged per the patch exemption).
- Commitment artifacts are now **consumer-context scoped**: default location is `<consuming project>/.contracts/sessions/` (anchored to the adoption manifest), with `CONTRACTCTL_SESSION_DIR` for harness-pinned per-worktree/session dirs and the library-local directory only as an in-library fallback. Parallel projects, worktrees, and workers can no longer collide; artifacts record their `session_dir` for inspectability. Parent-bundle lookup searches the consuming context first.
- `commit`/`attest` accept `--tag` for explicit surface-trigger matching (parity with `resolve`).

## [0.2.0] — 2026-09-11

Ask-for-help philosophy + v0.1 hardening.

### Added
- `ask-for-help` contract (core layer): asking as a first-class interoperability capability — the KNOW/DISCOVER/ASK/ESCALATE/PRESERVE-UNKNOWN ladder, ask-don't-guess prohibitions, discover-before-asking order, participant routing (human/service/agent/system), question quality contract, recommend-without-pretending, questions as resumable state with lifecycle, answers-become-provenance, interruption budget, service-to-service questions, delegate-don't-duplicate, `WAITING_FOR_HELP` as a successful stop state, and questions-are-never-authorization.
- `schema/question.schema.json`: one generalized schema family — `play-nice/question-v1` (human-facing), `help-request-v1` / `help-response-v1` (agent-to-agent) — with lifecycle states, decision provenance fields, and structural secret exclusion.
- `contractctl validate-question`: validates question/help artifacts (required fields, status vocabulary, participant types, help-request needs capability, help-response needs result, recommendation must be a real choice, inconsistent blocking flags, inline-secret rejection).
- CI (`.github/workflows/ci.yml`): library validation, byte-identical lock determinism check, full test suite, secret/private-material scan.
- `LICENSE` (MIT) and recommended branch-protection documentation.
- Worker inheritance is now enforced by construction: a worker's resolved set is the UNION of the parent's applicable contracts and its own task-triggered ones, each acknowledged with task-impact — silently dropping a parent constraint is structurally impossible, and the parent bundle must exist as a recorded orchestrator/session commitment (invented hashes rejected).
- Session-safe commitment artifacts: keyed by role+task under `.contract-commitments/` (gitignored) — parallel lanes/worktrees never share one global singleton.
- Attestation now fails closed when the lockfile is drifted (cannot produce an attestation against stale hashes).
- Bundle identity now represents the RESOLVED contract set (not the whole library): different task scopes produce different bundle receipts/SHA-256s; same scope is byte-stable.
- Library semver (VERSION file) is now distinct from the adopted Git revision (commit SHA when the repo is initialized): `library_version()` vs `library_revision()`; adoption pins validate against the revision.
- `contractctl commit --impact-file` (previously accepted but ignored).
- `session-status --role/--task/--artifact` for keyed artifact lookup.
- HELP IMPACT block in the standard session prefix (potential uncertainty points, available helpers, human-owned decisions, service-owned questions, safe stop state).

### Changed
- `play-nice-together` 1.0.0 → 1.1.0: knows when to act/discover/ask/preserve-uncertainty; well-formed questions reduce friction at boundaries.
- `orchestration` 1.0.0 → 1.1.0: workers return `WORKER STATE: NEEDS_HELP` with a structured question; the foreman routes answers and reduces interruption noise.
- `human-and-machine-parity` 1.0.0 → 1.1.0: questions carry parity (human + machine representations).
- `discovery-and-negotiation` 1.0.0 → 1.1.0: asking is part of negotiation; prefer direct questions over silent semantic guesses.
- Example adoption manifests: `ask-for-help` added to `always`.

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