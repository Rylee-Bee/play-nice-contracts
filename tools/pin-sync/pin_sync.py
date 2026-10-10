#!/usr/bin/env python3
"""pin-sync: keep adopters' Play-Nice pins current without a human treadmill.

For each adopter repo (config: ~/.config/play-nice/pin-sync.json), compare
its adoption manifest's `source.revision` with play-nice-contracts' main:

- same: nothing to do;
- behind: open ONE pin PR (branch `play-nice/pin-<sha7>`) that moves the
  revision and lists exactly which contracts changed (from
  contracts.lock.json at both revisions). Older pin-robot PRs are closed as
  superseded (never deleted);
- a pin-robot PR that is open, mergeable and fully green is merged
  (squash), unless it carries a breaking change (a contract removed, or a
  major version bump): those PRs are labelled in the title and wait for a
  person. Never with an admin override: a red or blocked PR waits and is
  reported.

The upstream change itself was already reviewed and merged in Play-Nice;
this only follows it. Uses the `gh` CLI (its own login); never prints a
token. Stdlib only.

    pin_sync.py            # do it
    pin_sync.py --dry-run  # say what it would do
    pin_sync.py --json     # machine-readable report
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

UPSTREAM = "rylee-bee-labs/play-nice-contracts"
CONFIG = Path(os.environ.get("PIN_SYNC_CONFIG", Path.home() / ".config/play-nice/pin-sync.json"))
GH = os.environ.get("PIN_SYNC_GH", "gh")
BRANCH_PREFIX = "play-nice/pin-"
REV_LINE = re.compile(r"^(\s*revision:\s*)([0-9a-f]{7,40})(.*)$", re.M)


class GhError(RuntimeError):
    pass


def gh(*args: str, input_: str | None = None) -> str:
    r = subprocess.run([GH, *args], capture_output=True, text=True, input=input_, timeout=120)
    if r.returncode != 0:
        raise GhError(f"gh {' '.join(args[:3])}: {r.stderr.strip()[:300]}")
    return r.stdout


def api(path: str, method: str = "GET", body: dict | None = None):
    args = ["api", "-X", method, path]
    if body is not None:
        args += ["--input", "-"]
    out = gh(*args, input_=json.dumps(body) if body is not None else None)
    return json.loads(out) if out.strip() else None


def lock_at(rev: str) -> dict[str, str]:
    """contract id -> version in contracts.lock.json at a revision."""
    f = api(f"repos/{UPSTREAM}/contents/contracts.lock.json?ref={rev}")
    lock = json.loads(base64.b64decode(f["content"]))
    return {c["id"]: c.get("version", "?") for c in lock.get("contracts", [])}


def _major(v: str) -> str:
    return v.split(".", 1)[0]


def contract_changes(old: str, new: str) -> tuple[list[str], bool]:
    """(plain lines on which contracts were added, changed or removed,
    whether any change is breaking: a removal or a major version bump).
    An unreadable lock counts as breaking, so it waits for a person."""
    try:
        a, b = lock_at(old), lock_at(new)
    except (GhError, KeyError, ValueError):
        return ["(couldn't read contracts.lock.json at both revisions; read the upstream diff)"], True
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    removed = sorted(set(a) - set(b))
    out = [f"`{k}` {a[k]} -> {b[k]}" + (" (major)" if _major(a[k]) != _major(b[k]) else "") for k in changed]
    out += [f"`{k}` {b[k]} (new)" for k in sorted(set(b) - set(a))]
    out += [f"`{k}` removed" for k in removed]
    breaking = bool(removed) or any(_major(a[k]) != _major(b[k]) for k in changed)
    return (out or ["no contract changed (docs, tooling or tests only)"]), breaking


def robot_prs(repo: str) -> list[dict]:
    out = gh("pr", "list", "-R", repo, "--state", "open", "--json",
             "number,headRefName,mergeable,mergeStateStatus,statusCheckRollup,title")
    return [p for p in json.loads(out) if p["headRefName"].startswith(BRANCH_PREFIX)]


def all_green(pr: dict) -> bool:
    checks = pr.get("statusCheckRollup") or []
    if not checks:
        return False
    for c in checks:
        state = (c.get("conclusion") or c.get("state") or "").upper()
        if state not in ("SUCCESS", "SKIPPED", "NEUTRAL"):
            return False
    return True


def sync_repo(entry: dict, head: str, dry: bool) -> dict:
    repo, manifest = entry["repo"], entry["manifest"]
    report: dict = {"repo": repo, "actions": []}
    meta = api(f"repos/{repo}")
    base = meta["default_branch"]
    f = api(f"repos/{repo}/contents/{manifest}?ref={base}")
    text = base64.b64decode(f["content"]).decode()
    m = REV_LINE.search(text)
    if not m:
        report["status"] = "unknown"
        report["actions"].append(f"no `revision:` line in {manifest}; nothing changed")
        return report
    pin = m.group(2)
    prs = robot_prs(repo)

    # 0. Already current (someone pinned by hand, or a robot PR merged):
    # any robot PR left open is no longer needed.
    if head.startswith(pin) or pin.startswith(head[:len(pin)]):
        for pr in prs:
            report["actions"].append(f"close #{pr['number']} (already current)")
            if not dry:
                gh("pr", "close", str(pr["number"]), "-R", repo, "--comment",
                   f"Already current at {head[:7]}; this pin PR isn't needed.")
        report["status"] = "current"
        return report

    # 1. Merge a green robot PR (it may be for `head` or older; only the newest matters).
    for pr in prs:
        if pr["headRefName"] != BRANCH_PREFIX + head[:7]:
            continue
        if "needs a person" in pr["title"]:
            report["actions"].append(f"#{pr['number']} waits for a person (breaking change)")
            report["status"] = "waiting"
            return report
        if pr["mergeable"] == "MERGEABLE" and pr["mergeStateStatus"] in ("CLEAN", "HAS_HOOKS", "UNSTABLE") and all_green(pr):
            report["actions"].append(f"merge #{pr['number']} (green)")
            if not dry:
                gh("pr", "merge", str(pr["number"]), "-R", repo, "--squash", "--delete-branch")
            report["status"] = "merged"
            return report
        report["actions"].append(f"#{pr['number']} waiting ({pr['mergeStateStatus'].lower()})")
        report["status"] = "waiting"
        return report

    # 2. Close superseded robot PRs, then open one for `head`.
    for pr in prs:
        report["actions"].append(f"close #{pr['number']} (superseded by {head[:7]})")
        if not dry:
            gh("pr", "close", str(pr["number"]), "-R", repo, "--comment",
               f"Superseded: Play-Nice moved to {head[:7]}; a new pin PR follows.")
    changes, breaking = contract_changes(pin, head)
    today = dt.date.today().isoformat()
    new_text = REV_LINE.sub(
        lambda mm: f"{mm.group(1)}{head}   # pin robot {today}: follows play-nice-contracts main; "
                   f"changed since {pin[:7]}: {'; '.join(changes)[:300]}",
        text, count=1)
    branch = BRANCH_PREFIX + head[:7]
    report["actions"].append(f"open pin PR {pin[:7]} -> {head[:7]}" + (" (breaking: waits for a person)" if breaking else ""))
    report["status"] = "opened"
    if dry:
        return report
    base_sha = api(f"repos/{repo}/git/ref/heads/{base}")["object"]["sha"]
    api(f"repos/{repo}/git/refs", "POST", {"ref": f"refs/heads/{branch}", "sha": base_sha})
    api(f"repos/{repo}/contents/{manifest}", "PUT", {
        "message": f"chore(play-nice): pin {head[:7]} (pin robot)",
        "content": base64.b64encode(new_text.encode()).decode(),
        "sha": f["sha"], "branch": branch})
    body = "\n".join([
        f"The pin robot follows play-nice-contracts main: `{pin[:7]}` -> `{head[:7]}`.",
        "", "**What changed in the contracts:**", *[f"- {c}" for c in changes], "",
        f"Upstream diff: https://github.com/{UPSTREAM}/compare/{pin}...{head}", "",
        ("**This one needs a person:** a contract was removed or changed its major version, so this "
         "project may need real changes before it can follow. The robot won't merge it."
         if breaking else
         "The upstream change was already reviewed and merged in Play-Nice. This PR merges itself "
         "once every check is green (never with an admin override); a red check waits for a person."),
        "", "Opened by `tools/pin-sync` in play-nice-contracts.",
    ])
    gh("pr", "create", "-R", repo, "--head", branch, "--base", base,
       "--title", f"chore(play-nice): pin {head[:7]} (pin robot{'; needs a person' if breaking else ''})",
       "--body", body)
    return report


def main(argv: list[str]) -> int:
    dry = "--dry-run" in argv
    try:
        entries = json.loads(CONFIG.read_text())["adopters"]
    except (OSError, ValueError, KeyError) as e:
        print(f"pin-sync: can't read {CONFIG} ({type(e).__name__}). It needs "
              '{"adopters": [{"repo": "Owner/name", "manifest": "path/to/adoption.yaml"}]}.')
        return 2
    try:
        head = api(f"repos/{UPSTREAM}/commits/main")["sha"]
    except GhError as e:
        print(f"pin-sync: couldn't read {UPSTREAM} main: {e}")
        return 2
    reports = []
    for entry in entries:
        try:
            reports.append(sync_repo(entry, head, dry))
        except (GhError, KeyError, ValueError) as e:
            reports.append({"repo": entry.get("repo"), "status": "error", "actions": [str(e)[:300]]})
    if "--json" in argv:
        print(json.dumps({"upstream": head, "dry_run": dry, "repos": reports}, indent=2))
    else:
        for r in reports:
            print(f"{r['repo']}: {r['status']}" + (" · " + " · ".join(r["actions"]) if r["actions"] else ""))
    return 1 if any(r["status"] == "error" for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
