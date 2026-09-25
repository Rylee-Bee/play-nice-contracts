# Play-Nice Contracts

A shared constitution for how humans, bots, software, services, APIs, interfaces, designs, automation, repositories, and future tools interact with one another.

> **Everything should play nicely with everything else.**

A good system should be understandable by a human, operable by automation, inspectable by an agent, interoperable with other tools, accessible to people with different needs, recoverable after failure, and replaceable without destroying the truth it manages.

This library preserves the lessons that keep being relearned, so that neither Rylee nor anyone else has to remember and restate them every time.

## New here?

Start with **[Trusted Translation](docs/principles/trusted-translation.md)** for the five-minute mental model, then use the [contract index](CONTRACT_INDEX.md) or `contractctl onboard --role <your-role>` for the rules that apply to your work. A [quick reference](docs/QUICK_REFERENCE.md) is available as a reminder after you have read the contracts.

## The layering

The `contracts/` tree groups the library into 8 topic areas; normative
**authority** is the five-layer stack below. A lower layer may never
violate a requirement above it:

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
schema/                     JSON Schemas: contract, adoption, attestation,
                            capability, status, question, project, participant,
                            references, global Play-Nice config
contracts/                  66 canonical contracts in 8 topic areas (normative)
.contracts/adoption.yaml    this repo's own adoption of its library — the
                            contract gate is dogfooded here (see AGENTS.md)
docs/                       QUICK_REFERENCE.md (non-normative reminder card),
                            principles/ (non-normative philosophy),
                            PLAYNICE.md (orchestrator reference), roles/,
                            research/, decisions/, participant-notes/
profiles/                   baseline + example personal profiles
tools/contractctl           the CLI (stdlib-only Python): validate, lock,
                            resolve, attest, commit, adopt, freshness, sync,
                            onboard, init-project, and more
tools/playnice              the `playnice work|status|reconcile` orchestrator
tests/                      hermetic suite: library invariants + tooling
examples/                   real adoption manifests, worked .project/ example,
                            session prefix
harness/                    EXPERIMENTAL research: candidate harness laws
                            are hypotheses with evidence — NOT contracts
CONTRACT_INDEX.md           the registry (routes, does not govern)
contracts.lock.json         generated: pinned id/version/sha256/receipt per contract
VERSION + CHANGELOG.md      library semver — distinct from adopted git revisions
SECURITY.md / TRADEMARKS.md threat model; name and fork-identity rules
CONTRIBUTING.md            the door: branch + gate + PR + Rylee review
```

## Design philosophy

Non-normative mental model behind the contracts. **Inspirational, not authoritative** — where a metaphor conflicts with a contract, the contract wins.

- [`docs/principles/trusted-translation.md`](docs/principles/trusted-translation.md) — *Different languages. Different systems. Shared understanding. Earned trust.* Why Play-Nice favors understanding across boundaries rather than forced uniformity.
- [`docs/principles/world-with-manners.md`](docs/principles/world-with-manners.md) — *The world knows how loudly to exist.* The Project Worlds Workshop v3 story: sixteen viable explorations, convergence without flattening, respectful attention, real provenance and a deliberate handoff and STOP.
- [`docs/roles/trusted-steward.md`](docs/roles/trusted-steward.md) — *A Trusted Steward carries continuity without claiming ownership.* The executive-assistant / thought-offloading role, composed entirely from existing contracts (Hermod/VEFR is one implementation).
- [`docs/PLAY-NICE-OPUS.md`](docs/PLAY-NICE-OPUS.md) — *The long-form why.* Non-normative philosophy, the Small Model Olympics case study, and the closing promises; a one-page [TLDR](docs/PLAY-NICE-OPUS-TLDR.md). Inspirational, not authoritative.

- [`docs/participant-notes/`](docs/participant-notes/) — *Letters back from participants who worked under Play-Nice.* Non-normative experience reports from agents and operators who used these contracts. New entries are welcome; no special mechanism required.

Each contract is dual-use: PURPOSE, NORMATIVE RULES, RATIONALE, HUMAN EXAMPLES, MACHINE IMPLICATIONS, GOOD EXAMPLES, ANTI-PATTERNS, ACCEPTANCE CHECKS — readable by a person, consumable by an agent.

## Quick start

`contractctl` is **a file, not an installed command**: every invocation
below means `./tools/contractctl/contractctl` (the executable shim) or
`python3 tools/contractctl/contractctl.py` from a library checkout
(consumers: `python3 "$PLAY_NICE_LIBRARY/tools/contractctl/contractctl.py"`,
or `alias` it once). Stdlib-only by design; there is no installer.
`playnice` works the same way: `./tools/playnice/playnice`.

```bash
# orient yourself
contractctl onboard --role orchestrator          # guided onboarding for your role
contractctl onboard --role worker --json         # machine-readable onboarding plan

# inspect the library
python3 tools/contractctl/contractctl.py list
python3 tools/contractctl/contractctl.py show truth-and-evidence

# validate + lock
python3 tools/contractctl/contractctl.py validate
python3 tools/contractctl/contractctl.py lock

# as a project: adopt (consume, don't fork)
contractctl init-adoption --project my-app   # writes .contracts/adoption.yaml, pinned
contractctl upgrade-check --manifest .contracts/adoption.yaml  # current? what changed? what next?
contractctl scan                              # the same public-boundary check, in your tree
contractctl resolve --manifest .contracts/adoption.yaml --task "your task"
contractctl attest --manifest .contracts/adoption.yaml --task "your task" \
  --impact truth-and-evidence="unknown stays unknown in my status output" ...
contractctl commit --manifest .contracts/adoption.yaml --task "your task" \
  --impact ... # activates CONTRACT COMMITMENT: ACTIVE
contractctl session-status --manifest .contracts/adoption.yaml   # ACTIVE / STALE / INACTIVE
contractctl validate-question q.json  # play-nice question / help-request / help-response artifacts
```

Commitment artifacts are **consumer-context scoped** (project/worktree/session-safe by default): they live in `<your project>/.contracts/sessions/` next to your adoption manifest — parallel projects, worktrees, and workers never collide. Orchestration harnesses may pin a per-lane directory with `CONTRACTCTL_SESSION_DIR`; `--output` overrides explicitly. Artifacts are secret-free JSON, keyed by role+task, and record their own location.

## Project context + participant packs

`.project/` is the standard durable-context structure any project can adopt
(`contractctl init-project .` creates a minimal skeleton): a project.yaml
manifest, canonical pointers (CURRENT/DECISIONS), the Play-Nice adoption
manifest, and optional **participant packs** — one directory per regular
collaborator (Figma, GitHub, an agent, a team) describing capabilities,
interaction guides, references, what the participant is authoritative for
and NOT authoritative for, and which questions it can answer directly
(ask-for-help routing). Packs are optional enrichment: deleting one never
corrupts canonical project truth. See the
`project-context-and-participant-packs` contract and the worked example under
`examples/project-context/`.

## Asking for help is part of the architecture

`ask-for-help` (core) encodes: **it is nice, polite, kind, and smart to ask.** Know → act; can safely discover → discover; another participant can answer cheaply → ask; high-risk/ambiguous → ask or escalate; unknown and nobody can answer → preserve UNKNOWN. Never guess to keep moving. Questions are resumable state (`play-nice/question-v1`), answers become provenance, and answers are never authorization. `WAITING_FOR_HELP` is a successful stop state.

## Assume UNKNOWN before assuming understood

[Assume UNKNOWN](contracts/core/ASSUME_UNKNOWN.md) requires a cheap, relevant
disconfirmation check before consequential execution. Separate authority, evidence,
interpretation, and decision; preserve UNKNOWN when understanding is insufficient.
See the [reported Workshop case](docs/research/workshop-v3-v1-shell.md) and
[adoption decision](docs/decisions/2026-09-13-assume-unknown.md). Existing consumers
add `assume-unknown` to `always`, pin the reviewed revision, resolve and re-attest;
updating the library alone does not force new core contracts into old manifests.

## The contract gate (session prefix)

Substantial work starts with the complete preflight:

```text
REMOTE FRESHNESS (require-current only)
        (contractctl freshness — verify the authoritative remote revision)
                ↓
RESOLVE APPLICABLE CONTRACTS → READ CANONICAL SOURCES →
VERIFY VERSION + HASH + RECEIPT → TASK-IMPACT ACKNOWLEDGEMENT →
CHECK FOR CONFLICTS → CONTRACT ATTESTATION →
OPERATIONAL COMMITMENT → CONTRACT COMMITMENT: ACTIVE →
MUTATING WORK MAY BEGIN
```

The three stages mean: receipt = "I obtained the lesson"; attestation = "I know this lesson applies here"; commitment = "I will use this lesson while I work." For substantial mutating work, BOTH `CONTRACT GATE: PASS` and `CONTRACT COMMITMENT: ACTIVE` are required before implementation. The commitment is an operating state, not ceremony: tooling uses it as an execution gate, stale bundles invalidate it, scope changes force re-resolution, and workers inherit the parent's bundle (they may strengthen, never weaken, the applicable constraints). Full prefix: `examples/session-handoff.md`. Neither gate nor commitment is ever authorization — authority comes from the task and the Authorization contract.

## Remote freshness (require-current)

A project can opt into **current contracts** in its adoption manifest:

```yaml
schema: play-nice/adoption-v1
source:
  repository: Rylee-Bee/play-nice-contracts
  revision: <reviewed SHA>
freshness:
  policy: require-current   # pinned (legacy default) | require-current
  ref: main                 # authoritative branch
  update: review            # review (block, ask for review) | automatic (refresh pin, still re-commit)
```

Under `require-current`, `contractctl` deterministically checks the authoritative remote (`git ls-remote`) BEFORE the resolve/read/attest stages:

```text
REMOTE FRESHNESS → RESOLVE → READ → VERIFY → ATTEST → COMMIT → MUTATE
```

- a local checkout, the adoption pin, a previous session, or "I checked GitHub" is **not** proof of remote freshness — the remote is actually queried;
- `UNKNOWN`/`UNREACHABLE` → `CONTRACT COMMITMENT: INACTIVE` (fail closed); `BEHIND`/`DIVERGED` → `STALE`, requiring fetch/update → resolve → read → attest → commit again;
- a changed authoritative revision invalidates existing commitments (re-resolve, re-attest, re-commit);
- `contractctl sync` refreshes the pin per the update policy — **checking for the newest revision is not the same as silently adopting it**; `update: review` blocks mutation pending explicit review, and even `automatic` still forces a fresh resolve/read/attest/commit cycle;
- **equivalence rule** (`update: automatic` only): when both the adopted pin and the local checkout are provable ancestors of the remote and `contracts/` + `schema/` are byte-identical across all three, freshness reads CURRENT despite post-merge docs/tooling commits ahead of the pin. Any difference in the normative surfaces, or unverifiable history, stays BEHIND — fail closed. This ends the post-merge pin treadmill without weakening review; commitment artifacts record `freshness.equivalence` so equivalence-CURRENT is distinguishable from exact-match CURRENT. `contractctl diff --from <pin> --to <rev>` answers "what actually changed between my pin and current?" including receipt rotations and always-set impact.

## The playnice orchestrator (`playnice work`)

`playnice` is the global agent-work entry point: take a task, fetch/refresh remote Play Nice contracts, reconcile carryover, pass the contract gate, issue a work permit, launch the agent, then verify and write a durable handoff — one command, no prompts required:

```bash
python3 tools/playnice/playnice.py work --repo ~/code/your-repo "implement the feature"
playnice status --repo ~/code/your-repo       # what state is this repo in?
playnice reconcile --repo ~/code/your-repo    # clean up merged work, refresh pins
```

- **Fail closed on UNKNOWN.** No adoption manifest, no freshness evidence, no permit → no work, no mutation. Freshness and carryover use the exact vocabularies `CURRENT/BEHIND/DIVERGED/UNREACHABLE/UNKNOWN` and `DONE/MERGED/CLOSED/STILL_ACTIVE/DEFERRED/WAITING_FOR_HELP/UNKNOWN/BLOCKED`.
- **Two-layer commitment.** The orchestrator computes a deterministic task-impact permit floor; the executing agent does its own worker attestation via `contractctl` and inherits the parent's constraints (worker packet: `INHERITED_CONTRACT_BUNDLE`, `PLAY_NICE_SOURCE_REVISION`, `PARENT_CONTRACT_COMMITMENT`).
- **Automation is explicit opt-in.** Automation runs only with both a global config grant (`~/.config/play-nice/global.yaml`, or `PLAY_NICE_CONFIG`/`--config`) and an ACTIVE permit; `reconcile` revalidates liveness with `contractctl session-status` before any mutation.
- **Deterministic, no live network.** Tests run against local bare remotes and a fake `gh` (`PLAY_NICE_GH`); nothing in the pipeline requires the network.
- Exit codes: `0` ok · `1` usage/internal · `2` fail-closed · `3` agent failed · `4` needs help (human attention, safely deferred).

Full reference: [`docs/PLAYNICE.md`](docs/PLAYNICE.md) · config schema: [`schema/global-playnice.schema.json`](schema/global-playnice.schema.json) · examples: [`examples/global-playnice.yaml`](examples/global-playnice.yaml).

## Versioning

Per-contract semver: PATCH = clarification, MINOR = compatible new rule, MAJOR = incompatible change. Library semver (VERSION) is distinct from the adopted Git revision: the version describes contract content, the revision pins the exact adopted commit. `contracts.lock.json` pins id, version, path, SHA-256, receipt, and status; lock drift is detected deterministically and attestations fail closed on it. A commitment's bundle identity represents the **resolved contract set** for its task — different scopes, different bundles — and stale bundles invalidate commitments. Bundle receipts (e.g. `cedar-lantern-47`) are identifiers, never credentials or authorization.

## Tests

```bash
python3 -m pytest tests/ -q    # what CI runs, after pip install pytest pyyaml
```

One-command local equivalent without polluting the system Python:

```bash
uv run --python 3.12 --with pytest,pyyaml python3 -m pytest tests/ -q
```

The full suite covers: library invariants, resolution, attestation/commitment machinery, receipt-rotation enforcement, ask-for-help + question schema, the project-context/participant-pack framework, participation-and-contribution (right-sized participation, honest refusal), mutual-contribution (the agreement loop, authority separation), and collaborative-good-faith (critique toward repair, safe uncertainty, foreman disagreement integration, no moderation machinery).

## Privacy / repository state

This repository is **public**. It is published sanitize-first: no credentials, private endpoints, personal topology, or private medical history — enforced by a canary test that runs locally and in CI. Sensory-safe/low-vision/attention requirements stand as engineering requirements with no personal context attached; the profile under `profiles/examples/` is a presentation-preferences example, not a personal record. Keep the repo publishable by construction, not by later scrub.

## CI / branch protection

CI (`.github/workflows/ci.yml`) runs on every push and PR. The job is named **`library`** and runs: workflow-YAML self-validation, `contractctl validate`, byte-identical lock determinism, the full test suite, and the secret/private-material scan.

`main` branch protection is **configured** (verified live):

- require pull request before merging; ≥1 approving review; stale reviews dismissed
- require status check **`library`** (the actual job name) and branches up to date
- force pushes disallowed; deletions disallowed

Admin reality: the owner's token bypasses protection (GitHub also
forbids self-approval on a single-maintainer repo), so one approved
agent-side admin *merge* is the sanctioned close when the owner has
explicitly approved merging in-task — as happened for PR #17. Bypass
is never used silently, and never for a direct push.

Contract text changes: lockfile regeneration ships in the same commit (`contractctl lock`) — CI's determinism check fails otherwise. Meaningful contract changes (MINOR/MAJOR) must rotate the hidden receipt — `contractctl validate` enforces this from Git history.

## License

- **Contract text** (`contracts/`) and **documentation** (`docs/`):
  **CC BY-SA 4.0** — copy, quote, and adapt freely; attribution is a
  legal term of the license, and derivatives of the text itself stay
  shareable. Your own projects and code are unaffected. See
  `contracts/LICENSE.md` and `docs/LICENSE.md`.
- **Tooling, schemas, lockfile, tests**: **MIT** (see `LICENSE`).
- **The name**: `TRADEMARKS.md` governs identity and fork naming; the
  optional 🐝 acknowledgement is credit, never endorsement.

This map supersedes a brief same-window "MIT everywhere" experiment and
simplifies that baseline's MPL tooling layer to MIT; `CHANGELOG.md`
records the full sequence, including where this README had it wrong.
Character and world content from Project Worlds lives in other
repositories under their own terms — nothing here licenses it, and it
must never be moved into this repository.
