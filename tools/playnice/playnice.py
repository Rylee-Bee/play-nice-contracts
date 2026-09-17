#!/usr/bin/env python3
"""playnice — global agent-work entry point.

One command owns the whole lifecycle:

    playnice work "fix the settings page"

The wrapper: refreshes truth -> reconciles old work -> loads Play Nice ->
launches the agent -> verifies and cleans up afterward. If something
genuinely needs a human, it says so; otherwise it finishes the lifecycle
itself and ends with a durable handoff.

`contractctl` (tools/contractctl in the Play Nice library) remains the
lower-level engine; this tool is the orchestration layer on top of it.

Deterministic machinery: every state transition is computed from Git /
contract state / gh JSON. UNKNOWN stays UNKNOWN (fail closed). No test
depends on live GitHub — tests substitute local bare repositories for the
authoritative remote and a fake `gh` binary.

Exit codes:
  0  success (work finished or nothing required)
  1  usage / internal error
  2  fail-closed gate (freshness / gate / permit blocked)
  3  agent exited nonzero
  4  needs human help (WAITING_FOR_HELP / BLOCKED)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PLAYNICE_VERSION = "0.1.0"

# ----------------------------------------------------------------- config

DEFAULT_CONFIG_PATHS = (
    Path(os.environ.get("PLAY_NICE_CONFIG", ""))
    if os.environ.get("PLAY_NICE_CONFIG")
    else Path.home() / ".config" / "play-nice" / "global.yaml"
)

CACHE_DIR = (
    Path(os.environ["PLAY_NICE_CACHE"])
    if os.environ.get("PLAY_NICE_CACHE")
    else Path.home() / ".cache" / "play-nice"
)
LIBRARY_CACHE = CACHE_DIR / "contracts"

KNOWN_CONFIG_KEYS = {
    "play_nice": {"repository", "ref", "freshness"},
    "repositories": {
        "fetch_before_work",
        "prune_remotes",
        "inspect_previous_work",
        "reconcile_before_new_work",
    },
    "github": {
        "inspect_pull_requests",
        "inspect_issues",
        "inspect_ci",
        "merge_ready_pull_requests",
        "close_proven_resolved_issues",
        "remove_proven_merged_branches",
        "merge_method",
        "bin",
    },
    "safety": {
        "unknown_fails_closed",
        "respect_branch_protection",
        "respect_required_reviews",
        "respect_authorization",
        "never_force_push_by_default",
    },
    "handoff": {"required", "path"},
    "agent": {"command", "args"},
    "post": {"verify_command", "create_pull_request", "push", "timeout_minutes"},
}

FRESHNESS_POLICIES = ("pinned", "require-current")
GH_MERGE_METHODS = ("merge", "squash", "rebase")

DISPOSITIONS = (
    "DONE",
    "MERGED",
    "CLOSED",
    "STILL_ACTIVE",
    "DEFERRED",
    "WAITING_FOR_HELP",
    "UNKNOWN",
    "BLOCKED",
)


def default_config() -> dict:
    return {
        "play_nice": {
            "repository": "Rylee-Bee/play-nice-contracts",
            "ref": "main",
            "freshness": "pinned",  # the global floor; manifests may raise
        },
        "repositories": {
            "fetch_before_work": True,
            "prune_remotes": True,
            "inspect_previous_work": True,
            "reconcile_before_new_work": True,
        },
        "github": {
            "inspect_pull_requests": True,
            "inspect_issues": True,
            "inspect_ci": True,
            "merge_ready_pull_requests": False,  # explicit opt-in
            "close_proven_resolved_issues": False,  # explicit opt-in
            "remove_proven_merged_branches": False,  # explicit opt-in
            "merge_method": "merge",
            "bin": "gh",
        },
        "safety": {
            "unknown_fails_closed": True,
            "respect_branch_protection": True,
            "respect_required_reviews": True,
            "respect_authorization": True,
            "never_force_push_by_default": True,
        },
        "handoff": {
            "required": True,
            "path": "",
        },
        "agent": {
            "command": "opencode",
            "args": ["run"],
        },
        "post": {
            "verify_command": "",
            "create_pull_request": False,
            "push": False,
            "timeout_minutes": 0,
        },
    }


def _merge_deep(base: dict, override: dict, where: str) -> dict:
    out = dict(base)
    for k, v in override.items():
        if k not in base and k not in KNOWN_CONFIG_KEYS.get(where, set()):
            raise ConfigError(
                f"unknown key '{where}.{k}' in global config "
                f"(known: {sorted(KNOWN_CONFIG_KEYS.get(where, set()))})"
            )
        if isinstance(v, dict):
            if not isinstance(base.get(k), dict):
                raise ConfigError(f"config key '{where}.{k}' must be a mapping")
            out[k] = _merge_deep(base[k], v, f"{where}.{k}")
        else:
            out[k] = v
    return out


class ConfigError(Exception):
    pass


def load_global_config(path: Path | None = None) -> dict:
    cfg = default_config()
    p = path or DEFAULT_CONFIG_PATHS
    if not p.exists():
        return cfg
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        raise ConfigError(f"cannot read global config {p}: {e}")
    import re as _re

    body = text
    m = _re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, _re.DOTALL)
    if m:
        body = m.group(1)
    data = _parse_yaml_simple(body, where="<global config>")
    if not isinstance(data, dict):
        raise ConfigError(f"global config {p} must be a mapping")
    out = _merge_deep(cfg, data, "")
    _validate_config(out)
    return out


def _validate_config(cfg: dict) -> None:
    """Enum/type validation. Unknown values fail loudly, never reinterpreted."""
    freshness = cfg["play_nice"]["freshness"]
    if freshness not in FRESHNESS_POLICIES:
        raise ConfigError(
            f"play_nice.freshness must be one of {FRESHNESS_POLICIES}, got {freshness!r}"
        )
    method = cfg["github"]["merge_method"]
    if method not in GH_MERGE_METHODS:
        raise ConfigError(
            f"github.merge_method must be one of {GH_MERGE_METHODS}, got {method!r}"
        )
    agent_cmd = cfg["agent"]["command"]
    if not isinstance(agent_cmd, str) or not agent_cmd.strip():
        raise ConfigError("agent.command must be a non-empty command name")
    if not isinstance(cfg["agent"]["args"], list) or not all(
        isinstance(a, str) for a in cfg["agent"]["args"]
    ):
        raise ConfigError("agent.args must be a list of strings")
    to = cfg["post"]["timeout_minutes"]
    if not isinstance(to, int) or to < 0:
        raise ConfigError("post.timeout_minutes must be a non-negative integer")
    if not isinstance(cfg["handoff"]["path"], str):
        raise ConfigError("handoff.path must be a string")
    non_bool_keys = {"merge_method", "bin", "path", "verify_command", "timeout_minutes"}
    for section in ("github", "safety", "repositories", "handoff", "post"):
        for k, v in cfg[section].items():
            if k == "timeout_minutes":
                if not isinstance(v, int):
                    raise ConfigError(f"{section}.{k} must be an integer")
                continue
            if k in non_bool_keys:
                continue
            if not isinstance(v, bool):
                raise ConfigError(f"{section}.{k} must be a boolean, got {v!r}")


def _parse_yaml_simple(text: str, where: str) -> dict:
    """Minimal deterministic YAML-subset parser (nested mappings + scalar lists).

    The project's own parser lives in contractctl; this tool touches only the
    small YAML shapes used by play-nice config. Anything not understood fails
    loudly instead of being silently reinterpreted.
    """
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.strip() in ("---", "..."):
            continue
        content = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        lines.append((indent, content))
    if not lines:
        return {}

    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]  # (indent, mapping frame)
    i = 0
    while i < len(lines):
        indent, content = lines[i]
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if content.startswith("- "):
            # scalar list item attached to the nearest open list key
            holder = _find_list_holder(stack, indent)
            if holder is None:
                raise ConfigError(f"{where}:{i + 1}: list item outside a list key")
            holder.append(_coerce(content[2:].strip()))
            i += 1
            continue

        if ":" not in content:
            raise ConfigError(
                f"{where}:{i + 1}: expected 'key: value', got {content!r}"
            )
        key, val = _split_scalar(content, where, i)
        if val == "":
            # lookahead: `- ` deeper -> list; otherwise nested mapping
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            if nxt is not None and nxt[0] > indent and nxt[1].startswith("- "):
                lst: list = []
                parent[key] = lst
                stack.append((indent, {"_LIST_@": lst}))
                i += 1
                continue
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
            i += 1
            continue
        parent[key] = _coerce(val)
        i += 1
    _drop_placeholder(root)
    return root


def _find_list_holder(stack: list, indent: int) -> list | None:
    for f_indent, frame in reversed(stack):
        if f_indent < indent:
            lst = frame.get("_LIST_@")
            if lst is not None:
                return lst
    return None


def _drop_placeholder(node):
    if isinstance(node, dict):
        for k, v in list(node.items()):
            if k == "_LIST_@":
                del node[k]
            else:
                _drop_placeholder(v)
    elif isinstance(node, list):
        for v in node:
            _drop_placeholder(v)


def _split_scalar(content: str, where: str, lineno: int) -> tuple[str, str]:
    idx = content.find(":")
    key = content[:idx].strip()
    val = content[idx + 1 :].strip()
    if not key:
        raise ConfigError(f"{where}:{lineno + 1}: empty key")
    return key, val


def _coerce(val: str):
    v = val.strip()
    if not v:
        return ""
    if v.startswith('"') and v.endswith('"') and len(v) >= 2:
        return v[1:-1]
    if v.startswith("'") and v.endswith("'") and len(v) >= 2:
        return v[1:-1]
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if v in ("null", "None", "~"):
        return None
    if v.startswith("[") and v.endswith("]"):
        body = v[1:-1].strip()
        if not body:
            return []
        return [_coerce(part.strip()) for part in body.split(",")]
    if re.fullmatch(r"-?\d+", v):
        try:
            return int(v)
        except ValueError:
            pass
    return v


# ----------------------------------------------------------------- library


def find_library(config: dict, cwd: Path, env: dict | None = None) -> Path:
    """Locate the canonical Play Nice library checkout (holds contractctl)."""
    env = env or os.environ
    override = env.get("PLAY_NICE_LIBRARY")
    if override:
        p = Path(override).resolve()
        if not (p / "tools" / "contractctl" / "contractctl.py").is_file():
            raise PlayNiceError(
                f"PLAY_NICE_LIBRARY={p} is not a play-nice-contracts checkout "
                "(tools/contractctl/contractctl.py missing)"
            )
        return p
    # running inside a checkout of the library itself?
    probe = cwd
    for up in [cwd, *cwd.parents]:
        if (up / "contracts").is_dir() and (
            up / "tools" / "contractctl" / "contractctl.py"
        ).is_file():
            return up
    # managed cache clone
    target = LIBRARY_CACHE
    ct = target / "tools" / "contractctl" / "contractctl.py"
    if not ct.is_file():
        if not shutil.which("git"):
            raise PlayNiceError(
                "git not found; cannot bootstrap the Play Nice library cache"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        repo = config["play_nice"]["repository"]
        r = subprocess.run(
            ["git", "clone", "--quiet", _remote_url(repo), str(target)],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if r.returncode != 0:
            raise PlayNiceError(
                f"cannot clone Play Nice library {repo}: {r.stderr.strip() or 'unknown error'}"
            )
    if config["repositories"]["fetch_before_work"]:
        ref = config["play_nice"]["ref"]
        r = subprocess.run(
            ["git", "-C", str(target), "fetch", "--quiet", "origin", ref],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode != 0 and not ct.is_file():
            raise PlayNiceError(f"cannot fetch Play Nice library: {r.stderr.strip()}")
    return target


def _remote_url(repository: str) -> str:
    if repository.startswith(("/", "./", "../", "~")) or Path(repository).exists():
        return str(Path(repository).expanduser().resolve())
    if "://" in repository:
        return repository
    if "@" in repository and ":" in repository:
        return repository
    # owner/repo shorthand
    owner, _, name = repository.partition("/")
    if not owner or not name:
        raise PlayNiceError(f"cannot interpret repository {repository!r}")
    return f"https://github.com/{owner}/{name}.git"


def import_contractctl(lib: Path):
    """Import the contractctl engine from the canonical library checkout."""
    import importlib.util

    path = lib / "tools" / "contractctl" / "contractctl.py"
    spec = importlib.util.spec_from_file_location("contractctl", path)
    if spec is None or spec.loader is None:
        raise PlayNiceError(f"cannot import contractctl from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["contractctl"] = mod
    spec.loader.exec_module(mod)
    return mod


class PlayNiceError(Exception):
    pass


# ----------------------------------------------------------------- git helpers


def git(
    repo: Path, *args: str, check: bool = True, timeout: int = 120
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=check,
    )


def git0(repo: Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return git(repo, *args, check=False, timeout=timeout)


def is_git_repo(path: Path) -> bool:
    return git0(path, "rev-parse", "--is-inside-work-tree").returncode == 0


# ----------------------------------------------------------------- repo state


def collect_repo_state(repo: Path, cfg: dict) -> dict:
    """Phase 2 — repository freshness: fetch, prune, classify. Never destroys work."""
    out = {
        "root": str(repo),
        "branch": None,
        "head": None,
        "upstream": None,
        "dirty": False,
        "dirty_files": [],
        "status": "UNKNOWN",
        "detail": "",
        "remotes": [],
        "default_branch": None,
        "fetched": False,
        "pruned": False,
        "worktrees": [],
    }
    if not is_git_repo(repo):
        out["detail"] = f"not a git repository: {repo}"
        return out
    r = git0(repo, "rev-parse", "--abbrev-ref", "HEAD")
    out["branch"] = r.stdout.strip() if r.returncode == 0 else "HEAD"
    r = git0(repo, "rev-parse", "HEAD")
    out["head"] = r.stdout.strip() if r.returncode == 0 else None
    r = git0(repo, "status", "--porcelain=v1", "--branch")
    out["status_raw"] = r.stdout
    dirty = [ln for ln in r.stdout.splitlines() if ln and not ln.startswith("##")]
    out["dirty"] = bool(dirty)
    out["dirty_files"] = dirty
    for ln in r.stdout.splitlines():
        if ln.startswith("## "):
            rest = ln[3:]
            if "..." in rest:
                branch, upstream = rest.split("...", 1)
                out["branch"] = branch or out["branch"]
                up = upstream.split(" ")[0]
                out["upstream"] = up
    r = git0(repo, "remote")
    out["remotes"] = r.stdout.split()
    # default branch from origin/HEAD
    r = git0(repo, "symbolic-ref", "refs/remotes/origin/HEAD")
    if r.returncode == 0:
        m = re.match(r"refs/remotes/origin/(.+)", r.stdout.strip())
        out["default_branch"] = m.group(1) if m else None
    if not out["default_branch"]:
        out["default_branch"] = "main"
    wt_list = [
        ln.split()[1]
        for ln in git0(repo, "worktree", "list", "--porcelain").stdout.splitlines()
        if ln.startswith("worktree ")
    ]
    out["worktrees"] = [w for w in wt_list if Path(w).resolve() != repo.resolve()]
    r = git0(repo, "ls-remote", "--symref", "origin", "HEAD")
    if r.returncode == 0:
        m = re.search(r"ref: refs/heads/(\S+)\s+HEAD", r.stdout)
        if m:
            out["default_branch"] = m.group(1)

    if cfg["repositories"]["fetch_before_work"] and out["remotes"]:
        fetch_args = ["fetch", "--quiet"]
        if cfg["repositories"]["prune_remotes"]:
            fetch_args.append("--prune")
        fetch_args.append("origin")
        fr = git0(repo, *fetch_args, timeout=300)
        out["fetched"] = fr.returncode == 0
        out["detail"] = (
            "" if fr.returncode == 0 else f"fetch failed: {fr.stderr.strip()[:200]}"
        )
        if cfg["repositories"]["prune_remotes"] and fr.returncode == 0:
            out["pruned"] = True

    # ahead/behind vs upstream
    if out["upstream"]:
        r = git0(
            repo, "rev-list", "--left-right", "--count", f"HEAD...{out['upstream']}"
        )
        if r.returncode == 0:
            left, _, right = r.stdout.strip().partition("\t")
            out["ahead"] = int(left)
            out["behind"] = int(right)
        r = git0(repo, "merge-base", "--is-ancestor", out["upstream"], "HEAD")
        out["upstream_in_head"] = r.returncode == 0

    out["status"] = classify_repo(out)
    return out


def classify_repo(s: dict) -> str:
    if not s.get("head"):
        return "EMPTY_OR_UNKNOWN"
    if s.get("dirty"):
        return "DIRTY"
    if s.get("upstream") is None:
        return "NO_UPSTREAM" if s.get("remotes") else "NO_REMOTE"
    ahead = s.get("ahead", 0)
    behind = s.get("behind", 0)
    if ahead == 0 and behind == 0:
        return "CURRENT"
    if ahead > 0 and behind == 0:
        return "AHEAD"
    if ahead == 0 and behind > 0:
        return "BEHIND"
    return "DIVERGED"


def reconcile_repo(repo: Path, cfg: dict) -> dict:
    """Deterministic reconcile: fetch (above) + fast-forward ONLY when clean."""
    s = collect_repo_state(repo, cfg)
    if s["status"] == "BEHIND" and cfg["repositories"]["reconcile_before_new_work"]:
        if s.get("branch") and s.get("branch") != "HEAD" and s.get("upstream"):
            if s["branch"] == "main" or s["default_branch"] == s["branch"]:
                r = git0(repo, "merge", "--ff-only", s["upstream"], timeout=300)
                if r.returncode == 0:
                    s["reconciled"] = True
                    s["status"] = "CURRENT"
                    s["detail"] = "fast-forwarded to upstream"
                else:
                    s["detail"] = f"ff-only failed: {r.stderr.strip()[:200]}"
    return s


# ------------------------------------------------------------- freshness


def find_adoption_manifest(repo: Path, explicit: str | None = None) -> Path | None:
    if explicit:
        p = Path(explicit)
        if not p.is_absolute():
            p = repo / p
        return p if p.is_file() else None
    candidates = [
        ".contracts/adoption.yaml",
        ".project/contracts/adoption.yaml",
        ".contracts/adoption.yml",
        ".project/contracts/adoption.yml",
    ]
    for rel in candidates:
        p = repo / rel
        if p.is_file():
            return p
    return None


def play_nice_check(manifest_path: Path, lib: Path, global_cfg: dict) -> dict:
    """Phase 1 — establish the authoritative remote revision (fail closed)."""
    cc = import_contractctl(lib)
    manifest = cc.load_adoption(manifest_path)
    result = cc.check_freshness(manifest_path)
    mf = manifest.get("freshness") or {}
    manifest_requires = mf.get("policy", "pinned") == "require-current"
    global_requires = global_cfg["play_nice"]["freshness"] == "require-current"
    enforced = manifest_requires or global_requires
    out = dict(result)
    out["enforced"] = enforced
    out["manifest_policy"] = mf.get("policy", "pinned")
    out["manifest_update"] = mf.get("update", "review")
    out["global_requires"] = global_requires
    if global_requires and not manifest_requires:
        out["detail"] = out.get("detail", "") + (
            "; global floor requires current contracts"
            if out["detail"]
            else "global floor requires current contracts"
        )
    return out


def freshness_blocked(fr: dict) -> bool:
    """Returns True when the freshness state must fail closed under enforcement."""
    if not fr.get("enforced"):
        return False
    return fr["status"] != "CURRENT"


def sync_pin_if_allowed(manifest_path: Path, fr: dict, lib: Path) -> dict:
    """Refresh the adoption pin per the manifest's update policy (never pinned)."""
    if fr.get("status") not in ("BEHIND", "DIVERGED"):
        return {"performed": False, "detail": "freshness is current; nothing to sync"}
    if not fr.get("remote_revision"):
        return {"performed": False, "detail": "no remote revision to sync to"}
    if (
        fr.get("manifest_update") != "automatic"
        or fr.get("manifest_policy") != "require-current"
    ):
        return {
            "performed": False,
            "detail": "update policy requires explicit review (never silently adopt)",
        }
    cc_path = lib / "tools" / "contractctl" / "contractctl.py"
    r = subprocess.run(
        [sys.executable, str(cc_path), "sync", "--manifest", str(manifest_path)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if r.returncode != 0:
        return {"performed": False, "detail": r.stderr.strip() or r.stdout.strip()}
    return {
        "performed": True,
        "detail": "pin refreshed to authoritative remote revision",
    }


# ------------------------------------------------------------- carryover

HANDOFF_PATTERNS = (
    "HANDOFF*.md",
    "*.handoff.md",
    "HANDOFF.md",
    "STATE.md",
    "CURRENT.md",
)


def discover_carryover(repo: Path, cfg: dict, gh: dict | None) -> dict:
    """Phase 3 — discover what previous work left behind; classify it."""
    items: list[dict] = []
    if cfg["repositories"]["inspect_previous_work"]:
        for sub in (".agent", ".project", ".contracts", "."):
            base = repo / sub
            if not base.is_dir():
                continue
            for pattern in HANDOFF_PATTERNS:
                for f in sorted(base.glob(pattern)):
                    if f.is_file():
                        items.append(_handoff_item(f, repo))
        sessions = repo / ".contracts" / "sessions"
        if sessions.is_dir():
            for f in sorted(sessions.glob("*.json")):
                items.append(_session_item(f))

    # branches (local), excluding current + the default branch
    st = collect_repo_state(repo, cfg)
    branch = st.get("branch")
    default = st.get("default_branch", "main")
    br = git0(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    for b in br.stdout.split():
        if b in (branch, default):
            continue
        r = git0(
            repo,
            "merge-base",
            "--is-ancestor",
            b,
            f"origin/{default}" if default else "HEAD",
        )
        merged = r.returncode == 0
        items.append(
            {
                "kind": "branch",
                "label": f"branch:{b}",
                "detail": f"merged into {default}"
                if merged
                else "not merged into default",
                "disposition": "MERGED" if merged else "UNKNOWN",
                "action": "delete-if-proven-no-longer-needed" if merged else "preserve",
                "evidence": f"merge-base --is-ancestor {b} origin/{default}"
                if merged
                else "no merge proof",
            }
        )
    # worktrees
    for wt in st.get("worktrees", []):
        items.append(
            {
                "kind": "worktree",
                "label": f"worktree:{wt}",
                "detail": "linked worktree",
                "disposition": "STILL_ACTIVE",
                "action": "preserve",
                "evidence": "git worktree list",
            }
        )
    # PRs / issues via gh (inspection only)
    if gh is not None and cfg["github"]["inspect_pull_requests"]:
        for pr in gh.get("prs", []):
            items.append(_pr_item(pr, cfg))
    if gh is not None and cfg["github"]["inspect_issues"]:
        for iss in gh.get("issues", []):
            items.append(_issue_item(iss))
    return {"items": items, "state": carryover_state(items)}


def _handoff_item(f: Path, repo: Path) -> dict:
    text = ""
    try:
        text = f.read_text(encoding="utf-8", errors="replace")
    except OSError:
        pass
    m = re.search(r"(?m)^NEXT:\s*(.+)$", text)
    next_line = m.group(1).strip() if m else None
    disp = "DONE"
    if next_line and next_line.lower() not in ("nothing required", "none", "n/a"):
        disp = "UNKNOWN"
        low = next_line.lower()
        if "waiting_for_help" in low or "needs help" in low or "help" in low:
            disp = "WAITING_FOR_HELP"
        elif "defer" in low:
            disp = "DEFERRED"
        elif "blocked" in low or "block" in low:
            disp = "BLOCKED"
    try:
        label = f"handoff:{f.relative_to(repo)}"
    except ValueError:
        label = f"handoff:{f.name}"
    return {
        "kind": "handoff",
        "label": label,
        "detail": f"NEXT: {next_line}" if next_line else "no NEXT line",
        "disposition": disp,
        "action": "read-and-continue"
        if disp in ("UNKNOWN", "STILL_ACTIVE", "WAITING_FOR_HELP", "BLOCKED")
        else "none",
        "evidence": str(f),
    }


def _session_item(f: Path) -> dict:
    data = {}
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    stat = data.get("commitment")
    task = data.get("task", "")
    disp = {"ACTIVE": "STILL_ACTIVE", "STALE": "UNKNOWN", "INACTIVE": "DEFERRED"}.get(
        str(stat), "UNKNOWN"
    )
    return {
        "kind": "commitment",
        "label": f"commitment:{f.name}",
        "detail": f"task={task!r} state={stat}",
        "disposition": disp,
        "action": "revalidate" if disp != "DEFERRED" else "none",
        "evidence": str(f),
    }


def _pr_item(pr: dict, cfg: dict) -> dict:
    n = pr.get("number")
    ready = _pr_ready(pr, cfg)
    if ready is True:
        disp = "STILL_ACTIVE"
        action = "merge-when-permit-active"
    elif ready is False and _pr_hard_block(pr):
        disp = "BLOCKED"
        action = "resolve-or-defer"
    elif ready is False:
        disp = "WAITING_FOR_HELP"
        action = "await-checks-or-review"
    else:
        disp = "UNKNOWN"
        action = "preserve"
    return {
        "kind": "pr",
        "label": f"pr:{n}",
        "detail": f"{pr.get('title', '')[:80]} [{pr.get('headRefName', '')}]",
        "disposition": disp,
        "action": action,
        "evidence": json.dumps(_pr_ready_fields(pr), sort_keys=True),
    }


def _issue_item(iss: dict) -> dict:
    n = iss.get("number")
    resolved = iss.get("_resolved_by", None)
    if resolved:
        disp = "CLOSED"
        action = "close-with-provenance"
    else:
        disp = "STILL_ACTIVE"
        action = "leave-open"
    return {
        "kind": "issue",
        "label": f"issue:{n}",
        "detail": iss.get("title", "")[:80],
        "disposition": disp,
        "action": action,
        "evidence": f"merged PR #{resolved} references close"
        if resolved
        else "no resolution proof",
    }


def carryover_state(items: list[dict]) -> str:
    if not items:
        return "RECONCILED"
    if any(i.get("disposition") == "UNKNOWN" for i in items):
        return "PARTIAL"
    return "RECONCILED"


# ------------------------------------------------------------- github layer


def gh_bin(cfg: dict, env: dict | None = None) -> str | None:
    env = env or os.environ
    if env.get("PLAY_NICE_GH"):
        return env["PLAY_NICE_GH"]
    if cfg["github"]["bin"] != "gh":
        return cfg["github"]["bin"]
    return shutil.which("gh")


def repo_identity(repo: Path) -> str | None:
    r = git0(repo, "remote", "get-url", "origin")
    url = r.stdout.strip() if r.returncode == 0 else ""
    m = re.search(
        r"(?:github\.com[/:]|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?$", url
    )
    if m:
        return f"{m.group(1)}/{m.group(2)}"
    m = re.match(r"([\w.-]+/[\w.-]+?)(?:\.git)?$", url)
    if m and "/" in url:
        return m.group(1)
    return None


def gh_query(
    bin_path: str, repo: Path, args: list[str], timeout: int = 60
) -> subprocess.CompletedProcess:
    ident = repo_identity(repo)
    cmd = [bin_path]
    if ident:
        cmd += ["-R", ident]
    cmd += args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def gh_json(bin_path: str, repo: Path, args: list[str]) -> list | dict | None:
    r = gh_query(bin_path, repo, args)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def collect_github_state(repo: Path, cfg: dict, env: dict | None = None) -> dict:
    """Read-only GitHub inspection: PRs, issues, per-PR CI. UNKNOWN on failure."""
    bin_path = gh_bin(cfg, env)
    out = {"available": bool(bin_path), "prs": [], "issues": [], "note": ""}
    if not bin_path:
        out["note"] = (
            "gh not available; GitHub state UNKNOWN (fail closed for mutations)"
        )
        return out
    try:
        if cfg["github"]["inspect_pull_requests"]:
            prs = gh_json(
                bin_path,
                repo,
                [
                    "pr",
                    "list",
                    "--state",
                    "open",
                    "--json",
                    "number,title,headRefName,baseRefName,isDraft,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,url",
                ],
            )
            if prs is None:
                out["note"] += "pr list UNKNOWN; "
            else:
                for pr in prs:
                    out["prs"].append(_enrich_pr(bin_path, repo, pr, cfg))
        if cfg["github"]["inspect_issues"]:
            issues = gh_json(
                bin_path,
                repo,
                ["issue", "list", "--state", "open", "--json", "number,title,url"],
            )
            if issues is None:
                out["note"] += "issue list UNKNOWN; "
            else:
                for i in issues:
                    i["_resolved_by"] = _issue_resolved_by(bin_path, repo, i["number"])
                out["issues"] = issues
        if out["note"]:
            out["available"] = False
    except (OSError, subprocess.TimeoutExpired) as e:
        out["available"] = False
        out["note"] = f"github inspection failed: {e}"
    return out


def _enrich_pr(bin_path: str, repo: Path, pr: dict, cfg: dict) -> dict:
    """Attach the deterministic readiness evidence for one PR."""
    n = pr.get("number")
    out = dict(pr)
    out["_ready"] = _pr_ready(pr, cfg)
    checks = pr.get("statusCheckRollup") or []
    failures = [
        c.get("name")
        for c in checks
        if c.get("conclusion") in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT")
    ]
    pending = [
        c.get("name")
        for c in checks
        if c.get("status") in ("IN_PROGRESS", "QUEUED", "PENDING")
        or (c.get("conclusion") in (None, "PENDING"))
    ]
    out["_failing_checks"] = failures
    out["_pending_checks"] = pending
    return out


def _pr_ready_fields(pr: dict) -> dict:
    return {
        "draft": pr.get("isDraft"),
        "mergeable": pr.get("mergeable"),
        "mergeStateStatus": pr.get("mergeStateStatus"),
        "reviewDecision": pr.get("reviewDecision"),
        "failing": (pr.get("_failing_checks") or [])
        if "_failing_checks" in pr
        else [
            c.get("name")
            for c in (pr.get("statusCheckRollup") or [])
            if c.get("conclusion") in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT")
        ],
    }


def _pr_hard_block(pr: dict) -> bool:
    return (
        bool(pr.get("_failing_checks") or pr.get("_pending_checks"))
        or pr.get("mergeable") == "CONFLICTING"
        or pr.get("mergeStateStatus") in ("BLOCKED", "BEHIND")
    )


def _pr_ready(pr: dict, cfg: dict) -> bool:
    """Objective readiness only — never 'probably okay'."""
    if pr.get("isDraft"):
        return False
    if pr.get("mergeable") not in ("MERGEABLE", True):
        return False
    if pr.get("mergeStateStatus") not in ("CLEAN", "UNSTABLE", None):
        # BEHIND / BLOCKED / DIRTY / DRAFT / HAS_HOOKS / UNKNOWN -> not ready
        return False
    if pr.get("statusCheckRollup") is not None:
        for c in pr.get("statusCheckRollup") or []:
            if c.get("conclusion") in ("FAILURE", "ERROR", "CANCELLED", "TIMED_OUT"):
                return False
            if c.get("status") in ("IN_PROGRESS", "QUEUED", "PENDING"):
                return False
    if (
        cfg["safety"]["respect_required_reviews"]
        or cfg["github"]["merge_ready_pull_requests"]
    ):
        if pr.get("reviewDecision") == "REVIEW_REQUIRED":
            return False
    return True


def _issue_resolved_by(bin_path: str, repo: Path, number: int) -> int | None:
    """Proven resolution: a merged PR whose head/body references 'close/fix #number'."""
    prs = gh_json(
        bin_path,
        repo,
        ["pr", "list", "--state", "merged", "--json", "number,body,title"],
    )
    if prs is None:
        return None
    pat = re.compile(rf"(?im)(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#{number}\b")
    for pr in prs:
        body = (pr.get("body") or "") + " " + (pr.get("title") or "")
        if pat.search(body):
            return pr.get("number")
    return None


# ------------------------------------------------------------- auto-finish


def reconcile_github(
    repo: Path, cfg: dict, permit: dict, gh: dict, env: dict | None = None
) -> list[dict]:
    """Phases 4–6 — merge ready PRs / close proven issues / prune merged branches.

    Runs ONLY under an ACTIVE work permit AND explicit config grants.
    """
    ops: list[dict] = []
    bin_path = gh_bin(cfg, env)
    if not permit or permit.get("work_permit") != "ACTIVE":
        return [{"op": "skip", "detail": "no ACTIVE work permit; mutation blocked"}]
    if not bin_path:
        return [
            {
                "op": "skip",
                "detail": "gh unavailable; remote state UNKNOWN (fail closed)",
            }
        ]
    if cfg["github"]["merge_ready_pull_requests"]:
        for pr in sorted(gh.get("prs", []), key=lambda p: p.get("number") or 0):
            n = pr.get("number")
            if pr.get("_ready") is True:
                method = cfg["github"]["merge_method"]
                r = gh_query(
                    bin_path, repo, ["pr", "merge", str(n), f"--{method}"], timeout=120
                )
                ops.append(
                    {
                        "op": "merged" if r.returncode == 0 else "merge-failed",
                        "target": f"pr:{n}",
                        "detail": r.stdout.strip()
                        or r.stderr.strip()
                        or f"gh pr merge {n} --{method}",
                    }
                )
            else:
                ops.append(
                    {
                        "op": "skip",
                        "target": f"pr:{n}",
                        "detail": _skip_reason(pr),
                    }
                )
    if cfg["github"]["close_proven_resolved_issues"]:
        for iss in gh.get("issues", []):
            n = iss.get("number")
            by = iss.get("_resolved_by")
            if by:
                r = gh_query(
                    bin_path,
                    repo,
                    [
                        "issue",
                        "close",
                        str(n),
                        "--comment",
                        f"closed by merged PR #{by} (playnice automated reconcile; provenance)",
                    ],
                    timeout=120,
                )
                ops.append(
                    {
                        "op": "closed" if r.returncode == 0 else "close-failed",
                        "target": f"issue:{n}",
                        "detail": f"resolved by merged PR #{by}",
                    }
                )
            else:
                ops.append(
                    {
                        "op": "keep",
                        "target": f"issue:{n}",
                        "detail": "no resolution proof",
                    }
                )
    if cfg["github"]["remove_proven_merged_branches"]:
        ops += _prune_branches(repo, cfg, gh, bin_path)
    return ops


def _skip_reason(pr: dict) -> str:
    if pr.get("isDraft"):
        return "draft"
    if pr.get("mergeable") == "CONFLICTING":
        return "conflicts"
    if pr.get("_failing_checks") or pr.get("_pending_checks"):
        return "checks not green"
    if pr.get("reviewDecision") == "REVIEW_REQUIRED":
        return "review required"
    if pr.get("mergeStateStatus") not in ("CLEAN", "UNSTABLE", None):
        return f"mergeStateStatus={pr.get('mergeStateStatus')}"
    return "not objectively ready"


def _prune_branches(repo: Path, cfg: dict, gh: dict, bin_path: str) -> list[dict]:
    ops: list[dict] = []
    st = collect_repo_state(repo, cfg)
    default = st.get("default_branch", "main")
    cur = st.get("branch")
    wt_paths = set(st.get("worktrees", []))
    # head branches of open PRs
    open_heads = {str(p.get("headRefName")) for p in gh.get("prs", [])}
    merged_heads = {
        str(p.get("headRefName")) for p in gh.get("prs", []) if p.get("mergedAt")
    }
    br = git0(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    for b in br.stdout.split():
        if b in (cur, default, "HEAD"):
            continue
        r = git0(
            repo,
            "merge-base",
            "--is-ancestor",
            b,
            f"origin/{default}" if True else default,
        )
        merged_local = r.returncode == 0
        if b in open_heads:
            continue
        if b in wt_paths:
            continue
        if not merged_local:
            ops.append(
                {
                    "op": "keep",
                    "target": f"branch:{b}",
                    "detail": "not merged (preserved)",
                }
            )
            continue
        if (
            "origin/" + b
            in git0(
                repo, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"
            ).stdout.split()
        ):
            r = git0(repo, "push", "origin", "--delete", b, timeout=120)
            if r.returncode == 0:
                ops.append(
                    {
                        "op": "deleted-remote",
                        "target": f"branch:{b}",
                        "detail": "merged into default",
                    }
                )
            else:
                ops.append(
                    {
                        "op": "delete-failed",
                        "target": f"branch:{b}",
                        "detail": r.stderr.strip()[:120],
                    }
                )
        r = git0(repo, "branch", "-d", b)
        if r.returncode == 0:
            ops.append(
                {
                    "op": "deleted-local",
                    "target": f"branch:{b}",
                    "detail": "merged into default",
                }
            )
        else:
            ops.append(
                {
                    "op": "keep",
                    "target": f"branch:{b}",
                    "detail": f"refused: {r.stderr.strip()[:120]}",
                }
            )
    return ops


# ------------------------------------------------------------- contract gate


def generate_impact(manifest_path: Path, task: str, lib: Path) -> dict[str, str]:
    """Deterministic task-impact acknowledgements for the resolved set.

    The orchestrator's commitment is a machine-checkable permit: for every
    selected contract it generates one explicit acknowledgement from the
    contract's own statement of what it governs, scoped to this task. The
    executing agent performs its OWN task-specific attestation as a worker
    (inheritance enforced by contractctl) — this floor is never a substitute.
    """
    cc = import_contractctl(lib)
    manifest = cc.load_adoption(manifest_path)
    res = cc.resolve_set(manifest, task)
    if res["errors"]:
        raise PlayNiceError(
            "commitment: resolution errors:\n  " + "\n  ".join(res["errors"])
        )
    by_id = {c["front_matter"]["contract_id"]: c for c in cc.load_library()}
    snippet = " ".join(task.split())[:120]
    impact: dict[str, str] = {}
    for cid, why in sorted(res["selected"].items()):
        c = by_id.get(cid)
        title = (c["front_matter"].get("title") if c else None) or cid
        purpose = _purpose_sentence(c) if c else ""
        impact[cid] = (
            f"task '{snippet}': {title} applies ({why}); {purpose}"
            if purpose
            else f"task '{snippet}': {title} applies ({why})"
        )
    return impact


def _purpose_sentence(c: dict) -> str:
    m = re.search(r"## Purpose\n+(.*?)(?:\n\n|\n## )", c.get("text", ""), re.DOTALL)
    if not m:
        return ""
    para = " ".join(m.group(1).split())
    return para[:200]


def run_contract_gate(
    manifest_path: Path, task: str, lib: Path, role: str = "orchestrator"
) -> dict:
    """Phase 7 — resolve / read / verify / attest / commit via contractctl."""
    cc_path = lib / "tools" / "contractctl" / "contractctl.py"
    impact = generate_impact(manifest_path, task, lib)
    cmd = [
        sys.executable,
        str(cc_path),
        "commit",
        "--manifest",
        str(manifest_path),
        "--task",
        task,
        "--role",
        role,
    ]
    for cid, sentence in sorted(impact.items()):
        cmd += ["--impact", f"{cid}={sentence}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    text = r.stdout + r.stderr
    if r.returncode != 0:
        fr_state = re.search(r"REMOTE FRESHNESS: (\w+)", text)
        state = "UNKNOWN"
        if "CONTRACT COMMITMENT: STALE" in text:
            state = "STALE"
        elif (
            "CONTRACT COMMITMENT: INACTIVE" in text or "CONTRACT GATE: BLOCKED" in text
        ):
            state = "INACTIVE"
        return {
            "ok": False,
            "state": state,
            "freshness_state": fr_state.group(1) if fr_state else None,
            "output": text.strip(),
        }
    m = re.search(r"session artifact written: (.+)$", r.stdout, re.MULTILINE)
    artifact_path = Path(m.group(1).strip()) if m else None
    artifact = {}
    if artifact_path and artifact_path.is_file():
        try:
            artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        except ValueError:
            artifact = {}
    return {
        "ok": True,
        "state": "ACTIVE",
        "artifact_path": str(artifact_path) if artifact_path else None,
        "artifact": artifact,
        "output": r.stdout,
        "impact": impact,
        "library_revision": artifact.get("library_revision"),
    }


# ------------------------------------------------------------- work permit


def write_permit(
    repo: Path,
    manifest_path: Path,
    task: str,
    fr: dict,
    repo_state: dict,
    carryover: dict,
    gate: dict,
) -> dict:
    """Phase 8 — a secret-free machine-readable work permit."""
    artifact = gate.get("artifact") or {}
    source = artifact.get("source") or {}
    permit = {
        "format": "play-nice/work-permit-v1",
        "work_permit": "ACTIVE",
        "task": task,
        "play_nice": {
            "status": fr.get("status", "UNKNOWN"),
            "revision": fr.get("remote_revision"),
            "source_repository": source.get("repository") or fr.get("repository"),
            "ref": fr.get("ref") or source.get("ref"),
            "policy": fr.get("manifest_policy", "pinned"),
            "enforced": bool(fr.get("enforced")),
        },
        "repository": {
            "status": repo_state.get("status", "UNKNOWN"),
            "revision": repo_state.get("head"),
            "branch": repo_state.get("branch"),
            "dirty": bool(repo_state.get("dirty")),
        },
        "carryover": {
            "status": carryover.get("state", "RECONCILED"),
            "items": carryover.get("items", []),
        },
        "contract_gate": artifact.get("contract_gate", "PASS"),
        "commitment": {
            "status": artifact.get("commitment", "ACTIVE"),
            "bundle_sha256": artifact.get("bundle_sha256"),
            "bundle_receipt": artifact.get("bundle_receipt"),
            "task": artifact.get("task"),
            "role": artifact.get("role", "session"),
            "artifact": gate.get("artifact_path"),
        },
        "worker_packet": {
            "INHERITED_CONTRACT_BUNDLE": artifact.get("bundle_sha256"),
            "PLAY_NICE_SOURCE_REVISION": source.get("revision"),
            "PARENT_CONTRACT_COMMITMENT": artifact.get("commitment", "ACTIVE"),
        },
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "library": gate.get("library_revision"),
    }
    out = manifest_path.parent / "work-permit.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(permit, indent=2) + "\n", encoding="utf-8")
    permit["_path"] = str(out)
    return permit


def load_permit(repo: Path, manifest_path: Path | None = None) -> dict | None:
    if manifest_path is not None:
        p = manifest_path.parent / "work-permit.json"
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                return None
    for rel in (".contracts/work-permit.json", ".project/contracts/work-permit.json"):
        p = repo / rel
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                return None
    return None


def commitment_still_active(
    manifest_path: Path, task: str, lib: Path
) -> tuple[bool, str]:
    """Live revalidation: session-status re-checks remote freshness under
    require-current, so a stale commitment (remote moved since the permit) is
    never treated as authorization to mutate."""
    cc_path = lib / "tools" / "contractctl" / "contractctl.py"
    r = subprocess.run(
        [
            sys.executable,
            str(cc_path),
            "session-status",
            "--manifest",
            str(manifest_path),
            "--role",
            "orchestrator",
            "--task",
            task,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    text = r.stdout + r.stderr
    active = "CONTRACT COMMITMENT: ACTIVE" in text
    if active:
        return True, "commitment ACTIVE (freshness re-verified)"
    m = re.search(r"CONTRACT COMMITMENT: (\w+)", text)
    return False, f"commitment {m.group(1) if m else 'UNKNOWN'} — {text.strip()[:160]}"


# ------------------------------------------------------------- agent launch


def build_agent_prompt(permit: dict, task: str, lib: Path) -> str:
    wp = permit["worker_packet"]
    return (
        "WORK PERMIT: ACTIVE — playnice orchestrator session\n"
        f"task: {task}\n"
        f"repo: {permit['repository']['branch']} @{permit['repository']['revision']}\n"
        f"PLAY NICE: {permit['play_nice']['status']} @{(permit['play_nice'].get('revision') or '')[:12]}\n"
        f"library: {lib} (contractctl lives here; PLAY_NICE_LIBRARY is set)\n"
        f"INHERITED CONTRACT BUNDLE: {wp.get('INHERITED_CONTRACT_BUNDLE')}\n"
        f"PLAY_NICE_SOURCE_REVISION: {wp.get('PLAY_NICE_SOURCE_REVISION')}\n"
        f"PARENT CONTRACT COMMITMENT: {wp.get('PARENT_CONTRACT_COMMITMENT')}\n"
        "\n"
        "Instructions:\n"
        "1. Follow this repository's AGENTS.md, then resolve and read the applicable\n"
        "   Play-Nice contracts from the library at $PLAY_NICE_LIBRARY.\n"
        "2. Run your OWN worker contract gate before mutating: contractctl commit\n"
        '   --manifest <manifest> --task "<your task>" --worker --parent-bundle\n'
        "   <INHERITED_CONTRACT_BUNDLE> with --impact for every resolved contract,\n"
        "   including the inherited set. Workers inherit; they may strengthen\n"
        "   constraints, never weaken them, and may not resolve a weaker source.\n"
        "3. Do the bounded task. Stay in scope and in the repository.\n"
        "4. Commit your work with explicit paths (never `git add -A` in shared\n"
        "   checkouts), push, and open a PR when that is the workflow.\n"
        "5. End your reply with the standard handoff sections\n"
        "   (CURRENT / CHANGED / VERIFIED / CONTRACTS / UNKNOWN / DEFERRED / NEXT).\n"
        "\n"
        f"THE WORK: {task}"
    )


def launch_agent(
    cfg: dict, repo: Path, task: str, permit: dict, lib: Path, env: dict | None = None
) -> int:
    command = cfg["agent"]["command"]
    args = list(cfg["agent"]["args"] or [])
    if not shutil.which(command):
        raise PlayNiceError(
            f"agent command '{command}' not found on PATH; install it or set "
            "agent.command in the play-nice global config"
        )
    prompt = build_agent_prompt(permit, task, lib)
    full = [command, *args, prompt]
    e = dict(os.environ)
    e["PLAY_NICE_LIBRARY"] = str(lib)
    e["PLAY_NICE_PERMIT"] = permit.get("_path") or ""
    timeout = cfg["post"].get("timeout_minutes") or 0
    print(f"launching agent: {' '.join(full[:3])} ...")
    r = subprocess.run(
        full, cwd=str(repo), env=e, timeout=(timeout * 60) if timeout else None
    )
    return r.returncode


# ------------------------------------------------------------- handoff


def handoff_path(repo: Path, cfg: dict) -> Path:
    p = cfg["handoff"].get("path") or ""
    if p:
        path = Path(p)
        if not path.is_absolute():
            path = repo / path
        return path
    if (repo / ".project").is_dir():
        return repo / ".project" / "HANDOFF.md"
    return repo / ".agent" / "HANDOFF.md"


def format_handoff(
    repo: Path,
    cfg: dict,
    fr: dict,
    repo_state: dict,
    carryover: dict,
    gate: dict,
    permit: dict,
    ops: list[dict],
    agent_rc: int | None,
    task: str,
    next_line: str,
) -> str:
    lines: list[str] = []
    lines.append(
        f"CURRENT: {repo_state.get('branch')} @{str(repo_state.get('head'))[:12]} "
        f"(dirty={bool(repo_state.get('dirty'))})"
    )
    lines.append(f"CHANGED: playnice orchestration for task {task!r}")
    if ops:
        for op in ops:
            lines.append(f"  - {op.get('op')}: {op.get('target')} ({op.get('detail')})")
    lines.append("VERIFIED: " + _verified_line(gate, fr, repo_state))
    lines.append("CONTRACTS: " + _contracts_line(gate))
    lines.append("UNKNOWN: " + _unknown_line(fr, repo_state, carryover, agent_rc))
    lines.append("DEFERRED: " + _deferred_line(carryover))
    lines.append(f"NEXT: {next_line}")
    return "\n".join(lines) + "\n"


def _verified_line(gate: dict, fr: dict, repo_state: dict) -> str:
    bits = []
    bits.append(f"play nice {fr.get('status')}")
    bits.append(f"repo {repo_state.get('status')}")
    if gate.get("ok"):
        bits.append("contract gate PASS (receipts+hashes verified by contractctl)")
    return "; ".join(bits)


def _contracts_line(gate: dict) -> str:
    if not gate.get("ok"):
        return f"gated: {gate.get('state', 'UNKNOWN')}"
    a = gate.get("artifact") or {}
    return (
        f"bundle {a.get('bundle_receipt')} ({str(a.get('bundle_sha256'))[:12]}) "
        f"gate {a.get('contract_gate')} commitment {a.get('commitment')} role {a.get('role')}"
    )


def _unknown_line(
    fr: dict, repo_state: dict, carryover: dict, agent_rc: int | None
) -> str:
    bits = []
    if fr.get("status") != "CURRENT":
        bits.append(f"freshness {fr.get('status')}")
    if repo_state.get("status") == "UNKNOWN":
        bits.append("repository state UNKNOWN")
    if carryover.get("state") == "PARTIAL":
        bits.append("carryover PARTIAL (see items)")
    if agent_rc is not None and agent_rc != 0:
        bits.append(f"agent exited {agent_rc}")
    return ", ".join(bits) or "none"


def _deferred_line(carryover: dict) -> str:
    items = [
        i for i in carryover.get("items", []) if i.get("disposition") == "DEFERRED"
    ]
    if not items:
        return "none"
    return "; ".join(i.get("label", "") for i in items[:5])


def write_handoff(repo: Path, cfg: dict, text: str) -> Path:
    p = handoff_path(repo, cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# ------------------------------------------------------------- NEXT


def compute_next(
    fr: dict,
    repo_state: dict,
    carryover: dict,
    gate: dict,
    ops: list[dict],
    agent_rc: int | None,
    cfg: dict,
    launched: bool,
) -> str:
    if not launched:
        return "agent not launched (--no-launch); preflight permit written"
    if agent_rc not in (0, None):
        return f"agent exited {agent_rc}; inspect the failure before further mutation"
    if repo_state.get("dirty"):
        return "working tree is dirty; inspect and commit/park the changes"
    if fr.get("enforced") and fr.get("status") != "CURRENT":
        return f"play nice freshness {fr.get('status')}; refresh and re-gate before mutation"
    if not gate.get("ok"):
        return f"contract gate {gate.get('state', 'UNKNOWN')}; resolve, then re-run"
    failed = [
        o
        for o in ops
        if o.get("op") in ("merge-failed", "delete-failed", "close-failed")
    ]
    if failed:
        return (
            f"{len(failed)} reconcile operation(s) failed; inspect: "
            f"{failed[0].get('detail', '')[:120]}"
        )
    waiting = [
        o
        for o in ops
        if o.get("op") == "skip" and "review required" in o.get("detail", "")
    ]
    if waiting:
        return "WAITING_FOR_HELP: a PR requires human review before merge"
    if cfg["github"]["merge_ready_pull_requests"]:
        needs_ci = [
            o
            for o in ops
            if o.get("op") == "skip" and "checks not green" in o.get("detail", "")
        ]
        if needs_ci:
            return "WAITING_FOR_HELP: PR(s) awaiting CI"
    blocked = [
        i for i in carryover.get("items", []) if i.get("disposition") == "BLOCKED"
    ]
    if blocked:
        return "BLOCKED: carryover items: " + ", ".join(
            i.get("label", "") for i in blocked[:5]
        )
    unknown = [
        i for i in carryover.get("items", []) if i.get("disposition") == "UNKNOWN"
    ]
    if unknown:
        return "carryover has `UNKNOWN` items (preserved): " + ", ".join(
            i.get("label", "") for i in unknown[:5]
        )
    return "nothing required"


# ------------------------------------------------------------- orchestration


def _print_permit(fr: dict, repo_state: dict, carryover: dict, gate: dict) -> None:
    print(
        f"PLAY NICE: {fr.get('status')} ({fr.get('ref') or '?'} @{str(fr.get('remote_revision') or '')[:12]})"
    )
    print(
        f"REPOSITORY: {repo_state.get('status')} ({repo_state.get('branch')} @{str(repo_state.get('head') or '')[:12]}, dirty={bool(repo_state.get('dirty'))})"
    )
    print(
        f"CARRYOVER: {carryover.get('state')} ({len(carryover.get('items', []))} items)"
    )
    gate_ok = gate.get("ok")
    print(
        f"CONTRACT GATE: {gate.get('artifact', {}).get('contract_gate', 'FAIL') if gate_ok else 'FAIL'}"
    )
    print(
        f"COMMITMENT: {gate.get('artifact', {}).get('commitment', 'INACTIVE') if gate_ok else 'INACTIVE'}"
    )
    print("WORK PERMIT: ACTIVE")


def cmd_work(args) -> int:
    cfg = load_global_config(Path(args.config) if args.config else None)
    if args.no_github:
        cfg["github"] = {
            **cfg["github"],
            "inspect_pull_requests": False,
            "inspect_issues": False,
            "inspect_ci": False,
            "merge_ready_pull_requests": False,
            "close_proven_resolved_issues": False,
            "remove_proven_merged_branches": False,
        }
    env = dict(os.environ)
    if args.agent:
        cfg["agent"]["command"] = args.agent
    repo = Path(args.repo).resolve()
    task = args.task
    if not task:
        print(
            'playnice: a task is required (e.g. playnice work "fix the settings page")',
            file=sys.stderr,
        )
        return 1
    manifest_path = find_adoption_manifest(repo, args.manifest)
    if manifest_path is None:
        print(
            "PLAY NICE: UNKNOWN — no adoption manifest found in this repository.\n"
            "  A participating repo carries `.contracts/adoption.yaml` (or\n"
            "  `.project/contracts/adoption.yaml`). Copy an example and pin the\n"
            "  reviewed revision: `cp examples/<repo>.adoption.yaml <repo>/.contracts/adoption.yaml`",
            file=sys.stderr,
        )
        return 2

    lib = find_library(cfg, Path.cwd(), env)
    fr = play_nice_check(manifest_path, lib, cfg)
    print(
        f"REMOTE FRESHNESS: {fr.get('status')}  (enforced={bool(fr.get('enforced'))})"
    )
    if fr.get("remote_revision"):
        print(f"  authoritative revision: {fr['remote_revision']}")
    if freshness_blocked(fr):
        print(f"  - {fr.get('detail', '')}")
        sync = sync_pin_if_allowed(manifest_path, fr, lib)
        if sync["performed"]:
            print(f"  synced: {sync['detail']}")
            fr = play_nice_check(manifest_path, lib, cfg)
            print(f"REMOTE FRESHNESS: {fr.get('status')}  (after sync)")
        else:
            if sync.get("detail"):
                print(f"  (no auto-sync: {sync['detail']})")
        if freshness_blocked(fr):
            print(
                "CONTRACT COMMITMENT: INACTIVE — mutating work stays blocked (fail closed)"
            )
            return 2

    repo_state = reconcile_repo(repo, cfg)
    gh = None
    if cfg["github"]["inspect_pull_requests"] or cfg["github"]["inspect_issues"]:
        gh = collect_github_state(repo, cfg, env)
        if gh.get("note") and not gh.get("available"):
            print(f"GITHUB STATE: {gh['note']}")
    carryover = discover_carryover(repo, cfg, gh)
    for item in carryover["items"]:
        print(
            f"  carryover: {item.get('disposition'):16s} {item.get('label')} — {item.get('action')}"
        )
    if carryover["state"] != "RECONCILED":
        print(
            f"CARRYOVER: {carryover['state']} — unknown items are preserved, never guessed"
        )

    gate = run_contract_gate(manifest_path, task, lib, role="orchestrator")
    if not gate["ok"]:
        print(gate["output"])
        print(f"\nCONTRACT GATE: {gate['state']}")
        print("CONTRACT COMMITMENT: INACTIVE")
        return 2
    print(gate["output"])

    permit = write_permit(repo, manifest_path, task, fr, repo_state, carryover, gate)
    _print_permit(fr, repo_state, carryover, gate)
    print(f"permit: {permit.get('_path')}")

    if args.no_launch:
        next_line = compute_next(fr, repo_state, carryover, gate, [], None, cfg, False)
        hd = write_handoff(
            repo,
            cfg,
            format_handoff(
                repo,
                cfg,
                fr,
                repo_state,
                carryover,
                gate,
                permit,
                [],
                None,
                task,
                next_line,
            ),
        )
        print(f"handoff: {hd}")
        print(f"NEXT: {next_line}")
        return 0

    agent_rc = launch_agent(cfg, repo, task, permit, lib, env)
    ops: list[dict] = []
    if agent_rc == 0:
        print("agent finished; reconciling post-work ...")
        if (
            cfg["github"]["merge_ready_pull_requests"]
            or cfg["github"]["close_proven_resolved_issues"]
            or cfg["github"]["remove_proven_merged_branches"]
        ):
            gh2 = collect_github_state(repo, cfg, env)
            ops = reconcile_github(repo, cfg, permit, gh2, env)
            for op in ops:
                print(
                    f"  reconcile: {op.get('op')}: {op.get('target')} — {op.get('detail', '')}"
                )
        else:
            print("  (github reconcile disabled in config)")
    else:
        print(f"agent exited {agent_rc}")

    next_line = compute_next(fr, repo_state, carryover, gate, ops, agent_rc, cfg, True)
    hd = write_handoff(
        repo,
        cfg,
        format_handoff(
            repo,
            cfg,
            fr,
            repo_state,
            carryover,
            gate,
            permit,
            ops,
            agent_rc,
            task,
            next_line,
        ),
    )
    print(f"handoff: {hd}")
    print(f"NEXT: {next_line}")
    return 0 if agent_rc == 0 else 3


def cmd_status(args) -> int:
    """Read-only inspection: freshness + repo + carryover + GitHub state."""
    cfg = load_global_config(Path(args.config) if args.config else None)
    if args.no_github:
        cfg["github"] = {
            **cfg["github"],
            "inspect_pull_requests": False,
            "inspect_issues": False,
            "inspect_ci": False,
        }
    env = dict(os.environ)
    repo = Path(args.repo).resolve()
    manifest_path = find_adoption_manifest(repo, args.manifest)
    lib = find_library(cfg, Path.cwd(), env)
    out: dict = {}
    if manifest_path is None:
        out["adoption"] = "UNKNOWN"
        out["play_nice"] = {
            "status": "UNKNOWN",
            "enforced": False,
            "detail": "no adoption manifest found in this repository",
        }
    else:
        fr = play_nice_check(manifest_path, lib, cfg)
        out["play_nice"] = fr
    rs = collect_repo_state(repo, cfg)
    out["repository"] = rs
    gh = None
    if cfg["github"]["inspect_pull_requests"] or cfg["github"]["inspect_issues"]:
        gh = collect_github_state(repo, cfg, env)
        out["github"] = gh
    co = discover_carryover(repo, cfg, gh)
    out["carryover"] = {
        "state": co["state"],
        "items": [
            {
                "kind": i.get("kind"),
                "label": i.get("label"),
                "detail": i.get("detail"),
                "disposition": i.get("disposition"),
                "action": i.get("action"),
            }
            for i in co["items"]
        ],
    }
    if args.json_output:
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0
    fr = out.get("play_nice") or {}
    fr = {**fr, "status": fr.get("status", "UNKNOWN")}
    print(f"PLAY NICE: {fr.get('status')} (enforced={bool(fr.get('enforced'))})")
    print(
        f"REPOSITORY: {out['repository'].get('status')} ({out['repository'].get('branch')} @{str(out['repository'].get('head') or '')[:12]}, dirty={bool(out['repository'].get('dirty'))})"
    )
    print(
        f"CARRYOVER: {out['carryover']['state']} ({len(out['carryover']['items'])} items)"
    )
    for item in out["carryover"]["items"]:
        print(
            f"  carryover: {item.get('disposition'):16s} {item.get('label')} — {item.get('action')}"
        )
    if out.get("github"):
        g = out["github"]
        print(
            f"GITHUB: available={bool(g.get('available'))} prs={len(g.get('prs', []))} issues={len(g.get('issues', []))}"
        )
        if g.get("note"):
            print(f"  {g['note']}")
    permit = load_permit(repo, manifest_path)
    if permit:
        print(f"WORK PERMIT: {permit.get('work_permit')} (task: {permit.get('task')})")
        if permit.get("commitment"):
            print(
                f"  commitment: {permit['commitment'].get('status')} "
                f"bundle {str(permit['commitment'].get('bundle_sha256'))[:12]}"
            )
    else:
        print("WORK PERMIT: none on file")
    return 0


def cmd_reconcile(args) -> int:
    """Standalone carryover + auto-finish. Mutations need an ACTIVE permit."""
    cfg = load_global_config(Path(args.config) if args.config else None)
    if args.no_github:
        cfg["github"] = {
            **cfg["github"],
            "inspect_pull_requests": False,
            "inspect_issues": False,
            "inspect_ci": False,
            "merge_ready_pull_requests": False,
            "close_proven_resolved_issues": False,
            "remove_proven_merged_branches": False,
        }
    env = dict(os.environ)
    repo = Path(args.repo).resolve()
    manifest_path = find_adoption_manifest(repo, args.manifest)
    lib = find_library(cfg, Path.cwd(), env)
    if manifest_path is None:
        print(
            "reconcile: no adoption manifest found; run a gate first", file=sys.stderr
        )
        return 2
    permit = load_permit(repo, manifest_path)
    gh = None
    if cfg["github"]["inspect_pull_requests"] or cfg["github"]["inspect_issues"]:
        gh = collect_github_state(repo, cfg, env)
        if gh.get("note"):
            print(f"GITHUB STATE: {gh['note']}")
    co = discover_carryover(repo, cfg, gh)
    for item in co["items"]:
        print(
            f"  carryover: {item.get('disposition'):16s} {item.get('label')} — {item.get('action')}"
        )
    if not permit or permit.get("work_permit") != "ACTIVE":
        print(
            "reconcile: no ACTIVE work permit on file — run `playnice work` to gate first"
        )
        print("read-only reconciliation above; mutations stay blocked")
        return 4
    ok, detail = commitment_still_active(manifest_path, permit.get("task", ""), lib)
    if not ok:
        print(f"reconcile: {detail}")
        print("mutations stay blocked until a fresh gate passes")
        return 4
    ops = reconcile_github(repo, cfg, permit, gh, env)
    for op in ops:
        print(
            f"  reconcile: {op.get('op')}: {op.get('target')} — {op.get('detail', '')}"
        )
    next_line = compute_next({}, {}, co, {"ok": True}, ops, None, cfg, True)
    print(f"NEXT: {next_line}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="playnice",
        description="Global agent-work entry point: refresh truth, reconcile old work, "
        "load Play Nice, launch the agent, verify and clean up afterward.",
    )
    ap.add_argument(
        "--version", action="version", version=f"playnice {PLAYNICE_VERSION}"
    )
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("work", help="run the full lifecycle for a task")
    p.add_argument(
        "task", nargs="?", help='the work to do, e.g. "fix the settings page"'
    )
    p.add_argument(
        "--repo", default=".", help="target repository (default: current directory)"
    )
    p.add_argument("--config", default=None, help="path to the global play-nice config")
    p.add_argument("--manifest", default=None, help="path to the adoption manifest")
    p.add_argument(
        "--agent", default=None, help="override agent command (e.g. codex, kilo, aider)"
    )
    p.add_argument(
        "--no-launch",
        action="store_true",
        help="preflight + permit only; do not launch the agent",
    )
    p.add_argument(
        "--no-github",
        action="store_true",
        help="disable GitHub inspection and mutations",
    )
    p.add_argument("--json", action="store_true", dest="json_output")
    p.set_defaults(func=cmd_work)

    p = sub.add_parser("status", help="read-only current-state inspection")
    p.add_argument("--repo", default=".")
    p.add_argument("--config", default=None)
    p.add_argument("--manifest", default=None)
    p.add_argument("--no-github", action="store_true")
    p.add_argument("--json", action="store_true", dest="json_output")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser(
        "reconcile", help="carryover + auto-finish (mutations need an ACTIVE permit)"
    )
    p.add_argument("--repo", default=".")
    p.add_argument("--config", default=None)
    p.add_argument("--manifest", default=None)
    p.add_argument("--no-github", action="store_true")
    p.add_argument("--json", action="store_true", dest="json_output")
    p.set_defaults(func=cmd_reconcile)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ConfigError as e:
        print(f"playnice: config error: {e}", file=sys.stderr)
        return 2
    except PlayNiceError as e:
        print(f"playnice: {e}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as e:
        print(f"playnice: timeout: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
