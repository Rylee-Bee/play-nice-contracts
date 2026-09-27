"""pin-sync: the pin robot's decisions (no network; gh is faked)."""
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pin_sync", REPO / "tools" / "pin-sync" / "pin_sync.py")
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def _locks(monkeypatch, a, b):
    monkeypatch.setattr(ps, "lock_at", lambda rev: a if rev == "old" else b)


def test_minor_changes_are_not_breaking(monkeypatch):
    _locks(monkeypatch, {"room": "2.1.0", "library": "1.0.0"}, {"room": "2.2.0", "library": "1.1.0", "new": "1.0.0"})
    lines, breaking = ps.contract_changes("old", "new")
    assert not breaking
    assert "`room` 2.1.0 -> 2.2.0" in lines and "`new` 1.0.0 (new)" in lines


def test_removals_and_major_bumps_wait_for_a_person(monkeypatch):
    _locks(monkeypatch, {"room": "1.1.0", "gone": "1.0.0"}, {"room": "2.0.0"})
    lines, breaking = ps.contract_changes("old", "new")
    assert breaking and "`gone` removed" in lines and "`room` 1.1.0 -> 2.0.0 (major)" in lines


def test_unreadable_lock_is_treated_as_breaking(monkeypatch):
    def boom(rev):
        raise ps.GhError("nope")
    monkeypatch.setattr(ps, "lock_at", boom)
    assert ps.contract_changes("old", "new")[1] is True


def test_revision_line_is_found_and_replaced_once():
    text = "source:\n  repository: X\n  revision: abc1234def   # old note\nother: 1\n"
    m = ps.REV_LINE.search(text)
    assert m.group(2) == "abc1234def"
    out = ps.REV_LINE.sub(lambda mm: f"{mm.group(1)}ffff000   # new", text, count=1)
    assert "revision: ffff000   # new" in out and "other: 1" in out


def test_all_green_needs_every_check_to_pass():
    assert ps.all_green({"statusCheckRollup": [{"conclusion": "SUCCESS"}, {"conclusion": "SKIPPED"}]})
    assert not ps.all_green({"statusCheckRollup": [{"conclusion": "SUCCESS"}, {"conclusion": "FAILURE"}]})
    assert not ps.all_green({"statusCheckRollup": [{"state": "PENDING"}]})
    assert not ps.all_green({"statusCheckRollup": []})


def test_a_breaking_pr_is_never_merged(monkeypatch):
    calls = []
    head = "d4ed803325dd59e9de62b822c8143aa6a41c5a6c"
    manifest = "source:\n  revision: a0e3efb000000000000000000000000000000000\n"
    import base64

    def fake_api(path, method="GET", body=None):
        if path == "repos/O/r":
            return {"default_branch": "main"}
        if "contents/" in path:
            return {"content": base64.b64encode(manifest.encode()).decode(), "sha": "x"}
        raise AssertionError(path)

    def fake_gh(*args, input_=None):
        calls.append(args)
        if args[:2] == ("pr", "list"):
            return json.dumps([{"number": 9, "headRefName": "play-nice/pin-" + head[:7], "mergeable": "MERGEABLE",
                                "mergeStateStatus": "CLEAN", "statusCheckRollup": [{"conclusion": "SUCCESS"}],
                                "title": "chore(play-nice): pin d4ed803 (pin robot; needs a person)"}])
        return ""
    monkeypatch.setattr(ps, "api", fake_api)
    monkeypatch.setattr(ps, "gh", fake_gh)
    r = ps.sync_repo({"repo": "O/r", "manifest": "m.yaml"}, head, dry=False)
    assert r["status"] == "waiting"
    assert not [c for c in calls if c[:2] == ("pr", "merge")]


def test_a_green_follow_along_pr_merges_without_admin(monkeypatch):
    calls = []
    head = "d4ed803325dd59e9de62b822c8143aa6a41c5a6c"
    import base64
    monkeypatch.setattr(ps, "api", lambda path, method="GET", body=None: {"default_branch": "main"} if path == "repos/O/r"
                        else {"content": base64.b64encode(b"  revision: c801217\n").decode(), "sha": "x"})

    def fake_gh(*args, input_=None):
        calls.append(args)
        if args[:2] == ("pr", "list"):
            return json.dumps([{"number": 7, "headRefName": "play-nice/pin-" + head[:7], "mergeable": "MERGEABLE",
                                "mergeStateStatus": "CLEAN", "statusCheckRollup": [{"conclusion": "SUCCESS"}],
                                "title": "chore(play-nice): pin d4ed803 (pin robot)"}])
        return ""
    monkeypatch.setattr(ps, "gh", fake_gh)
    r = ps.sync_repo({"repo": "O/r", "manifest": "m.yaml"}, head, dry=False)
    merge = [c for c in calls if c[:2] == ("pr", "merge")]
    assert r["status"] == "merged" and merge and "--admin" not in merge[0]


def test_robot_prs_close_when_already_current(monkeypatch):
    calls = []
    head = "d4ed803325dd59e9de62b822c8143aa6a41c5a6c"
    import base64
    monkeypatch.setattr(ps, "api", lambda path, method="GET", body=None: {"default_branch": "main"} if path == "repos/O/r"
                        else {"content": base64.b64encode(f"  revision: {head}\n".encode()).decode(), "sha": "x"})

    def fake_gh(*args, input_=None):
        calls.append(args)
        if args[:2] == ("pr", "list"):
            return json.dumps([{"number": 5, "headRefName": "play-nice/pin-" + head[:7], "mergeable": "MERGEABLE",
                                "mergeStateStatus": "CLEAN", "statusCheckRollup": [], "title": "x (pin robot)"}])
        return ""
    monkeypatch.setattr(ps, "gh", fake_gh)
    r = ps.sync_repo({"repo": "O/r", "manifest": "m.yaml"}, head, dry=False)
    assert r["status"] == "current" and [c for c in calls if c[:2] == ("pr", "close")]
    assert not [c for c in calls if c[:2] == ("pr", "merge")]
