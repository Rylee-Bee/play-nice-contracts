# Contract Index

The registry of every contract in this library. Exactly one authoritative source per contract; this index routes, it does not govern.

Load discipline: resolve the smallest applicable set (see `contractctl resolve`), read each contract from its canonical file, attest before mutating work. Do not load everything merely because it exists.

Layers, in resolution order of authority: universal safety/interoperability (core) → human experience/accessibility floor → project contracts → user/org preferences → theme/personality.

## Core (universal floor)

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `assume-unknown` | Assume UNKNOWN — Epistemic Humility Before Execution | 1.0.0 | canonical | Challenge unproven interpretations before execution; authority and evidence do not guarantee understanding |
| `truth-and-evidence` | Truth and Evidence | 1.0.0 | canonical | Honesty cheaper than fabrication; UNKNOWN is valid; evidence over reports |
| `stable-truth-replaceable-machinery` | Stable Truth, Replaceable Machinery | 1.0.0 | canonical | Truth survives tool replacement; derived ≠ canonical |
| `provenance-and-audit` | Provenance and Audit | 1.0.0 | canonical | Who/what changed it, when, why; generated labeled; history recoverable |
| `recovery-and-reversibility` | Recovery and Reversibility | 1.0.0 | canonical | Previews, rollback, PROVE STALE → CLEAN; mistakes become guardrails |
| `portability-and-ownership` | Portability and Ownership | 1.0.0 | canonical | Leave any tool with your data; explicit ownership boundaries |
| `explicit-state` | Explicit State | 1.0.0 | canonical | Shared status vocabulary; state never inferred from silence |
| `ask-for-help` | Ask for Help | 1.3.0 | canonical | Ask the participant who owns the answer; honest refusal + negotiation in-bounds; uncertainty is never ridiculed |
| `collaborative-good-faith` | Collaborative Good Faith | 1.0.0 | canonical | Be useful without being cruel; critique the work, not the participant; disagreement toward repair; safe uncertainty |
| `mutual-contribution` | Mutual Contribution by Agreement | 1.1.0 | canonical | Contributions are offered and agreed, not imposed; both sides state constraints; DECLINE is not disobedience |
| `participation-and-contribution` | Participation and Contribution | 1.2.0 | canonical | Right-sized participation: smallest suitable participant, bounded contributions, no model castes |
| `project-context-and-participant-packs` | Project Context and Participant Packs | 1.2.0 | canonical | Durable project context + optional participant packs; contribution-fit guidance routes offers |
| `play-nice-together` | Play Nice Together | 1.6.0 | canonical | The constitution: everything plays nicely with everything else |

## Human (experience floor)

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `human-reliability` | Human Reliability | 1.2.0 | canonical | No heroics; attention finite; reduced cognitive capacity; unknowns preserved; resumable |
| `accessibility-floor` | Accessibility Floor | 1.0.0 | canonical | Accessibility is architecture: keyboard, targets, labels, zoom, focus |
| `migraine-and-sensory-safety` | Migraine and Sensory Safety | 1.0.0 | canonical | Low-glare, static-first, reduced-motion unconditional; no strobing |
| `low-vision-and-reflow` | Low Vision and Reflow | 1.0.0 | canonical | 200% zoom/reflow gate; text scaling; forced-colors; coherent contrast |
| `attention-and-focus` | Attention and Focus | 1.0.0 | canonical | Control when complexity enters attention; externalize memory |
| `interruption-and-resumption` | Interruption and Resumption | 1.0.0 | canonical | Interruption is normal; resumption without archaeology |
| `complexity-on-demand` | Complexity on Demand | 1.0.0 | canonical | Depth ladder L0–L3; organize complexity, never remove it |

## Experience (product behavior)

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `what-why-next` | What / Why / Next | 1.0.0 | canonical | Important work answers what, why it matters, what's next |
| `progressive-disclosure` | Progressive Disclosure | 1.1.0 | canonical | Smallest useful view first; human meaning leads; summaries never lie; native mechanisms |
| `quiet-when-healthy` | Quiet When Healthy | 1.0.0 | canonical | Routine success costs zero attention; NO ACTION NEEDED valid |
| `progress-and-closure` | Progress and Closure | 1.0.0 | canonical | Real accomplishment rewarded; done beats additionally awesome |
| `guide-me` | Guide Me | 1.0.0 | canonical | Resumable guided paths for complex workflows; not every flow a wizard |
| `themes-and-personalization` | Themes and Personalization | 1.0.0 | canonical | Layered customization; theme never breaks the floor |
| `motion-and-feedback` | Motion and Feedback | 1.0.0 | canonical | Motion reduced by default, never essential; every action has observable result |
| `design-source-and-fidelity` | Design Source and Fidelity | 1.0.0 | canonical | Semantic tokens as canonical design truth; extract, never eyeball |
| `visual-fidelity-and-composition` | Visual Fidelity and Composition | 1.0.0 | canonical | Token fidelity ≠ design fidelity; composition is verified design data; D0–D4 levels |
| `copy-and-language` | Copy and Language | 1.1.0 | canonical | Words are interface; simplest clear language; brevity pass; truth before tone |

## Interoperability (playing with other systems)

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `capability-first` | Capability First | 1.1.0 | canonical | Intent → capability → policy → adapter → provider; vendors never own meaning |
| `friendly-api-client` | Friendly API Client | 1.0.0 | canonical | Learn, respect, read-before-write, retry intelligently, idempotent |
| `provider-neutrality` | Provider Neutrality | 1.0.0 | canonical | Provider-neutral meaning; namespaced enrichment; no config looks "real" |
| `discovery-and-negotiation` | Discovery and Negotiation | 1.1.0 | canonical | Ask what's supported; degrade gracefully on absence |
| `versioning-and-compatibility` | Versioning and Compatibility | 1.0.0 | canonical | Declared versions; breaks explicit; unknown fails clearly |
| `failure-and-degradation` | Failure and Degradation | 1.1.0 | canonical | Shared status vocabulary; optional failure contained; errors answer seven questions; no blame |
| `idempotency` | Idempotency | 1.0.0 | canonical | Repeated invocation never double-applies destruction |
| `polling-webhooks-and-caching` | Polling, Webhooks, and Caching | 1.0.0 | canonical | Prefer events; poll politely; cached data never masquerades as current |
| `external-mutations` | External Mutations | 1.0.1 | canonical | Observe → smallest mutation → verify → attribute; approval gates |

## Security

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `authorization` | Authorization | 1.0.0 | canonical | Explicit, scoped, fails closed; step-up for sensitive actions |
| `authentication` | Authentication | 1.0.0 | canonical | Provider-neutral identity seam; break-glass; multiple first-class paths |
| `secrets` | Secrets | 1.0.0 | canonical | Symbolic references only; structural exclusion everywhere |
| `data-classification` | Data Classification | 1.0.0 | canonical | public/private/secret assigned by core; payloads can't self-promote |
| `public-private-boundaries` | Public Private Boundaries | 1.0.0 | canonical | Canary-tested public safety; no private topology/medical history |
| `least-privilege` | Least Privilege | 1.0.0 | canonical | Exactly the permissions the bounded job needs; revocable |

## Engineering

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `deterministic-first` | Deterministic First | 1.0.0 | canonical | Deterministic substrate; AI at the edges; boots without models |
| `search-before-inventing` | Search Before Inventing | 1.0.0 | canonical | Inspect existing seams before parallel concepts |
| `bounded-work` | Bounded Work | 1.0.0 | canonical | Objective, scope, authority, budget, stop conditions |
| `testing-and-verification` | Testing and Verification | 1.0.0 | canonical | Evidence grades; "works" states its command |
| `dependency-discipline` | Dependency Discipline | 1.0.0 | canonical | Few, boring, pinned, reproducible; removal supported |
| `git-and-worktrees` | Git and Worktrees | 1.0.0 | canonical | PROVE STALE → CLEAN; per-lane worktrees; explicit staging |
| `documentation-and-continuity` | Documentation and Continuity | 1.1.0 | canonical | Docs are interfaces; brevity pass; ordinary words; no transcript archaeology |
| `migrations` | Migrations | 1.0.0 | canonical | CURRENT/TARGET/TRANSFORM/VALIDATE/ROLLBACK/DELETION GATE |
| `observability` | Observability | 1.0.0 | canonical | Correlated, attributed, secret-free, diagnosable |

## Agents

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `agent-behavior` | Agent Behavior | 1.1.0 | canonical | Inspect, preserve uncertainty, preserve human authority, truth before tone, verify, stop at boundaries |
| `orchestration` | Orchestration | 1.4.0 | canonical | Owner/architect/foreman/worker/gatekeeper; assignment is negotiated; foreman resolves heat into information; serial integration |
| `model-routing` | Model Routing | 1.2.0 | canonical | Sufficient-for-the-contribution routing, never prestige or benchmark; participant-stated conditions shape the task; no silent fallback |
| `worker-contract` | Worker Contract | 1.0.0 | canonical | Bounded packets: SHA, paths, criteria, exclusions, authority |
| `review-and-integration` | Review and Integration | 1.0.0 | canonical | Worker-green ≠ integration-green; review real diffs |
| `handoff` | Handoff | 1.0.0 | canonical | Resumable truth reports; cold-start continuation |
| `contract-attestation` | Contract Attestation | 1.2.0 | canonical | Full gate: freshness-verified source, receipt + hash + task-impact attestation, then OPERATIONAL COMMITMENT: ACTIVE before mutation |

## Interfaces

| ID | Title | Ver | Status | Purpose |
|---|---|---|---|---|
| `cli` | CLI | 1.0.0 | canonical | First-class surface; --json; exit codes; quiet success, loud failure |
| `api` | API | 1.0.0 | canonical | The programmable seam; versioned, honest envelopes, documented |
| `web-ui` | Web UI | 1.0.0 | canonical | A view, never the source of truth; honest states; floor applies |
| `machine-readable-output` | Machine Readable Output | 1.0.0 | canonical | Stable parseable shapes for scripts/agents/future tools |
| `human-and-machine-parity` | Human and Machine Parity | 1.1.0 | canonical | Every state legible twice; surfaces are views of one truth |

## How to use this index

```bash
contractctl list                          # every contract, current versions
contractctl show truth-and-evidence       # canonical text
contractctl resolve --manifest .contracts/adoption.yaml --task "add a GitHub provider"
contractctl attest --manifest ... --task ... --impact id=sentence ...
```

## Adding a contract

1. One file per contract, in its layer directory, named `ID_WITH_UNDERSCORES.md`.
2. Front matter validated by `schema/contract.schema.json` (contract_id, title, version, status, layer, applies, triggers).
3. Exactly one `<!-- contract-receipt: word-word-word -->` comment, unique in the library.
4. Body follows the dual-use structure: PURPOSE / NORMATIVE RULES / RATIONALE / HUMAN EXAMPLES / MACHINE IMPLICATIONS / GOOD EXAMPLES / ANTI-PATTERNS / ACCEPTANCE CHECKS.
5. Add the row here, run `contractctl validate && contractctl lock`, commit.