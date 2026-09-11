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
schema/            contract, adoption, attestation, capability, status schemas
contracts/         60 canonical contracts across 8 layers
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
contractctl session-status          # ACTIVE / STALE / INACTIVE
```

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

Per-contract semver: PATCH = clarification, MINOR = compatible new rule, MAJOR = incompatible change. `contracts.lock.json` pins id, version, path, SHA-256, receipt, and status; lock drift is detected deterministically. A library revision's resolved set derives a bundle receipt (e.g. `cedar-lantern-47`) — an identifier, never a credential or authorization.

## Tests

```bash
python3 -m pytest tests/ -q
```

Covers: duplicate IDs/receipts, missing/invalid receipts and versions, index drift, lockfile drift and hash verification, adoption schema validation, unknown-contract rejection, ALWAYS-selection, trigger selection, irrelevant omission, bundle-receipt change on contract change, stale pins, wrong receipt/hash failures, missing-mandatory-contract failure, conflict-state representation, offline validation, full attestation pass/fail paths — and the commitment machinery: ACTIVE after PASS, blocked without impact, exact bundle recording, stale-bundle invalidation, task-change re-resolution, worker inheritance (parent bundle required, floors preserved), and hash-mismatch prevention.

## Privacy

This library is private but sanitize-first: no credentials, private endpoints, personal topology, or private medical history. Sensory-safe/low-vision/attention requirements stand as engineering requirements with no personal context attached. The architecture is intended to survive eventual public release of the reusable contracts.

## License

MIT (see `LICENSE`), chosen so the reusable contracts can eventually be published and adopted freely.