---
contract_id: project-context-and-participant-packs
title: Project Context and Participant Packs
version: 1.2.0
status: canonical
layer: core
applies: [projects, agents, tools, services, documentation, onboarding]
triggers: [project-onboarding, participant-integration, new-session, project-memory]
rationale: Every new session should not have to rediscover how a particular project, service, tool, or collaborator works. After accepting Play-Nice contracts, a participant should be able to say: I agree — and here is useful information you can retain with this project. Mutual courtesy encoded as durable, structured project context.
---

<!-- contract-receipt: sail-dell-ember -->

# Project Context and Participant Packs

## Purpose

Solve the recurring rediscovery problem. Three clearly separated concepts:

```text
PLAY-NICE CONTRACTS   — how everybody should behave together (universal)
        ↓
PROJECT CONTEXT       — what this particular project is, wants, owns, and uses
        ↓
PARTICIPANT PACKS     — optional knowledge supplied by tools/services/people
                        that helps them interact well with the project
```

A new human, bot, tool, or service should not need to rediscover the relationship from scratch. Agree on how to play nice; introduce yourself; share what makes cooperation easier; remember it for next time.

## NORMATIVE RULES

### The three layers

1. Contracts are universal and govern behavior. Project context is project-specific truth. Participant packs are optional, replaceable enrichment describing working relationships.
2. A participant pack MUST NOT become canonical project truth unless the project explicitly promotes information from it. Authority flows:
   ```text
   PROJECT TRUTH
        ↓
   capability / policy boundary
        ↓
   PARTICIPANT PACK
        ↓
   external tool/service/provider
   ```
   Never: "Figma said this once, therefore Figma owns project architecture forever." Packs help interaction; they do not own the project.

### Standard project directory

3. The recommended project structure (create only useful sections — the template defines vocabulary and placement; it must not create empty bureaucratic clutter):
   ```text
   .project/
   ├── README.md            # durable-context explanation (see rule 28 of the framework)
   ├── project.yaml         # machine-readable manifest (play-nice/project-v1)
   ├── CURRENT.md            # where things stand now
   ├── DECISIONS.md          # decision provenance
   ├── contracts/adoption.yaml   # Play-Nice adoption manifest
   ├── context/             # purpose, architecture, vocabulary, interfaces,
   │                        # constraints, current-state, recovery
   ├── participants/
   │   ├── README.md
   │   └── <participant-id>/    # participant.yaml, capabilities.yaml,
   │                            # interaction.md, references.yaml, artifacts/, examples/
   ├── design/              # CURRENT.md, references.yaml, exports/
   ├── integrations/<id>/   # integration.yaml, mapping.md, notes.md
   ├── handoffs/            # CURRENT.md, archive/
   └── history/decisions/
   ```

### project.yaml

4. A small machine-readable manifest (`play-nice/project-v1`): id, name, purpose summary, ownership (human, role), pointers to the adoption manifest and canonical files, participants directory, status vocabulary. **No secrets.**

### Participant packs

5. A participant is anything that regularly interacts with the project: design services, forges, agents, test tools, deployment systems, databases, human teams, external APIs.
6. After contract resolution and operational commitment, a participant may optionally provide a cooperation package — friendly and conversational, not legalistic:
   ```text
   PLAY-NICE PARTICIPANT ACCEPTANCE v1

   participant: <id>
   contract_bundle: <hash>
   contract_commitment: ACTIVE

   I accept the applicable Play-Nice operating constraints.

   To make future collaboration easier, I can provide the following
   project-relevant information: capabilities I expose; tools/interfaces
   available; supported input/output formats; identifiers worth preserving;
   canonical references; recommended workflows; limitations; version
   information; useful exports; interoperability notes.

   This information is optional project context. It does not override
   project truth, authorization, or other contracts.

   PARTICIPANT PACK: OFFERED
   ```
7. A participant pack declares (play-nice/participant-v1): identity, type, relationship (role, optional-ness, `authoritative_for` AND `not_authoritative_for`), interfaces, pointers to capabilities/interaction/references files, and provenance (supplied_by, observed_at, source_revision).
8. Capabilities are real discovered capabilities — do not invent capabilities merely to populate the file. Limitations are recorded alongside.
9. The interaction guide answers: how do we work effectively with this participant? Best uses; what to check before asking it; how to consume its output; what NOT to assume.
10. References are stable things future sessions should know exist (external IDs are useful; secrets are not).
11. Packs are bidirectional: the project also records what helps the collaboration work (canonical visual source, accessibility contract, composition anti-patterns, implementation framework, verification requirements). The pack is a shared boundary document — not "what do I know about Figma?" but "what do Figma and this project know about working together?"

### Human and agent participants

12. Human/team packs describe working relationships — role, ownership boundaries, preferred review flow, escalation path, artifact expectations — not dossiers. No sensitive personal profiles.
13. Agent packs may describe strengths, approved roles, task shapes, tools, evidence expectations — but must not encode temporary model folklore as eternal truth: separate the stable role contract from observed behavior, and version/refresh observations. The observed-capability vocabulary (see Participation and Contribution rule 22):
    ```yaml
    strengths: [classification, bounded-code-generation]
    limitations: [no-browser, weak-long-context]
    good_task_shapes: [small-independent-files, structured-input-output]
    avoid_task_shapes: [architecture-convergence, visual-judgment]
    ```
    is versioned, dated observation data — it routes delegation; it never becomes authority or an eternal property of the participant. Packs may also carry contribution-fit guidance (`good_fits` / `workable_with_support` / `poor_fits` / `preferred_task_shape`) so future orchestrators offer work the participant can agree to comfortably (see Mutual Contribution by Agreement).

### Discovery and updates

14. Where a service's API can describe itself, generate participant information from authoritative discovery; do not hand-maintain what an API reliably publishes. Preserve a readable snapshot + provenance so future sessions know what was observed.
15. Updates follow: discover → compare with stored pack → show meaningful differences → update pack → record provenance. Never silently overwrite meaningful human decisions.

### Session bootstrap

16. A future session: identify project → load project.yaml → resolve contracts → attest + commit → inspect applicable participant packs → load only task-relevant participant context → work. Participant context is resolved like contracts: the smallest useful applicable set, never everything.

### Ask-for-help integration

17. Participant packs act as routing maps for cooperation: manifests may declare `help.can_answer`, `help.cannot_answer`, and preferred question format (`play-nice/question-v1`). An agent needing a design reference checks the Figma pack's capabilities, discovers `export-frame`, and asks Figma — not the human — falling back to foreman then owner only when the choice is human-owned.

### Canonicality, provenance, no lock-in

18. Participant artifacts carry statuses from a closed vocabulary: `canonical`, `reference`, `observed`, `generated`, `historical`, `superseded`, `stale`, `unknown`. Not everything is equally authoritative; future sessions must distinguish current project truth, current participant data, and historical participant data.
19. Every imported participant artifact retains provenance: source, participant, observed_at, version/revision if available, canonical_status, import_method.
20. Packs are optional enrichment with no lock-in: deleting `.project/participants/figma/` must not corrupt the project. It may reduce convenience or live capability; it must not destroy canonical project truth. Code, exports, tokens, composition docs, and accessibility rules all survive.

### Privacy

21. Participant packs MUST NOT become a convenient place to dump credentials. Never persist API keys, tokens, passwords, session cookies, or private auth payloads. Persist references to secret stores instead:
   ```yaml
   authentication:
     method: oauth
     secret_reference: figma/oauth
   ```

## RATIONALE

Contracts let participants agree on how to behave. Project context tells them where they are. Participant packs teach them how to work together. A friendly participant does not merely say "I agree" — it offers the useful information that makes future cooperation easier. A friendly project remembers that information so the participant does not have to explain itself again next session. That is mutual courtesy encoded as architecture, and it follows the ecosystem's core lesson: durable, inspectable, well-provenanced state beats session memory (see Stable Truth, Provenance, Ask for Help).

## HUMAN EXAMPLES

- Rylee asks Figma: "Please resolve and accept the Play-Nice contracts applicable to our work. Then tell me, in human- and machine-readable form, what capabilities you expose, what interfaces we can use, what references to preserve, what you are authoritative for and NOT authoritative for, your limitations, and what questions you can answer directly." Figma returns a proposed pack; the project validates and stores it under `.project/participants/figma/`.
- A future session changing Today loads: applicable contracts, project context, the Figma pack's capabilities, and the current Today visual reference — and knows how to work with Figma without being taught again.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Schemas: `project.schema.json` (project-v1 manifest), `participant.schema.json` (participant-v1 manifest + acceptance), `participant-capabilities.schema.json` (capabilities-v1), `references.schema.json` (references-v1) — reusing existing status/capability/question structures where sensible; no schema explosion.
- `contractctl` offers lightweight commands: `init-project` (minimal skeleton only), `project validate`, `participant validate`, `participant list`. contractctl must not become a project-management platform.
- Validation enforces: schema conformance, participant ID uniqueness per project, canonicality vocabulary, symbolic-secret-only authentication blocks, and no secret-shaped content anywhere in a pack.
- Packs parse without their Markdown companions (machine files stand alone); the human README/context exists alongside.

## GOOD EXAMPLES

```yaml
# .project/participants/figma/participant.yaml (excerpt)
schema: play-nice/participant-v1
id: figma
type: design-service
relationship:
  role: design-source
  optional: true
  authoritative_for: [approved-visual-composition, design-tokens-when-explicitly-designated]
  not_authoritative_for: [product-policy, runtime-state, accessibility-floor, source-code-truth]
help:
  can_answer: [visual-composition, design-token, frame-reference]
  cannot_answer: [product-priority, deployment-state]
  preferred_question_format: {schema: play-nice/question-v1}
```

## ANTI-PATTERNS

- "Figma said this once, therefore Figma owns project architecture forever."
- Packs containing tokens or API keys ("convenient" credential dumping).
- Invented capabilities to fill the file.
- Temporary model folklore encoded as eternal participant truth.
- Loading every participant pack into every session's context.
- Deleting a pack corrupts the project.
- Everything marked equally `canonical`; provenance silently overwritten.
- Empty bureaucratic directory forests created "for completeness".
- A participant pack promoted to canonical truth without an explicit, recorded promotion.

## ACCEPTANCE CHECKS

- Can a new session orient (project, contracts, relevant participants) without a human teaching it?
- Does deleting any participant pack leave canonical truth intact?
- Does every imported artifact carry provenance and a canonicality status?
- Are authoritative-for and not-authoritative-for both declared?
- Is any secret-shaped material present anywhere in a pack? (Must be structurally impossible.)
- Is participant context loaded by relevance, like contracts — not wholesale?