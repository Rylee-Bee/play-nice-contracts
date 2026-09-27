# pin-sync: the pin robot

> **Status:** Current · for projects that adopt Play-Nice and are tired of moving the pin by hand.

When play-nice-contracts' `main` moves, every adopter's `source.revision` falls behind and its freshness check turns red. `pin_sync.py` follows upstream for you:

- **Behind:** it opens one pin PR per adopter (branch `play-nice/pin-<sha7>`), listing exactly which contracts changed. An older robot PR is closed as superseded.
- **Green:** it merges its own PR on the next run (squash, never with an admin override).
- **Breaking** (a contract removed, or a major version bump): the PR title says "needs a person", and the robot leaves it for a person.

It pairs with ci-harness `expect: warn` on pull requests, so unrelated PRs aren't blocked while a pin PR is on its way. The default branch and the weekly schedule stay strict.

## Set it up

1. List the adopters in `~/.config/play-nice/pin-sync.json`:
   `{"adopters": [{"repo": "Owner/name", "manifest": ".project/contracts/adoption.yaml"}]}`
2. Make sure `gh` is signed in (the robot uses its login, so CI runs on its PRs).
3. Try it: `tools/pin-sync/pin_sync.py --dry-run`.
4. Run it every 15 minutes: copy `pin-sync.service` and `pin-sync.timer` to `~/.config/systemd/user/`, set the paths in the service, then `systemctl --user enable --now pin-sync.timer`.

`--json` gives a machine-readable report. Exit code 0 means all fine, 1 means an adopter errored (the others still ran), and 2 means the config or upstream couldn't be read.
