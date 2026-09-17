#!/usr/bin/env python3
"""Deterministic fake `gh` binary for the playnice test suite.

No test ever touches live GitHub. Set PLAY_NICE_GH to this script and
PLAY_NICE_FAKE_GH_SCENARIO to a JSON file:

    {
      "log": "/abs/path/gh.log",         # every invocation appended here
      "pr_list": [...],                   # `gh pr list --state open`
      "pr_list_merged": [...],            # `gh pr list --state merged`
      "issue_list": [...],                # `gh issue list --state open`
      "pr_view": {...},                   # `gh pr view N`
      "merge_fail": false                 # `gh pr merge N --merge`
    }

The script mirrors the `gh` JSON shapes the playnice orchestrator consumes.
"""

import json
import os
import sys


def main() -> int:
    scenario_path = os.environ.get("PLAY_NICE_FAKE_GH_SCENARIO", "")
    scenario: dict = {}
    if scenario_path:
        with open(scenario_path, encoding="utf-8") as f:
            scenario = json.load(f)

    log = scenario.get("log")
    if log:
        with open(log, "a", encoding="utf-8") as f:
            f.write(" ".join(sys.argv[1:]) + "\n")

    # strip `-R owner/repo` pairs the orchestrator may prefix
    argv = sys.argv[1:]
    args: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == "-R":
            i += 2
            continue
        args.append(argv[i])
        i += 1

    def value(flag: str) -> str | None:
        return args[args.index(flag) + 1] if flag in args else None

    if args[:2] == ["pr", "list"]:
        state = value("--state") or "open"
        key = "pr_list_merged" if state == "merged" else "pr_list"
        sys.stdout.write(json.dumps(scenario.get(key, [])) + "\n")
        return 0
    if args[:2] == ["pr", "merge"]:
        if scenario.get("merge_fail"):
            sys.stderr.write("merge failed\n")
            return 1
        sys.stdout.write(f"Merged pull request #{args[2]}\n")
        return 0
    if args[:2] == ["issue", "list"]:
        sys.stdout.write(json.dumps(scenario.get("issue_list", [])) + "\n")
        return 0
    if args[:2] == ["issue", "close"]:
        sys.stdout.write("closed\n")
        return 0
    if args[:2] == ["pr", "view"]:
        sys.stdout.write(json.dumps(scenario.get("pr_view", {})) + "\n")
        return 0

    sys.stderr.write(f"fake gh: unhandled invocation: {args!r}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
