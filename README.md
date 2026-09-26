# Play-Nice

[![Play-Nice](assets/badge/badge-current.svg)](contracts/everyone/FLOOR.md)

**How people, AI agents, tools and websites work well together.** A short
floor everyone follows, plus packs of rules for what you're building.

## Start here

1. **Read [the floor](contracts/everyone/FLOOR.md).** One page, 17 plain
   rules. It applies to everyone, every time.
2. **Open the pack for what you're building** (full list in the
   [index](CONTRACT_INDEX.md)):

   | Pack | For |
   |---|---|
   | [Everyone](contracts/everyone/) | truth and unknowns, status words, asking for help, working together, recovery, ownership |
   | [Agents and work](contracts/work/) | AI agents and anyone doing a task: bounded work, handoffs, testing, git, proof |
   | [People](contracts/people/) | anything a person uses: attention, accessibility, sensory safety, depth, themes |
   | [Surfaces](contracts/surfaces/) | APIs, CLIs, web UIs, rooms: plain words, one truth for people and machines, setups that check themselves |
   | [Sites](contracts/sites/) | websites that people and agents can both use |
   | [Integration](contracts/integration/) | connecting to other services |
   | [Access](contracts/access/) | identity and roles, secrets and data, public and private |

3. **Prove you read it.** Agents start each handoff with one line:
   `Play-Nice floor <version> · receipt <word>` (details:
   [contract-proof](contracts/work/CONTRACT_PROOF.md)).

## Use it in a project

No install and no setup file needed. From a copy of this library:

```bash
python3 path/to/play-nice/tools/playnice/playnice.py start    # adds the floor to AGENTS.md and a badge to README
python3 path/to/play-nice/tools/playnice/playnice.py check    # checks the project, writes the bee badge
python3 path/to/play-nice/tools/playnice/playnice.py verify "Play-Nice floor 1.0.0 · receipt <word>"
python3 path/to/play-nice/tools/contractctl/contractctl resolve --task "add a settings page"   # which rules apply
```

`check` also takes a website: `playnice.py check https://example.org` reads
its `/.well-known/play-nice.json` (see [friendly-site](contracts/sites/FRIENDLY_SITE.md)).

## The bee badge

<img src="assets/badge/bee.svg" width="48" alt="The Play-Nice bee">

A project shows the badge that `check` writes: **plays nice**, **behind**
(a newer version is out), or **fix needed**. The badge links to the check
that made it; a copied picture proves nothing. How the badge and the docs
look and sound: [design philosophy](docs/DESIGN_PHILOSOPHY.md).

## Changing the library

Contracts change by pull request, reviewed by the owner. See
[CONTRIBUTING.md](CONTRIBUTING.md) and [maintaining](docs/MAINTAINING.md)
(tests, CI, versioning, the legacy gate). Old contract names still work: see
the old-name table in the [index](CONTRACT_INDEX.md) and `aliases.json`.

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
