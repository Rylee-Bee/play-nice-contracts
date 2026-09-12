# Project Context

This directory contains durable context that helps humans, bots, tools, and
external services work with this project without rediscovering the same
information each session.

- **Contracts** define how participants behave together.
- **Project context** defines what this project is.
- **Participant packs** describe how optional collaborators interact with it.

Participant data may enrich project truth but does not silently replace it.

The three layers:

```text
PLAY-NICE CONTRACTS   how everybody should behave together (universal)
        ↓
PROJECT CONTEXT       what this particular project is, wants, owns, and uses
        ↓
PARTICIPANT PACKS     optional knowledge from tools/services/people that
                      helps them interact well with the project
```

Deleting any participant pack must not corrupt the project — it only reduces
convenience or live capability. No secrets here, ever.

See the `project-context-and-participant-packs` contract in the Play-Nice
library for the full model.