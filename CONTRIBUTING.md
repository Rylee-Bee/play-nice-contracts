# Contributing to Play-Nice Contracts

One maintainer of record (Rylee Hulgan). Agents, bots, and future
co-maintainers come through the same door.

1. **Branch, never main.** Work on a topic branch and open a pull
   request. Direct pushes to `main` are not the flow; admin bypass is
   reserved to the owner and to merges she has explicitly approved
   in-task (say so in the PR if you used it).
2. **Run the gate.** Substantial mutating work follows the contract
   gate against `.contracts/adoption.yaml`: freshness → resolve → read
   canonical text → attest → commit before implementation
   (see `AGENTS.md`).
3. **Know the change class.** `contracts/` and `schema/` are
   governance: state intent, bump per-contract semver, rotate receipts
   on MINOR/MAJOR, regenerate `contracts.lock.json` in the same
   commit. `tools/` is code: stdlib-only, tests accompany changes.
   `docs/`, `profiles/`, `examples/` must stay non-normative relative
   to `contracts/`.
4. **Keep the license map true.** Code MIT; contract text and docs
   CC BY-SA 4.0; identity per `TRADEMARKS.md`. The map is
   machine-checked by `tests/test_license_map.py`.
5. **Privacy floor.** Public repo: no tokens, hostnames, private IPs,
   family details, or medical history — CI scans for them.
6. **Continuity.** Every landed change gets a `CHANGELOG.md` entry
   (docs and licensing changes too). `VERSION` bumps only for
   library-level releases.
7. **Green or it didn't happen.** CI job `library` must pass; Rylee
   approves or merges.
