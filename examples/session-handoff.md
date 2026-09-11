# Standard Session Prefix + Final Handoff

The reusable session protocol for any project that has adopted the
play-nice contract library. Paste the PREFIX at the start of a substantial
session; require the HANDOFF at the end. Both are harness-neutral: any
agent, any human, any tooling.

---

## SESSION PREFIX

```text
PHASE 0 — CONTRACT GATE (complete order)

RESOLVE APPLICABLE CONTRACTS
        (contractctl resolve --manifest .contracts/adoption.yaml --task "<task>")
                ↓
READ CANONICAL SOURCES
        (each resolved contract, from the library — not from memory)
                ↓
VERIFY VERSION + HASH + RECEIPT
        (contractctl attest ... — receipts, hashes, versions must match)
                ↓
TASK-IMPACT ACKNOWLEDGEMENT
        (one concrete sentence per contract: how it changes this task)
                ↓
CHECK FOR CONFLICTS
                ↓
CONTRACT ATTESTATION
        (CONTRACT GATE: PASS | BLOCKED)
                ↓
OPERATIONAL COMMITMENT
        (contractctl commit ... — activate the operating state)
                ↓
CONTRACT COMMITMENT: ACTIVE
                ↓
MUTATING WORK MAY BEGIN

For substantial mutating work, BOTH must be true before implementation:
  CONTRACT GATE: PASS
  CONTRACT COMMITMENT: ACTIVE

Read-only discovery may occur before the commitment when required to
determine which contracts apply. Mutation may not.

If contracts materially conflict:
  CONTRACT GATE: BLOCKED
  CONTRACT COMMITMENT: INACTIVE
with the conflicting rules, applicable authority, possible interpretations,
and the safest reversible path. Never silently ignore one. An honest blocked
state is compliant behavior.

For tasks resolving visual-fidelity-and-composition, the task-impact must
additionally identify: design reference, live surface, intended composition
to preserve, known anti-patterns, verification method.

WORKER INHERITANCE: a foreman that accepted the contracts cannot dispatch a
worker outside them. Worker packets carry:
  INHERITED CONTRACT BUNDLE: <bundle hash>
  PARENT CONTRACT COMMITMENT: ACTIVE
The worker loads inherited contracts, resolves task-specific additions,
attests, and activates its own worker commitment before mutation. Workers
may strengthen constraints; they may NOT silently weaken or omit the
parent's applicable constraints.

RE-COMMITMENT: if the task's scope materially changes (new surfaces,
sensitive data, external providers, design/UI work, different repo or
authority), resolve again — do not rely on the original commitment.

PHASE 1 — CURRENT TRUTH

Inspect current state before planning mutations:
  - repository, branch, SHA, dirty state, worktrees, remotes
  - PRs where relevant
  - runtime, deployment, tests
  - existing handoff/state documents

Current evidence outranks historical reports. Unknown is a valid state.

PHASE 2 — WORK

Perform the bounded task under the accepted, committed contracts:
  - bounded objective, owned paths, explicit authority
  - inspect before changing; reversible approaches
  - verify with evidence grades; never inflate them
  - the commitment governs how EVERY side interacts: be truthful,
    accessible, interoperable, respectful of attention and external
    systems, inspectable, recoverable, explicit about uncertainty
  - if a contract proves ambiguous, impossible, or friction-causing:
    record the issue, don't silently work around it — the library learns
  - stop conditions: objective met / human decision needed /
    insufficient evidence / rising risk — stop states are success
```

---

## FINAL HANDOFF STANDARD

Substantial work ends with:

```text
CURRENT      — verified current state (repo, branch, SHA, runtime, deployment)
CHANGED      — what actually changed
VERIFIED     — evidence with grades + exact commands
CONTRACTS    — bundle, gate, commitment state, material application:
                CONTRACTS
                  bundle: <receipt> (<sha prefix>)
                  gate: PASS
                  commitment: ACTIVE
                  applied:
                    - <contract>: how it actually shaped the work
                  task-impact:
                    - ...
                  conflicts: none | ...
                  deviations: none | ...
              (do not merely list filenames; explain material application)
ACCESSIBILITY — relevant verification (for human-facing work)
INTEROPERABILITY — relevant verification (for interface work)
SECURITY / OWNERSHIP — relevant verification
UNKNOWN      — unresolved truth, preserved honestly
DEFERRED     — parked improvements, with reasons
NEXT         — the single most legitimate next action, or "nothing required"
```

Where relevant, also include: branch, SHA, remote state, worktrees,
runtime, model/provider used, exact tests, and the human gate that remains.

The handoff must be resumable by another human OR another bot, cold.
`NEXT: nothing required` is a successful outcome.
```

---

## Example attestation + commitment (filled)

```text
CONTRACT_ATTESTATION v1

bundle:
  revision: 51c912a
  receipt: cedar-lantern-47

loaded:
  truth-and-evidence@1.0.0
    receipt: wren-loam-sail
    sha256: <hash>
    status: ACCEPTED
  friendly-api-client@1.0.0
    receipt: harbor-prairie-fable
    sha256: <hash>
    status: ACCEPTED
  accessibility-floor@1.0.0
    receipt: ridge-meadow-kindle
    sha256: <hash>
    status: ACCEPTED

task-impact:
  - truth-and-evidence: unknown states remain unknown in status output
  - friendly-api-client: API writes use observe → mutate → verify
  - accessibility-floor: new form keeps 44px targets and visible focus

conflicts: none

CONTRACT GATE: PASS

CONTRACT OPERATIONAL COMMITMENT v1

I have loaded and verified the complete applicable contract set for this
task. I accept these contracts as operating constraints for this session
and will actively use their information when making decisions. I will
apply them to improve the interaction between every relevant side,
including humans, agents, tools, APIs, services, interfaces, automation,
data, repositories, and future maintainers. [...]

bundle: cedar-lantern-47
task: add-github-provider

CONTRACT COMMITMENT: ACTIVE
```