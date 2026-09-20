# Standard Session Prefix + Final Handoff

The reusable session protocol for any project that has adopted the
play-nice contract library. Paste the PREFIX at the start of a substantial
session; require the HANDOFF at the end. Both are harness-neutral: any
agent, any human, any tooling.

---

## SESSION PREFIX

```text
PHASE 0 — CONTRACT GATE (complete order)

VERIFY AUTHORITATIVE REMOTE REVISION   (when freshness.policy: require-current)
        (contractctl freshness --manifest .contracts/adoption.yaml
         — deterministic git ls-remote; UNKNOWN/UNREACHABLE/BEHIND/DIVERGED
           block mutation, fail closed)
                ↓
REMOTE FRESHNESS: CURRENT
                ↓
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

For tasks resolving ask-for-help, the task-impact should identify (HELP IMPACT):

```text
HELP IMPACT

potential uncertainty:
  <what might be missing/ambiguous that matters to this task>

available helpers:
  <service/API docs, capability endpoints, specialist agents, config>

human-owned decisions:
  <decisions only the owner can make, if any are expected>

service-owned questions:
  <facts another system naturally owns (API version, limits, semantics)>

safe stop:
  <e.g. preserve current state and return WAITING_FOR_HELP
   rather than guess or retry a mutation>
```

When blocked mid-work, return NEEDS_HELP / WAITING_FOR_HELP with a
well-formed question (checked-where, options, recommendation, blocking,
if-unanswered) — asking is GOOD, SAFE, POLITE, SMART, and COMPLIANT,
not failure. Never guess to keep moving.

WORKER INHERITANCE: a foreman that accepted the contracts cannot dispatch a
worker outside them. Worker packets carry:
  INHERITED CONTRACT BUNDLE: <bundle hash>
  PLAY_NICE_SOURCE_REVISION: <source revision the parent resolved against>
  PARENT CONTRACT COMMITMENT: ACTIVE
The worker loads inherited contracts, resolves task-specific additions,
attests, and activates its own worker commitment before mutation. Workers
may strengthen constraints (including freshness requirements); they may NOT
silently weaken or omit the parent's applicable constraints or resolve a
weaker/older source revision than the parent's.

RE-COMMITMENT: if the task's scope materially changes (new surfaces,
sensitive data, external providers, design/UI work, different repo or
authority), or the authoritative Play Nice revision changes
(freshness.policy: require-current: `contractctl freshness` re-verifies;
BEHIND/DIVERGED → `contractctl sync` per update policy), resolve again —
do not rely on the original commitment. Checking for the newest revision is
not the same as silently adopting it: update: review requires explicit
review before re-commitment.

PHASE 1 — CURRENT TRUTH

Inspect current state before planning mutations:
  - repository, branch, SHA, dirty state, worktrees, remotes
  - PRs where relevant
  - runtime, deployment, tests
  - existing handoff/state documents

Current evidence outranks historical reports. Unknown is a valid state.

PHASE 1B — DISCONFIRM BEFORE DEPENDENT EXECUTION

For assume-unknown, record in task-impact or a linked decision:
  AUTHORITY / EVIDENCE / INTERPRETATION / DECISION
  claims: OBSERVED / INFERRED / ASSUMED / UNKNOWN
  highest-impact unproven belief
  what observation would make the interpretation wrong
  cheapest reasonable check performed, result, and limits
  reservations, resulting action, and recovery path
An unavailable or inconclusive check preserves UNKNOWN and stops or narrows the
dependent action; independent authorized work may continue. Gate PASS and ACTIVE
record process, not comprehension. Revisit when contradictory evidence appears.

PHASE 2 — WORK

Perform the bounded task under the accepted, committed contracts:
  - bounded objective, owned paths, explicit authority
  - inspect before changing; reversible approaches
  - verify with evidence grades; never inflate them
  - the commitment governs how EVERY side interacts: be truthful,
    accessible, interoperable, respectful of attention and external
    systems, inspectable, recoverable, explicit about uncertainty
  - know when to act, when to discover, when to ask, and when to
    preserve UNKNOWN: check discoverable places first, then ask the
    participant who naturally owns the answer; record the question as
    resumable state; answers become provenance, never authorization
  - if a contract proves ambiguous, impossible, or friction-causing:
    record the issue, don't silently work around it — the library learns
  - stop conditions: objective met / human decision needed / insufficient
    evidence / rising risk / WAITING_FOR_HELP — stop states are success
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

---

## Example handoffs

### Orchestrator → Worker (bounded task assignment)

```text
WORKER PACKET

base: 659fb87
branch: feat/t14-status-chip
owned: [frontend/src/primitives/StatusChip.tsx, tests/StatusChip.test.tsx]
objective: "StatusChip renders canonical statuses; word + luminance tint; no color-only meaning"
acceptance: ["vitest run tests/StatusChip.test.tsx → green", "axe: 0 serious"]
contracts: [accessibility-floor, explicit-state]
exclusions: ["design/tokens.json", "shared shell"]
authority: {push: branch, merge: false, deploy: false}
budget: {model: fast-14b, max_tokens: 24000}
INHERITED CONTRACT BUNDLE: dovetail-orchard-compass
PARENT CONTRACT COMMITMENT: ACTIVE
```

### Worker → Orchestrator (task complete)

```text
CURRENT: feat/t14-status-chip @a1b2c3d, clean, pushed
CHANGED: StatusChip.tsx + StatusChip.test.tsx
VERIFIED: vitest run tests/StatusChip.test.tsx → 4 passed (CI TESTED)
          axe: 0 serious, 0 moderate (BROWSER VERIFIED)
CONTRACTS: accessibility-floor PASS; explicit-state PASS
UNKNOWN: runtime behavior with real-world status data (not tested)
DEFERRED: animation variants (issue #31, low value)
NEXT: integration merge; combined suite at integration SHA
```

### Participant → Human (asking for help)

```text
QUESTION: Two approved visual references disagree about navigation placement.
  The newer desktop reference uses the left rail.
  Recommendation: left rail (matches the newer approved frame).
  Blocking: yes (won't change Settings until resolved).
  [Use left rail — recommended]  [Use top navigation]
```

### Session → Next session (cold resumption)

```text
CURRENT: main @07b5dd3, clean; Project Worlds API on :18080 (healthy)
CHANGED: participant profiles published (hermes.md, qwen-local-bazzite.md)
         contractctl onboard command added (7 tests)
         docs/QUICK_REFERENCE.md created
VERIFIED: 106 tests passed; contractctl validate VALID; CI green
CONTRACTS: all 65 read; no modifications; no lockfile changes
UNKNOWN: runtime behavior of agent-sync sensor (API not tested this session)
         Big Pickle capabilities (profile exists but no observed tasks)
DEFERRED: machine-readable changelog (generation feasibility TBD)
          cross-reference map (needs deterministic link extraction)
NEXT: nothing required (or: run agent-sync sensor verification if API is up)
```