# Changelog

All notable changes to the play-nice-contracts library. Per-contract semver: PATCH = clarification, MINOR = compatible new rule, MAJOR = incompatible behavior change. Meaningful contract changes (MINOR/MAJOR) rotate the hidden receipt — enforced mechanically by `contractctl validate` via Git history.

## [0.7.0] — 2026-09-13

### Added
- `assume-unknown` (core, 1.0.0): epistemic claim classification, separate authority/evidence/interpretation/decision, and consequence-scaled disconfirmation before dependent execution. Honest uncertainty and practical recovery are successful outcomes.
- Generalized, attributed Workshop v3 / V1-shell case study and adoption decision; no claim of independently verified runtime causality.

### Changed
- `play-nice-together` 1.5.0 -> 1.6.0, new founding rule; receipt rotated from gatehouse-meadow-juniper to compass-fern-harbor.
- All adoption examples include `assume-unknown` in `always`; registry, quick reference, session protocol, and lock updated. Consumers intentionally update their pins and re-attest; no schema or CLI semantics changed.
- CI emits the required `library` check name, matching the live branch protection context.
- Lock generation uses portable forward-slash paths and LF bytes on Windows and Linux.
- Regression coverage checks adoption, onboarding, omitted impacts, stale bundles, and public provenance boundaries.

## [0.6.0] — 2026-09-12

Be useful without being cruel. (Foundational principle; bounded pass. Internal project shorthand: the Butthole Clause — the canonical contract keeps a professional name.)

### Added
- `collaborative-good-faith` contract (core, 1.0.0): the system should never require someone to spend unnecessary time repairing damage from needless hostility, contempt, gatekeeping, or ego. CLEAR + HONEST + RESPECTFUL + USEFUL over hostile honesty or dishonest politeness. Criticize toward repair (WHAT I OBSERVED -> WHY IT MATTERS -> EVIDENCE -> WHAT I SUGGEST -> WHAT I CAN HELP WITH). Correct without humiliating. Failure is evidence, not moral judgment. Good-faith disagreement is a contribution (claim/evidence/tradeoff/decision — never status/identity); HEARD != AGREED != ADOPTED. No gotcha culture; no status games; no gatekeeping knowledge. Ideas travel with provenance (borrow, don't appropriate); credit is ordinary and proportional. Safe uncertainty is a prerequisite of truth ("I don't know" -> "Thanks — who or what is most likely to know?"). Good faith with firm boundaries: no endless tolerance of abuse; disengagement preserves technical state. Humans keep their own voice; no tone policing; humor welcome. Foreman integrates disagreement into decision summaries rather than forwarding conflict raw — the human never referees a model argument. Critique and credit scale with consequence. Explicitly NOT a politeness police: no sentiment scoring, tone classifiers, civility points, moderation machinery — deterministic checks only where objective (provenance/attribution fields).
- Play-nice founding rule 12: help make collaboration worth continuing.

### Changed
- `play-nice-together` 1.4.0 -> 1.5.0 (receipt rotated: dell-timber-clover -> gatehouse-meadow-juniper).
- `orchestration` 1.3.0 -> 1.4.0 (receipt rotated): foreman's rule 7 gains disagreement-integration duty.
- `ask-for-help` 1.2.0 -> 1.3.0 (receipt rotated): asking must feel safe; uncertainty is never ridiculed.
- `mutual-contribution` 1.0.0 -> 1.1.0 (receipt rotated): collaborative good faith named as the social prerequisite.
- `participation-and-contribution` 1.1.0 -> 1.2.0 (receipt rotated): fair-hearing + HEARD/AGREED/ADOPTED distinction.
- Adoption example manifests now include `collaborative-good-faith` in `always`.

### Tests
- 99 passing (5 new: contract existence + receipt, core-principle coverage including no-politeness-police guard, cross-contract integration, always-resolution, moderation-machinery absence).

## [0.5.0] — 2026-09-12

Contributions are agreed, not imposed. (Foundational companion to participation-and-contribution; bounded pass.)

### Added
- `mutual-contribution` contract (core, 1.0.0): the agreement loop — NEED -> OFFER A CONTRIBUTION -> PARTICIPANT EVALUATES -> ACCEPT / MODIFY / DECLINE / OFFER ALTERNATIVE -> AGREED CONTRIBUTION -> PERFORM -> VERIFY + INTEGRATE. Capability defines possibility, not obligation; assignment is never treated as automatically accepted. Mutual constraints from both sides shape the scope. Safety and usability are part of capability (technically possible + safe enough + usable enough + reliable enough + appropriately authorized). Human workload is negotiated ("I can tell you whether this feels right; I cannot review 3,000 lines of JSON" -> the system adapts: machine summarizes, human reviews three meaningful decisions). Services negotiate through their natural interfaces (no webhooks -> bounded conditional polling). No penalty for boundaries — DECLINE is not disobedience, MODIFY is not failure, "try harder" pressure is an anti-pattern. Partial participation and mid-work scope change when assumptions become false are compliant behavior. Agreements are observed state, never permanent castes. Authority remains separate: capability / participation / agreement / authorization / acceptance kept distinct. Mutual agreement never removes consequence-matched verification. Shared closed vocabulary (OFFERED / ACCEPTED / MODIFIED / DECLINED / NEEDS_CONTEXT / NEEDS_HELP / COMPLETED / PARTIAL). Explicitly lightweight: no negotiation server, marketplace, optimization engine, scheduler, or large schema family.
- Play-nice founding rule 11: good cooperation is negotiated at the boundary.

### Changed
- `participation-and-contribution` 1.0.0 -> 1.1.0 (receipt rotated): the selected contribution is OFFERED and agreed, not imposed — links its companion contract.
- `orchestration` 1.2.0 -> 1.3.0 (receipt rotated): rule 7 is now a negotiation loop (identify need -> offer -> receive counterproposal -> agree scope -> provide context -> verify -> integrate), richer than assignment.
- `ask-for-help` 1.1.0 -> 1.2.0 (receipt rotated): scope negotiation uses the same structured-question machinery; agreed contributions can WAIT_FOR_HELP until missing conditions resolve.
- `model-routing` 1.1.0 -> 1.2.0 (receipt rotated): participant-stated reliability conditions shape the task; context window / benchmark / price alone never justify assignment.
- `project-context-and-participant-packs` 1.1.0 -> 1.2.0 (receipt rotated): packs may carry contribution-fit guidance (good_fits / workable_with_support / poor_fits / preferred_task_shape).
- `human-reliability` 1.0.0 -> 1.1.0 (receipt rotated): the human's contribution is negotiated — machinery carries volume so the human carries judgment.
- `play-nice-together` 1.3.0 -> 1.4.0 (receipt rotated: amber-rill-orbit -> dell-timber-clover).
- Adoption example manifests now include `mutual-contribution` in `always`.

### Tests
- 94 passing (5 new: contract existence + receipt, core-principle coverage including authority separation and no-schema-explosion guard, cross-contract integration, always-resolution, negotiation-schema absence).

## [0.4.0] — 2026-09-12

Everyone gets to participate. (Foundational philosophy + durable operating rules; bounded pass.)

### Added
- `participation-and-contribution` contract (core, 1.0.0): right-sized participation — the ladder NEED -> CAPABILITY -> SMALLEST SUITABLE PARTICIPANT -> BOUNDED CONTRIBUTION -> VERIFICATION; no model castes (authority comes from role, evidence, contracts, ownership, verification — never size/price/prestige); contribution is not all-or-nothing (observation, idea, classification, lookup, draft, test, comparison, review, contradiction, question are all real contributions); consequence-matched capability; participant dignity (no tasks designed to fail; honest refusal states without penalty; partial contributions preserved and passed onward); capability-ladder pipelines; local-first as feature; expensive reasoning's kindest use is durable constraints others reuse; ideas are participation; provenance per contribution; credit without authority confusion; orchestrator shapes winnable tasks; no token burn for status; failure preserves useful discoveries. Explicitly NOT cheapness-as-ideology: right-sized, never cheapest-first.
- Play-nice founding rule 10: making room for each participant according to real capabilities is part of playing nicely.

### Changed
- `model-routing` 1.0.0 -> 1.1.0 (receipt rotated): routing question is "which available participant is sufficient for this bounded contribution?" — never prestige/benchmark; small/local selected by sufficiency, never excluded because a larger model exists.
- `orchestration` 1.1.0 -> 1.2.0 (receipt rotated): new rule 7 — the foreman actively shapes conditions for participants to succeed; no task designed to fail; refusal/partial contributions preserved, not punished.
- `ask-for-help` 1.0.0 -> 1.1.0 (receipt rotated): honest refusal always in-bounds (UNSUPPORTED / INSUFFICIENT_CONTEXT / LOW_CONFIDENCE / OUT_OF_SCOPE alongside NEEDS_HELP); participants may offer a smaller contribution they CAN make reliably.
- `capability-first` 1.0.0 -> 1.1.0 (receipt rotated): participants are providers of contributions too; the smallest suitable participant provides the capability — a bigger/dearer participant never becomes the definition of the capability.
- `project-context-and-participant-packs` 1.0.0 -> 1.1.0 (receipt rotated): rule 13 gains the observed-capability vocabulary (strengths / limitations / good_task_shapes / avoid_task_shapes) as versioned observation data that routes delegation but never becomes authority.
- `play-nice-together` 1.2.0 -> 1.3.0 (receipt rotated: glade-thicket-compass -> amber-rill-orbit).
- Adoption example manifests now include `participation-and-contribution` in `always`.

### Tests
- 89 passing (9 new: contract existence + receipt, core-principle coverage, resolution for orchestration tasks + always-resolution, model-routing/orchestration/ask-for-help/capability-first/packs integration, play-nice rule 10, no-schema-explosion check for capability shapes).

## [0.3.0] — 2026-09-12

Project Context + Participant Pack framework. (Structure, schemas, validation, templates, Figma example, documentation — bounded pass; no migrations, no API calls, no UI/server.)

### Added
- `project-context-and-participant-packs` contract (core, 1.0.0): the three-layer model (contracts → project context → participant packs); packs never silently become canonical truth; standard `.project/` directory; participant acceptance flow; bidirectional boundary documents; human/agent participants; discovery over hand-maintenance; session bootstrap; ask-for-help routing; canonicality vocabulary; provenance; no-lock-in; symbolic secrets only.
- Schemas: `project.schema.json` (play-nice/project-v1), `participant.schema.json` (participant-v1: authoritative_for + not_authoritative_for, help routing, symbolic authentication), `participant-capabilities.schema.json` (real capabilities + mandatory honest limitations), `references.schema.json` (canonicality statuses + provenance).
- `contractctl init-project` — minimal useful skeleton (no empty directory forest, idempotent); `contractctl project validate`; `contractctl participant validate/list`.
- Example under `examples/project-context/.project/`: generic project manifest, adoption manifest, design CURRENT pointer, and a complete Figma participant pack (capabilities, interaction guide, references with provenance, help routing) — no private design data.
- YAML-subset parser upgraded to full list-of-maps support (nested blocks inside list items), verified equivalent to PyYAML on all example files.

### Changed
- `play-nice-together` 1.1.0 → 1.2.0, receipt rotated (cedar-basalt-vellum → glade-thicket-compass): rule 9 — mutual courtesy encoded as architecture; friendly participants offer what makes cooperation easier, friendly projects remember it.

### Tests
- 80 passing (13 new: project/participant validation, invalid manifests rejected, secret-shape rejection, capability + canonicality vocabulary checks, participant ID uniqueness, optional-deletion survival, same-participant-different-projects, minimal init skeleton, machine files parse without Markdown, help routing present).

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