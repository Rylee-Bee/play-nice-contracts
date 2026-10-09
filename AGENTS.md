# AGENTS.md

**Using Play-Nice in a project (including a copy under `vendor/`)?**
Read [the floor](contracts/everyone/FLOOR.md), then the pack for what you're
building ([index](CONTRACT_INDEX.md)). Start your handoff with the proof line
from [contract-proof](contracts/work/CONTRACT_PROOF.md). Nothing else here
is needed.

**Changing this library itself?** Read
[docs/MAINTAINING.md](docs/MAINTAINING.md) first: tests, CI, versioning, and
the rules for agents working on this repository.

## The packs

The floor is for everyone. Each pack goes deeper for one kind of work; nothing
in a pack may go below the floor.

| Pack | For |
|---|---|
| [Everyone](contracts/everyone/) | truth and unknowns, status words, asking for help, working together, recovery, ownership |
| [Agents and work](contracts/work/) | AI agents and anyone doing a task: bounded work, handoffs, testing, git, proof |
| [People](contracts/people/) | anything a person uses: attention, accessibility, sensory safety, depth, themes |
| [Surfaces](contracts/surfaces/) | APIs, CLIs, web UIs, rooms: plain words, one truth for people and machines, setups that check themselves |
| [Sites](contracts/sites/) | websites that people and agents can both use |
| [Integration](contracts/integration/) | connecting to other services |
| [Access](contracts/access/) | identity and roles, secrets and data, public and private |

## Two version numbers, on purpose

The **library** is `2.0.0` (`VERSION`); the **floor** has its own version
(`1.0.0`), and that is the one the proof line names.

## Proving you read it

Agents put one line at the top of their handoff —
`Play-Nice floor <version> · receipt <word> · read <contract ids>` — and check
it with `playnice verify`, which prints `CURRENT` (exit 0), `OUT_OF_DATE`
(exit 1) or `INVALID` (exit 2). The receipt word is in the floor's source.

## The bee badge

`playnice check` writes a badge — **plays nice**, **behind** (a newer version is
out), or **fix needed**. It links to the check that made it; a copied picture
proves nothing. Run `check --badge playnice-badge.svg` yourself to write the
file and commit it.

`playnice check` also takes a website: `playnice.py check https://example.org`
reads its `/.well-known/play-nice.json` (see
[friendly-site](contracts/sites/FRIENDLY_SITE.md)).

## Changing the library

Contracts change by pull request, reviewed by the owner. See
[CONTRIBUTING.md](CONTRIBUTING.md) and [maintaining](docs/MAINTAINING.md)
(tests, CI, versioning, the legacy gate). The full gate is one command:
`./tools/check.sh`. Old contract names still work — see the old-name table in
the [index](CONTRACT_INDEX.md) and `aliases.json`.

Character and world content from Project Worlds lives in other repositories
under their own terms — nothing here licenses it, and it must never be moved
into this repository.

The license map (code MIT, contract text and docs CC BY-SA 4.0, identity per
`TRADEMARKS.md`) supersedes a brief same-window "MIT everywhere" experiment and
simplifies that baseline's MPL tooling layer to MIT; `CHANGELOG.md` records the
full sequence, including where the README had it wrong.

How the badge and the docs look and sound: [design
philosophy](docs/DESIGN_PHILOSOPHY.md).
