"""playnice friction regression tests (Play-Nice v2 plan, step 1).

  7. `playnice status --repo <missing>` printed UNKNOWN and exited 0; now it
     errors with a next step and exits 2 (like `playnice work` already did).
  8. `work --json` / `reconcile --json` accepted --json and ignored it; now
     they emit one JSON object (state, permit path, handoff path) instead of
     the human prose. Prose output without --json is unchanged.

Fully offline: the authoritative remote is a local bare repo; GitHub is off.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
PLAYNICE = REPO / "tools" / "playnice" / "playnice.py"

git0 = lambda repo, *a: subprocess.run(  # noqa: E731
    ["git", "-C", str(repo), *a], capture_output=True, text=True, timeout=60
)


@pytest.fixture()
def lib(tmp_path):
    """A git-initialized copy of the library checkout (the contract source)."""
    target = tmp_path / "lib"
    shutil.copytree(
        REPO,
        target,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", ".venv", "__pycache__", ".pytest_cache", ".contract-commitments"
        ),
    )
    git0(target, "init", "-q", "-b", "main")
    git0(target, "config", "user.email", "test@example.invalid")
    git0(target, "config", "user.name", "Test")
    assert git0(target, "add", "-A").returncode == 0
    assert git0(target, "commit", "-qm", "baseline", "--no-gpg-sign").returncode == 0
    return target


def bare_clone(src, dest):
    r = subprocess.run(
        ["git", "clone", "--quiet", "--bare", str(src), str(dest)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, r.stderr
    return Path(dest)


@pytest.fixture()
def pn_remote(lib, tmp_path):
    return bare_clone(lib, tmp_path / "pn_remote.git")


def head(path) -> str:
    return git0(path, "rev-parse", "HEAD").stdout.strip()


def manifest_text(remote, sha) -> str:
    return (
        "schema: play-nice/adoption-v1\n"
        "source:\n"
        f"  repository: {remote}\n"
        f"  revision: {sha}\n"
        "always:\n"
        "  - truth-and-evidence\n"
        "  - explicit-state\n"
        "  - recovery-and-reversibility\n"
        "  - provenance-and-audit\n"
        "  - ask-for-help\n"
        "  - assume-unknown\n"
        "freshness:\n"
        "  policy: require-current\n"
        "  ref: main\n"
        "  update: review\n"
    )


def make_consumer(tmp_path, lib, pn_remote) -> Path:
    repo = tmp_path / "consumer"
    repo.mkdir()
    git0(repo, "init", "-q", "-b", "main")
    git0(repo, "config", "user.email", "test@example.invalid")
    git0(repo, "config", "user.name", "Test")
    (repo / "baseline.txt").write_text("baseline\n")
    git0(repo, "add", "baseline.txt")
    assert git0(repo, "commit", "-qm", "baseline", "--no-gpg-sign").returncode == 0
    m = repo / ".contracts" / "adoption.yaml"
    m.parent.mkdir(parents=True)
    m.write_text(manifest_text(pn_remote, head(lib)))
    git0(repo, "add", str(m))
    assert git0(repo, "commit", "-qm", "adoption", "--no-gpg-sign").returncode == 0
    bare_clone(repo, tmp_path / "consumer_remote.git")
    git0(repo, "remote", "add", "origin", str(tmp_path / "consumer_remote.git"))
    assert git0(repo, "fetch", "--quiet", "origin").returncode == 0
    assert git0(repo, "branch", "--set-upstream-to=origin/main", "main").returncode == 0
    return repo


def pn_env(tmp_path, lib) -> dict:
    return {
        **os.environ,
        "PLAY_NICE_LIBRARY": str(lib),
        "PLAY_NICE_CONFIG": str(tmp_path / "no-such-global.yaml"),
    }


def run_pn(args, env, cwd) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PLAYNICE), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd),
        timeout=180,
    )


# ------------------------------------------------------- 7. status: fail closed


def test_status_missing_repo_errors_and_exits_2(tmp_path, lib):
    env = pn_env(tmp_path, lib)
    r = run_pn(["status", "--repo", str(tmp_path / "does-not-exist")], env, tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "repo not found or not a git repository" in r.stderr
    assert "next:" in r.stderr


def test_status_non_git_directory_errors_and_exits_2(tmp_path, lib):
    plain = tmp_path / "plain-dir"
    plain.mkdir()
    env = pn_env(tmp_path, lib)
    r = run_pn(["status", "--repo", str(plain)], env, tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "not a git repository" in r.stderr


def test_status_real_repo_without_manifest_still_reports_unknown(tmp_path, lib):
    """Not a regression: a *reachable* repo with no manifest keeps the old
    read-only UNKNOWN answer (exit 0) — only an unopenable repo errors."""
    repo = tmp_path / "bare-repo"
    repo.mkdir()
    git0(repo, "init", "-q", "-b", "main")
    git0(repo, "config", "user.email", "test@example.invalid")
    git0(repo, "config", "user.name", "Test")
    (repo / "a.txt").write_text("x\n")
    git0(repo, "add", "a.txt")
    assert git0(repo, "commit", "-qm", "x", "--no-gpg-sign").returncode == 0
    env = pn_env(tmp_path, lib)
    r = run_pn(["status", "--repo", str(repo), "--no-github", "--json"], env, repo)
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data["play_nice"]["status"] == "UNKNOWN"


# ------------------------------------------------- 8. work/reconcile honour --json


def test_work_json_emits_machine_object_not_prose(tmp_path, lib, pn_remote):
    consumer = make_consumer(tmp_path, lib, pn_remote)
    env = pn_env(tmp_path, lib)
    r = run_pn(
        [
            "work",
            "--repo",
            str(consumer),
            "--no-launch",
            "--no-github",
            "--json",
            "update the onboarding checklist",
        ],
        env,
        consumer,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    # the pledge prose must be gone; stdout must be exactly one JSON object
    assert "CONTRACT OPERATIONAL COMMITMENT" not in r.stdout
    data = json.loads(r.stdout)
    assert data["command"] == "work"
    assert data["state"] == "PERMITTED"
    assert data["freshness"] == "CURRENT"
    permit_path = Path(data["permit_path"])
    assert permit_path.is_file()
    handoff_path = Path(data["handoff_path"])
    assert handoff_path.is_file()
    assert data["next"]


def test_work_json_without_manifest_reports_state(tmp_path, lib):
    env = pn_env(tmp_path, lib)
    r = run_pn(
        ["work", "--repo", str(tmp_path), "--no-github", "--json", "x"], env, tmp_path
    )
    assert r.returncode == 2
    data = json.loads(r.stdout)
    assert data["state"] == "NO_MANIFEST"
    assert data["permit_path"] is None


def test_reconcile_json_emits_machine_object(tmp_path, lib, pn_remote):
    consumer = make_consumer(tmp_path, lib, pn_remote)
    env = pn_env(tmp_path, lib)
    r = run_pn(
        ["reconcile", "--repo", str(consumer), "--no-github", "--json"], env, consumer
    )
    assert r.returncode == 4  # no ACTIVE permit yet: read-only, unchanged policy
    data = json.loads(r.stdout)
    assert data["command"] == "reconcile"
    assert data["state"] == "READ_ONLY"
    assert "permit_path" in data and "handoff_path" in data
    assert data["carryover"]


def test_reconcile_json_without_manifest_reports_state(tmp_path, lib):
    repo = tmp_path / "plain"
    repo.mkdir()
    git0(repo, "init", "-q", "-b", "main")
    env = pn_env(tmp_path, lib)
    r = run_pn(["reconcile", "--repo", str(repo), "--no-github", "--json"], env, repo)
    assert r.returncode == 2
    data = json.loads(r.stdout)
    assert data["state"] == "NO_MANIFEST"


def test_work_prose_without_json_is_unchanged(tmp_path, lib, pn_remote):
    consumer = make_consumer(tmp_path, lib, pn_remote)
    env = pn_env(tmp_path, lib)
    r = run_pn(
        ["work", "--repo", str(consumer), "--no-launch", "--no-github",
         "update the onboarding checklist"],
        env,
        consumer,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "PLAY NICE: CURRENT" in r.stdout
    assert "WORK PERMIT: ACTIVE" in r.stdout
