# Play-Nice Contracts

A shared constitution for how humans, bots, software, services, APIs, interfaces, designs, automation, repositories, and future tools interact with one another.

> **Everything should play nicely with everything else.**

A good system should be understandable by a human, operable by automation, inspectable by an agent, interoperable with other tools, accessible to people with different needs, recoverable after failure, and replaceable without destroying the truth it manages.

This library preserves the lessons that keep being relearned, so that neither Rylee nor anyone else has to remember and restate them every time.

## The layering

Contracts are layered; a lower layer may never violate a requirement above it:

```text
UNIVERSAL SAFETY / INTEROPERABILITY FLOOR      (contracts/core)
        ↓
HUMAN EXPERIENCE / ACCESSIBILITY FLOOR         (contracts/human)
        ↓
PROJECT CONTRACTS                              (adoption manifests)
        ↓
USER / ORGANIZATION PREFERENCES                 (profiles/)
        ↓
THEME / PERSONALITY / DECORATION
```

Rylee's preferred experience is a first-class profile (`profiles/`), not a hidden requirement for everyone else. Accessibility requirements are universal design requirements; private medical history is not (and does not appear in this library).

## What's here

```text
schema/            contract, adoption, attestation, capability, status, question schemas
contracts/         61 canonical contracts across 8 layers
profiles/          baseline + example personal profiles
tools/contractctl  the CLI (stdlib-only Python)
tests/             full library test suite
examples/          adoption manifests (Personal World, VEFR, homelab) + session prefix
CONTRACT_INDEX.md  the registry (routes, does not govern)
contracts.lock.json pinned id/version/sha256/receipt for every contract
```

Each contract is dual-use: PURPOSE, NORMATIVE RULES, RATIONALE, HUMAN EXAMPLES, MACHINE IMPLICATIONS, GOOD EXAMPLES, ANTI-PATTERNS, ACCEPTANCE CHECKS — readable by a person, consumable by an agent.

## Quick start

```bash
# inspect the library
python3 tools/contractctl/contractctl.py list
python3 tools/contractctl/contractctl.py show truth-and-evidence

# validate + lock
python3 tools/contractctl/contractctl.py validate
python3 tools/contractctl/contractctl.py lock

# as a project: adopt (consume, don't fork)
cp examples/personal-world.adoption.yaml  .contracts/adoption.yaml   # in your repo
# pin the revision to the commit you adopted
contractctl resolve --manifest .contracts/adoption.yaml --task "your task"
contractctl attest --manifest .contracts/adoption.yaml --task "your task" \
  --impact truth-and-evidence="unknown stays unknown in my status output" ...
contractctl commit --manifest .contracts/adoption.yaml --task "your task" \
  --impact ... # activates CONTRACT COMMITMENT: ACTIVE
contractctl session-status --manifest .contracts/adoption.yaml   # ACTIVE / STALE / INACTIVE
contractctl validate-question q.json  # play-nice question / help-request / help-response artifacts
```

Commitment artifacts are **consumer-context scoped** (project/worktree/session-safe by default): they live in `<your project>/.contracts/sessions/` next to your adoption manifest — parallel projects, worktrees, and workers never collide. Orchestration harnesses may pin a per-lane directory with `CONTRACTCTL_SESSION_DIR`; `--output` overrides explicitly. Artifacts are secret-free JSON, keyed by role+task, and record their own location.
```

## Asking for help is part of the architecture

`ask-for-help` (core) encodes: **it is nice, polite, kind, and smart to ask.** Know → act; can safely discover → discover; another participant can answer cheaply → ask; high-risk/ambiguous → ask or escalate; unknown and nobody can answer → preserve UNKNOWN. Never guess to keep moving. Questions are resumable state (`play-nice/question-v1`), answers become provenance, and answers are never authorization. `WAITING_FOR_HELP` is a successful stop state.

## The contract gate (session prefix)

Substantial work starts with the complete preflight:

```text
RESOLVE APPLICABLE CONTRACTS → READ CANONICAL SOURCES →
VERIFY VERSION + HASH + RECEIPT → TASK-IMPACT ACKNOWLEDGEMENT →
CHECK FOR CONFLICTS → CONTRACT ATTESTATION →
OPERATIONAL COMMITMENT → CONTRACT COMMITMENT: ACTIVE →
MUTATING WORK MAY BEGIN
```

The three stages mean: receipt = "I obtained the lesson"; attestation = "I know this lesson applies here"; commitment = "I will use this lesson while I work." For substantial mutating work, BOTH `CONTRACT GATE: PASS` and `CONTRACT COMMITMENT: ACTIVE` are required before implementation. The commitment is an operating state, not ceremony: tooling uses it as an execution gate, stale bundles invalidate it, scope changes force re-resolution, and workers inherit the parent's bundle (they may strengthen, never weaken, the applicable constraints). Full prefix: `examples/session-handoff.md`. Neither gate nor commitment is ever authorization — authority comes from the task and the Authorization contract.

## Versioning

Per-contract semver: PATCH = clarification, MINOR = compatible new rule, MAJOR = incompatible change. Library semver (VERSION) is distinct from the adopted Git revision: the version describes contract content, the revision pins the exact adopted commit. `contracts.lock.json` pins id, version, path, SHA-256, receipt, and status; lock drift is detected deterministically and attestations fail closed on it. A commitment's bundle identity represents the **resolved contract set** for its task — different scopes, different bundles — and stale bundles invalidate commitments. Bundle receipts (e.g. `cedar-lantern-47`) are identifiers, never credentials or authorization.

## Tests

```bash
python3 -m pytest tests/ -q
```

67 tests covering: duplicate IDs/receipts, missing/invalid receipts and versions, index drift, lockfile drift and hash verification, adoption schema validation, unknown-contract rejection, ALWAYS-selection, trigger selection, irrelevant omission, bundle-receipt change on contract change, stale pins (git revision), wrong receipt/hash failures, missing-mandatory-contract failure, conflict-state representation, offline validation, full attestation pass/fail paths — the commitment machinery (resolved-set bundles, version-vs-revision separation, worker inheritance with exact-union attestation enforcement, invented-parent rejection, consumer-context session isolation across projects/worktrees, lock-drift fail-closed, impact-file support) — receipt-rotation enforcement via Git history (meaningful change → version change → receipt change; PATCH exempt) — and ask-for-help + the question schema family (canonical status vocabulary, secret-bearing rejection, help-request capability requirement).

## Asking for help is part of the architecture

`ask-for-help` (core) encodes: **it is nice, polite, kind, and smart to ask.** Know → act; can safely discover → discover; another participant can answer cheaply → ask; high-risk/ambiguous → ask or escalate; unknown and nobody can answer → preserve UNKNOWN. Never guess to keep moving. Questions are resumable state (`play-nice/question-v1`), answers become provenance, and answers are never authorization. `WAITING_FOR_HELP` is a successful stop state.

## Privacy / repository state

This repository is **public**. It is published sanitize-first: no credentials, private endpoints, personal topology, or private medical history — enforced by a canary test that runs locally and in CI. Sensory-safe/low-vision/attention requirements stand as engineering requirements with no personal context attached; the profile under `profiles/examples/` is a presentation-preferences example, not a personal record. Keep the repo publishable by construction, not by later scrub.

## CI / branch protection

CI (`.github/workflows/ci.yml`) runs on every push and PR. The job is named **`library`** and runs: workflow-YAML self-validation, `contractctl validate`, byte-identical lock determinism, the full test suite, and the secret/private-material scan.

`main` branch protection is **configured** (verified live):

- require pull request before merging; ≥1 approving review; stale reviews dismissed
- require status check **`library`** (the actual job name) and branches up to date
- force pushes disallowed; deletions disallowed

Contract text changes: lockfile regeneration ships in the same commit (`contractctl lock`) — CI's determinism check fails otherwise. Meaningful contract changes (MINOR/MAJOR) must rotate the hidden receipt — `contractctl validate` enforces this from Git history.

## License

MIT (see `LICENSE`). GitHub recognizes the license.
