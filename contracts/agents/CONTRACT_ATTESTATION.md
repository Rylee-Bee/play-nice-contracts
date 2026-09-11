---
contract_id: contract-attestation
title: Contract Attestation
version: 1.1.0
status: canonical
layer: agents
applies: [agents, contracts, workflows]
triggers: [always-before-mutating-work, contract-gate]
rationale: Reading a contract is not applying it, and knowing one applies is not using it. The full gate proves retrieval (receipt), application (task-impact), and finally operating intent (commitment) — three checkable stages before mutating work begins.
---

<!-- contract-receipt: kindle-cedar-beacon -->

# Contract Attestation

## Purpose

Force contracts to be applied, not merely retrieved. Before mutating work: resolve the applicable set, read each from canonical source, verify receipts/hashes, and acknowledge each contract's impact on this task.

## NORMATIVE RULES

### The full gate order

1. Substantial mutating work follows the complete preflight:
   ```text
   RESOLVE APPLICABLE CONTRACTS
             ↓
   READ CANONICAL SOURCES
             ↓
   VERIFY VERSION + HASH + RECEIPT
             ↓
   TASK-IMPACT ACKNOWLEDGEMENT
             ↓
   CHECK FOR CONFLICTS
             ↓
   CONTRACT ATTESTATION
             ↓
   OPERATIONAL COMMITMENT
             ↓
   CONTRACT COMMITMENT: ACTIVE
             ↓
   MUTATING WORK MAY BEGIN
   ```
2. For substantial mutating work, nothing begins before BOTH are true:
   `CONTRACT GATE: PASS` and `CONTRACT COMMITMENT: ACTIVE`. Read-only discovery may occur before the commitment when required to determine which contracts apply; mutation may not.
3. The three stages mean distinct things: the receipt says "I obtained the lesson"; the attestation says "I know this lesson applies here"; the commitment says "I will use this lesson while I work."

### Receipts, bundles, attestation

4. Every canonical contract contains a hidden receipt:
   ```html
   <!-- contract-receipt: <unique-three-word-phrase> -->
   ```
   The receipt: is unique; is indexed; changes for meaningful contract changes; is not a credential, not authorization, not security. It proves only that the exact file was accessible/read.
5. Resolved bundles get a derived receipt (from selected versions/hashes), e.g. `CONTRACT-BUNDLE: cedar-lantern-47`. A handoff may know the expected bundle phrase; the phrase alone never establishes acceptance.
6. Attestation requires all three: (a) correct receipt (the exact file was read); (b) correct version/hash (the exact text was read); (c) task-impact acknowledgement (one concrete sentence per contract about how it changes this task).
7. Attestations follow the standard format:
   ```text
   CONTRACT_ATTESTATION v1

   bundle:
     revision: <repo revision>
     receipt: <bundle receipt>

   loaded:
     <contract_id>@<version>
       receipt: <hidden receipt>
       sha256: <content hash>
       status: ACCEPTED | CONFLICT

   task-impact:
     - one concrete sentence per contract

   conflicts: none

   CONTRACT GATE: PASS | BLOCKED
   ```
8. If contracts conflict materially: `CONTRACT GATE: BLOCKED` with an explanation of the conflicting rules, the applicable authority, possible interpretations, and the safest reversible path. Never silently ignore one.

### The operational commitment

9. After a PASS gate, the participant (human, agent, or automation about to mutate) activates the operational commitment — the explicit statement: I will actually use these contracts to govern how I perform this work and how every involved side interacts. Canonical form (meaning preserved; wording may be normalized):
   ```text
   CONTRACT OPERATIONAL COMMITMENT v1

   I have loaded and verified the complete applicable contract set for this task.

   I accept these contracts as operating constraints for this session and will
   actively use their information when making decisions.

   I will apply them to improve the interaction between every relevant side,
   including humans, agents, tools, APIs, services, interfaces, automation,
   data, repositories, and future maintainers.

   I will prefer behavior that is: truthful; accessible; understandable;
   interoperable; respectful of finite human attention; respectful of external
   systems; inspectable; recoverable; reversible where practical; explicit
   about uncertainty; provider/tool neutral where appropriate; friendly to both
   human and machine consumers.

   I will not treat these contracts as passive documentation.
   I will not silently weaken, bypass, contradict, or ignore an applicable
   contract for convenience.

   When implementation choices create tension between participants, I will use
   the applicable contracts to seek an outcome that improves the interaction
   between them rather than optimizing one side at the unnecessary expense of
   another.

   If contracts genuinely conflict, required evidence is unavailable, or the
   safe interpretation is unclear, I will preserve that state honestly and
   surface the conflict rather than inventing certainty.

   I understand that "play nice together" means designing the boundary between
   systems as carefully as the systems themselves.

   bundle: <resolved bundle receipt>
   task: <task id or description>

   CONTRACT COMMITMENT: ACTIVE
   ```
10. The commitment is not ceremonial and not "legal acceptance". It is an operating state: tooling uses it as an execution gate where practical, and behavior under it must match it. The tooling does not pretend to prove internal comprehension — it proves the required process occurred and records an explicit operating state.
11. Commitment mechanics (enforced by tooling):
    - commitment only succeeds after valid contract resolution and a PASS gate;
    - invalid or missing contract hashes prevent the ACTIVE state;
    - unresolved material conflicts prevent the ACTIVE state;
    - the commitment records the exact resolved bundle (receipt and SHA-256 of the bundle material) and the task;
    - a stale bundle (library changed) invalidates the commitment;
    - changing the task so that additional contracts trigger requires re-resolution and re-commitment;
    - changing applicable contract versions requires re-attestation and re-commitment.
12. The commitment is stored as a session artifact (local state), containing no secrets:
    ```json
    {"contract_gate": "PASS", "commitment": "ACTIVE",
     "bundle_sha256": "...", "task": "...",
     "contracts": ["<id>@<version>", ...]}
    ```

### Worker inheritance (propagation tree)

13. A foreman/orchestrator that accepted the contracts cannot dispatch a worker outside them. The propagation tree:
    ```text
    OWNER INTENT
        ↓
    ORCHESTRATOR CONTRACT SET
        ↓
    ORCHESTRATOR COMMITMENT
        ↓
    BOUNDED WORKER CONTRACT SET
        ↓
    WORKER COMMITMENT
        ↓
    TOOLS / APIs / SERVICES
    ```
14. Worker task packets include: `INHERITED CONTRACT BUNDLE: <bundle hash>` and `PARENT CONTRACT COMMITMENT: ACTIVE`. The worker: loads the inherited applicable contracts; resolves additional contracts triggered by its narrower work; attests; activates its own commitment before mutation.
15. A worker may discover additional applicable contracts and may strengthen constraints. A worker may NOT silently weaken or omit the parent's applicable constraints.
16. The reverse path remains inspectable through provenance: service response → tool action → worker result → orchestrator verification → human-readable result. Contracts govern both directions.

### Conflict behavior under commitment

17. If an agent cannot satisfy two applicable contracts simultaneously: do not fake compliance. Return `CONTRACT GATE: BLOCKED` / `CONTRACT COMMITMENT: INACTIVE`, and report the conflicting contracts, the exact requirements in tension, why both cannot currently be satisfied, the safest reversible options, and whether owner input is needed. An honest blocked state is compliant behavior.

### Re-commitment

18. A new resolution/commitment is required when work materially changes scope — e.g., a documentation task expands into a production API integration change; a project or repository change; mutating authority change; external provider change; design/UI work becomes involved; sensitive data becomes involved. Do not rely on the original commitment.
19. If implementation reveals a contract is ambiguous, impossible to apply, causes unnecessary friction, creates conflict, or misses an important case: do NOT silently work around it. Record the issue — the library is allowed to learn from failures.
20. A PASS gate permits work to begin; it is not authorization for any particular mutation — authority comes from the task and the Authorization contract.

## RATIONALE

Agents would summarize contracts from memory, read the index and skip the files, or acknowledge everything without applying anything. The receipt proves the file was read; the hash proves which text; the task-impact sentence forces one moment of actual application. The final commitment stage exists because retrieval-and-knowledge still permitted "read, agreed, then worked as before": an explicit operating state, recorded and machine-gated, makes "I will actually use these" a checkable part of the session instead of an internal hope. Together: receipt = I obtained the lesson; attestation = I know it applies here; commitment = I will use it while I work.

## HUMAN EXAMPLES

- A session begins: `contractctl resolve --task "add GitHub provider"` → attest → gate PASS → work proceeds. A stale pin or edited contract under the same version fails the gate loudly.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- `contractctl attest` produces the attestation block; `verify-attestation` re-checks receipts/hashes against the library.
- Lockfiles record id/version/path/SHA-256/receipt/status; bundle receipts derive from those.
- Conflict state is representable and blocks by default (fail closed).

## GOOD EXAMPLES

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
task-impact:
  - unknown states remain unknown in status reporting
  - API writes use observe → mutate → verify
conflicts: none
CONTRACT GATE: PASS

CONTRACT OPERATIONAL COMMITMENT v1
... (canonical commitment text) ...
bundle: cedar-lantern-47
task: add-github-provider
CONTRACT COMMITMENT: ACTIVE
```

## ANTI-PATTERNS

- "Contracts read and understood" without receipts/hashes/impacts.
- Attesting from memory while the file changed.
- Treating gate PASS as authorization to do anything.
- Silently dropping a contract because it conflicted.
- Reusing yesterday's attestation for today's changed library.
- Printing the commitment and immediately ignoring it; commitment without a changed way of working is a defect.
- A foreman accepting contracts, then dispatching workers with "do whatever".
- Faking compliance on conflict instead of returning an honest BLOCKED/INACTIVE state.
- Workers weakening the parent's applicable constraints instead of re-resolving and escalating.

## ACCEPTANCE CHECKS

- Does every mutating session produce a verifiable attestation AND an ACTIVE commitment before mutation?
- Do wrong receipt/hash/missing-required/stale-pin/conflict all prevent ACTIVE?
- Does each contract have a concrete task-impact sentence?
- Is BLOCKED/INACTIVE representable and honored as compliant behavior?
- Does a worker packet carry the inherited bundle and parent commitment?
- Does the commitment state fail closed when the bundle goes stale or the task's scope changes?