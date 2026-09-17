---
contract_id: documentation-and-continuity
title: Documentation and Continuity
version: 1.1.0
status: canonical
layer: engineering
applies: [docs, engineering, agents]
triggers: [documentation, handoffs, always]
rationale: Documentation is an interface for humans, agents, maintainers, and future sessions. Nobody should need transcript archaeology to know where things stand.
---

<!-- contract-receipt: oasis-opal-amber -->

# Documentation and Continuity

## Purpose

Make documentation an interface: canonical locations, explicit ownership, current state, examples, schemas, and links — serving humans, agents, maintainers, and future sessions.

## NORMATIVE RULES

1. Documentation serves: humans (understand and operate), agents (load contracts and context), maintainers (extend safely), and future sessions (resume cold). If it serves only one, it is incomplete.
2. Canonical location: each piece of truth has exactly one authoritative home; everything else routes there. Summaries route, they do not govern.
3. Explicit ownership and currency: docs state what they cover, their status (current/historical/archived), and who owns them. Historical information is clearly marked historical — never mistaken for current.
4. Current state must be inspectable without archaeology: a returning human or fresh agent session determines what is done, what is in flight, and what is next from durable state (handoffs, STATUS files, roadmaps) — not from chat history.
5. Prefer: concise summaries, examples, schemas, and links over exhaustive prose. A small example beats a paragraph of abstract description.
6. Docs change with the code they describe: commands, contracts, and behaviors stay in sync in the same change that alters them (drift is a defect).
7. Transcript archaeology is an anti-pattern: if the answer to "why is this like this?" lives only in an old conversation, it belongs in a doc, ADR, or provenance record now.
8. Every project maintains a minimal continuity surface: what this is, how to verify, where truth lives, how to resume.
9. Documentation requires a brevity pass. Before human-facing documentation is complete, make one explicit pass to remove: repeated explanations, throat-clearing introductions, background that does not help the current task, formal wording where ordinary wording works, paragraphs that could be one sentence, sections that do not improve navigation, and explanations added merely because the author knows the detail. Prefer this order: what this is, what the person needs to do, what they need to know to do it safely, deeper explanation and implementation detail (see Copy and Language).
10. Documentation must use ordinary words (see Copy and Language rule 9). When two versions mean the same thing, prefer the shorter, more familiar, easier-to-scan wording. Do not add words to sound formal, complete, or authoritative.

## RATIONALE

The ecosystem's most expensive recurring cost was re-derivation: new sessions (human or agent) rediscovering what previous sessions knew because it lived in scrollback. Canonical docs + handoff formats + provenance convert that from a rite of passage into a lookup. The brevity pass ensures that documentation remains an interface rather than a knowledge dump: the reader should find what they need before they find what the author knew.

## HUMAN EXAMPLES

- A fresh agent session reads AGENTS.md → contract index → STATUS doc and is productive in minutes without asking anyone.
- A README's "Commands" section matches reality because CI tests it.
- A retired spec says `Status: archived (superseded by X)` at the top — impossible to mistake for current.

## MACHINE / IMPLEMENTATION IMPLICATIONS

- Docs that state commands are verifiable (doc-lint that runs the commands it teaches where feasible).
- Contract/index registries are data (see this library's CONTRACT_INDEX.md).
- Handoff documents are a supported, structured output (see Handoff).
- Status/roadmap files carry update dates and are part of the definition of done.

## GOOD EXAMPLES

```markdown
| Want to...          | Read this                 |
|---------------------|---------------------------|
| Run the tests       | `uv run pytest -q`        |
| Understand status    | STATUS.md (updated weekly)|
| Find design truth    | docs/DESIGN.md (canonical)|
```

## ANTI-PATTERNS

- The real documentation living in a Slack thread.
- A README whose commands haven't worked in a year.
- Archived specs indistinguishable from live ones.
- "Ask <person> how it works."
- Docs updated "later" (i.e., never) after a behavior change.

## ACCEPTANCE CHECKS

- Can a cold session orient in under ten minutes using only durable files?
- Is exactly one authoritative source findable per topic?
- Are historical docs marked historical?
- Do documented commands still work?