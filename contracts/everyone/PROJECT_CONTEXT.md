---
contract_id: project-context
title: Project Context
version: 2.0.0
status: canonical
layer: everyone
applies: [humans, agents, tools, services, projects]
triggers: [onboarding, project-context, project-structure, participant, session-start, documentation, setup]
rationale: A new session should orient from durable files, not rediscover the project and its participants from scratch every time.
---

<!-- contract-receipt: warp-nettle-cuff -->

# Project Context

## In short

Remember, in plain files, what this project is and how each participant
works with it. Project truth comes first; participant notes are optional
enrichment.

## Applies when

You set up a project, record what a participant (a person, tool, service,
or agent) brings to working with it, or resume work in a new session.
Command mechanics live in the tool docs; this contract fixes the shape of
the files.

## Rules

1. **Keep three things separate:** contracts (how everyone behaves),
   project context (what this project is, wants, owns, uses), and
   participant packs (what one participant adds to the collaboration).
   Authority runs in that order, then the external tool itself. (MUST)
2. **A participant pack is never project truth.** It helps interaction;
   promoting information from a pack into canonical status takes an
   explicit, recorded project decision. "It said so once" grants no
   lasting authority. (MUST)
3. **The standard home is `.project/`:** README.md, project.yaml,
   CURRENT.md, DECISIONS.md, the adoption manifest under contracts/, and
   as needed participants/<id>/, design/, integrations/<id>/, handoffs/,
   history/. Create only sections that carry content — an empty directory
   forest is a defect. (SHOULD)
4. **project.yaml is small and secret-free:** id, name, purpose,
   ownership, and pointers to the adoption manifest, canonical files, and
   the participants directory. (MUST)
5. **Each participant pack declares:** identity and type; its role and
   whether it's optional; what it is authoritative for and — equally —
   what it is not; discovered capabilities with their limits beside them;
   how to work with it; stable references; and provenance (supplied_by,
   observed_at, source_revision). (MUST)
6. **Record only real, discovered capabilities.** Never invent
   capabilities to fill the file. Where a service's API can describe
   itself, generate the pack from discovery and keep a readable snapshot. (MUST)
7. **Observed behavior is dated, versioned data — never authority.**
   Strengths, limits, and good task shapes get refreshed as tools change;
   separate the stable role from the observation, and don't turn
   temporary limits into permanent ranks. (MUST)
8. **Packs describe the relationship, not a dossier.** Record how both
   sides work together: best uses, what to check before asking it, how to
   consume its output, what not to assume. Human packs cover roles,
   ownership boundaries, review and escalation preferences — no sensitive
   personal profiles. (MUST)
9. **Updates show meaningful differences before applying them** and never
   silently overwrite a human decision in a pack. (MUST)
10. **Load context by relevance.** A session takes the smallest useful
    set of packs — like contracts — never everything. (MUST)
11. **Deletion must be safe:** removing any participant pack can cost
    convenience, never canonical truth. And packs never store credentials
    — references to the secret store only (see the floor, rule 11). (MUST)
12. **Imported artifacts carry a canonicality status** — canonical,
    reference, observed, generated, historical, superseded, stale,
    unknown — so a future session can tell current truth from history. (SHOULD)

## Examples

- Good: the design tool's pack says `authoritative_for:
  approved-visual-composition` and `not_authoritative_for: product-policy,
  runtime-state, source-code-truth`; a session asks it about composition
  and the human about priority.
- Bad: "It said this once, so it owns the architecture forever."
- Bad: a pack storing an API key because it was convenient.

## Why

Every fresh session repeats the same discovery work unless something
remembers for it. Durable, provenanced notes about the project and its
collaborators are courtesy made structural: say what you can do, have it
kept, and nobody has to introduce themselves again next session.

## You're done when

- A new session can orient — project, contracts, relevant participants —
  without a human teaching it.
- Every pack declares both what it is and what it isn't authoritative
  for.
- Deleting any participant pack leaves the project valid.
- No secret-shaped value exists anywhere in a pack.

## Machine notes

Schemas: `schema/project.schema.json` (project-v1),
`schema/participant.schema.json`,
`schema/participant-capabilities.schema.json`,
`schema/references.schema.json`. A pack's machine files parse without
their Markdown companions. A pack may route questions with `help`
fields: `can_answer`, `cannot_answer`, `preferred_question_format` (see
ask-for-help).
