# Maintaining the Play-Nice library

> **Status:** Current · for people changing this library, not for people using it.
> Using Play-Nice in your project? Start at [the floor](../contracts/everyone/FLOOR.md).

The legacy `contractctl` attest/commit gate below still works for projects
that pinned it; v2 replaces it with the one-line proof in
[contract-proof](../contracts/work/CONTRACT_PROOF.md).

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
