"""Play-nice contract library test suite.

Covers the required validation cases:
- duplicate IDs fail
- duplicate receipts fail
- missing receipt fails
- invalid version fails
- index drift fails
- lockfile drift detected
- hashes verified
- adoption schemas validated
- unknown contract rejected
- ALWAYS contracts always selected
- trigger selection works
- irrelevant contracts omitted
- bundle changes when contract changes
- stale pin detected
- incorrect receipt fails
- incorrect hash fails
- omitted mandatory contract fails
- conflict state representable
- offline validation works
- plus attestation end-to-end pass/fail and determinism checks.
"""

import copy
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CT = REPO / "tools" / "contractctl" / "contractctl.py"


# --------------------------------------------------------------- fixtures

@pytest.fixture()
def lib():
    sys.path.insert(0, str(REPO / "tools" / "contractctl"))
    import contractctl as ct
    yield ct
    sys.path.pop(0)


@pytest.fixture()
def tmp_repo(tmp_path, lib):
    """A copy of the library for mutation tests (keeps the real tree safe).
    Initialized as a Git repo with one baseline commit so Git-history-based
    enforcement (receipt rotation) is exercisable."""
    dest = tmp_path / "play-nice-contracts"
    shutil.copytree(REPO, dest / "play-nice-contracts", symlinks=True,
                    ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__",
                                                   ".pytest_cache", ".contract-commitments"))
    repo = dest / "play-nice-contracts"
    def _git(*args):
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True, timeout=30)
    _git("init", "-b", "main")
    _git("config", "user.email", "test@example.invalid")
    _git("config", "user.name", "Test")
    _git("add", "-A")
    _git("commit", "-m", "baseline", "--no-gpg-sign")
    # contractctl resolves REPO_ROOT from its own path; run against the copy
    ct_path = repo / "tools" / "contractctl" / "contractctl.py"
    (repo / ".tests-ct-path").write_text(str(ct_path))
    yield repo


import os as _os


def artifact_dir(repo, manifest_rel="examples/homelab.adoption.yaml"):
    """Consumer-context artifact dir for a repo whose adoption manifest lives
    at manifest_rel: <manifest's parent>/.contracts/sessions/."""
    m = repo / manifest_rel
    if m.parent.name == ".contracts":
        return m.parent / "sessions"
    return m.parent / ".contracts" / "sessions"


def run_ct(args, cwd=None, ct_path=None, env=None):
    ct = ct_path or CT
    full_env = _os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, str(ct), *args],
        capture_output=True, text=True, cwd=cwd or str(REPO), timeout=60,
        env=full_env,
    )


# --------------------------------------------------------------- library validity

def test_library_validates(lib):
    errors = lib.validate_library()
    assert errors == [], "\n".join(errors)


def test_receipts_unique(lib):
    receipts = []
    for c in lib.load_library():
        assert len(c["receipts"]) == 1, f"{c['rel_path']} receipt count"
        receipts.append(c["receipts"][0])
    assert len(receipts) == len(set(receipts))


def test_all_contracts_dual_use_structure(lib):
    required_sections = [
        "## Purpose",
        "## NORMATIVE RULES",
        "## RATIONALE",
        "## HUMAN EXAMPLES",
        "## ANTI-PATTERNS",
        "## ACCEPTANCE CHECKS",
    ]
    for c in lib.load_library():
        for sec in required_sections:
            assert sec in c["text"], f"{c['rel_path']} missing {sec!r}"


def test_contract_count(lib):
    assert len(lib.load_library()) == 61


# --------------------------------------------------------------- validation failures (mutation tests)

_CT_CACHE = {}


def _load_ct_from(tmp_repo):
    """Import contractctl from the copied repo, bypassing module cache."""
    import importlib.util
    key = str(tmp_repo)
    if key in _CT_CACHE:
        return _CT_CACHE[key]
    path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    spec = importlib.util.spec_from_file_location(f"ct_{abs(hash(key))}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _CT_CACHE[key] = mod
    return mod


def test_duplicate_id_fails(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    src = tmp_repo / "contracts" / "core" / "TRUTH_AND_EVIDENCE.md"
    dup = tmp_repo / "contracts" / "core" / "TRUTH_DUPLICATE.md"
    # same contract_id, different file, unique receipt → pure duplicate-id error
    text = src.read_text().replace("wren-loam-sail", "north-juniper-cedar")
    dup.write_text(text)
    errors = ct.validate_library()
    assert any("duplicate contract_id" in e for e in errors), errors


def test_duplicate_receipt_fails(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    src = tmp_repo / "contracts" / "core" / "EXPLICIT_STATE.md"
    target = tmp_repo / "contracts" / "core" / "PLAY_NICE_TOGETHER.md"
    text = target.read_text()
    # give PLAY_NICE_TOGETHER the same receipt as EXPLICIT_STATE
    text = text.replace("cedar-basalt-vellum", "driftwood-thicket-jetty")
    target.write_text(text)
    errors = ct.validate_library()
    assert any("duplicate receipt" in e for e in errors), errors


def test_missing_receipt_fails(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    target = tmp_repo / "contracts" / "human" / "HUMAN_RELIABILITY.md"
    text = target.read_text()
    text = text.replace("<!-- contract-receipt: dell-maple-anchor -->", "")
    target.write_text(text)
    errors = ct.validate_library()
    assert any("missing receipt" in e for e in errors), errors


def test_invalid_version_fails(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    target = tmp_repo / "contracts" / "core" / "PROVENANCE_AND_AUDIT.md"
    text = target.read_text().replace("version: 1.0.0", "version: banana")
    target.write_text(text)
    errors = ct.validate_library()
    assert any("invalid version" in e for e in errors), errors


def test_index_drift_fails(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    idx = tmp_repo / "CONTRACT_INDEX.md"
    text = idx.read_text()
    # remove a row → contract missing from index
    text = text.replace("| `truth-and-evidence` | Truth and Evidence | 1.0.0 | canonical |", "| `ghost-contract` | Ghost | 1.0.0 | canonical |")
    idx.write_text(text)
    errors = ct.validate_library()
    assert any("missing from CONTRACT_INDEX.md" in e for e in errors), errors
    assert any("unknown contract 'ghost-contract'" in e for e in errors), errors


def test_lockfile_drift_detected(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    lock = tmp_repo / "contracts.lock.json"
    data = json.loads(lock.read_text())
    data["contracts"][0]["sha256"] = "f" * 64
    lock.write_text(json.dumps(data))
    errors = ct.verify_lock()
    assert any("hash changed" in e for e in errors), errors


def test_lockfile_missing_contract_detected(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    lock = tmp_repo / "contracts.lock.json"
    data = json.loads(lock.read_text())
    removed = data["contracts"].pop()
    lock.write_text(json.dumps(data))
    errors = ct.verify_lock()
    assert any("missing from contracts.lock.json" in e for e in errors), errors


def test_hash_verification(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    import hashlib
    src = tmp_repo / "contracts" / "core" / "TRUTH_AND_EVIDENCE.md"
    sha = hashlib.sha256(src.read_text().encode()).hexdigest()
    lock = json.loads((tmp_repo / "contracts.lock.json").read_text())
    entry = [e for e in lock["contracts"] if e["id"] == "truth-and-evidence"][0]
    assert entry["sha256"] == sha


# --------------------------------------------------------------- adoption

def test_adoption_examples_valid(lib):
    for name in ("personal-world", "vefr", "homelab"):
        path = REPO / "examples" / f"{name}.adoption.yaml"
        errors = lib.validate_adoption_manifest(path)
        assert errors == [], f"{name}: {errors}"


def test_adoption_unknown_contract_rejected(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    m = tmp_repo / "examples" / "vefr.adoption.yaml"
    text = m.read_text().replace("- deterministic-first", "- not-a-real-contract")
    m.write_text(text)
    errors = ct.validate_adoption_manifest(m)
    assert any("unknown contract" in e for e in errors), errors


def test_adoption_bad_schema_rejected(tmp_path):
    ct_path = REPO / "tools" / "contractctl" / "contractctl.py"
    bad = tmp_path / "adoption.yaml"
    bad.write_text("schema: wrong/schema\nsource: {repository: x}\n")
    r = run_ct(["adopt", "--manifest", str(bad)], ct_path=ct_path)
    assert r.returncode != 0
    assert "play-nice/adoption-v1" in (r.stdout + r.stderr)


# --------------------------------------------------------------- resolution

def test_always_contracts_selected(lib):
    m = lib.load_adoption(REPO / "examples" / "personal-world.adoption.yaml")
    res = lib.resolve_set(m, task="totally unrelated backend refactor")
    for cid in m["always"]:
        assert cid in res["selected"], cid


def test_trigger_selection_works(lib):
    m = lib.load_adoption(REPO / "examples" / "personal-world.adoption.yaml")
    res = lib.resolve_set(m, task="add GitHub provider and update Project UI", task_tags=["external-api"])
    for cid in ("friendly-api-client", "provider-neutrality", "capability-first"):
        assert cid in res["selected"], cid


def test_irrelevant_contracts_omitted(lib):
    m = lib.load_adoption(REPO / "examples" / "homelab.adoption.yaml")
    res = lib.resolve_set(m, task="rename a variable in the deploy script", task_tags=["git"])
    assert "migraine-and-sensory-safety" not in res["selected"]
    assert "guide-me" not in res["selected"]
    # ALWAYS still applies
    for cid in m["always"]:
        assert cid in res["selected"]


def test_resolve_unknown_contract_errors(lib):
    fake = {"schema": "play-nice/adoption-v1", "always": ["ghost"], "triggers": {}}
    res = lib.resolve_set(fake, task="")
    assert any("unknown contract" in e for e in res["errors"])


# --------------------------------------------------------------- bundle + lock determinism

def test_lock_generation_deterministic(lib):
    a = lib.build_lock()
    b = lib.build_lock()
    assert a == b
    assert lib.bundle_receipt(a) == lib.bundle_receipt(b)


def test_bundle_changes_when_contract_changes(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    before = ct.bundle_receipt(ct.load_lock())
    target = tmp_repo / "contracts" / "core" / "TRUTH_AND_EVIDENCE.md"
    text = target.read_text()
    target.write_text(text.replace("UNKNOWN", "UNKNOWN-AND-PROUD"))
    # regenerate lock from mutated library
    lock2 = ct.build_lock()
    after = ct.bundle_receipt(lock2)
    assert before != after


# --------------------------------------------------------------- attestation

def _attest(tmp_repo, manifest, task, impact, ct_path):
    args = ["attest", "--manifest", str(manifest), "--task", task]
    for k, v in impact.items():
        args.append("--impact")
        args.append(f"{k}={v}")
    return run_ct(args, cwd=str(tmp_repo), ct_path=ct_path)


def test_good_attestation_passes_and_verifies(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "rotate the deploy credentials and update the health checks"
    # impact must cover every contract the resolver selects for this task
    impact = {
        "truth-and-evidence": "rotation verified by live check, not by report",
        "explicit-state": "statuses use the shared vocabulary with observed_at",
        "recovery-and-reversibility": "rollback documented before rotation",
        "provenance-and-audit": "rotation journaled with actor and reason",
        "least-privilege": "deploy token scoped to the deploy job only",
        "ask-for-help": "unknown provider semantics get asked, not guessed",
    }
    r = _attest(tmp_repo, manifest, task, impact, ct_path)
    assert "CONTRACT GATE: PASS" in r.stdout, r.stdout + r.stderr
    att_path = tmp_repo / "att.txt"
    att_path.write_text(r.stdout)
    v = run_ct(["verify-attestation", str(att_path), "--manifest", str(manifest)],
               cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode == 0, v.stdout + v.stderr
    assert "ATTESTATION VERIFIED" in v.stdout


def test_missing_task_impact_blocks(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    r = run_ct(["attest", "--manifest", str(manifest),
                "--task", "redeploy the stack"], cwd=str(tmp_repo), ct_path=ct_path)
    assert "CONTRACT GATE: BLOCKED" in r.stdout
    assert "missing task-impact" in r.stdout


def test_incorrect_receipt_fails_verification(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    r = _attest(tmp_repo, manifest, task, impact, ct_path)
    att = tmp_repo / "att.txt"
    att.write_text(r.stdout.replace("wren-loam-sail", "wrong-wrong-wrong"))
    v = run_ct(["verify-attestation", str(att)], cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode != 0
    assert "wrong receipt" in v.stdout


def test_incorrect_hash_fails_verification(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    r = _attest(tmp_repo, manifest, task, impact, ct_path)
    assert "PASS" in r.stdout
    att = tmp_repo / "att.txt"
    att.write_text(r.stdout)
    # corrupt one hash in the lockfile underneath: verification must fail
    # closed on lock drift (hardening #5) — never verify against a stale lock
    lock = tmp_repo / "contracts.lock.json"
    data = json.loads(lock.read_text())
    for e in data["contracts"]:
        if e["id"] == "explicit-state":
            e["sha256"] = "0" * 64
    lock.write_text(json.dumps(data))
    v = run_ct(["verify-attestation", str(att)], cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode != 0
    assert "lock drift" in v.stdout


def test_omitted_mandatory_contract_fails_verification(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    r = _attest(tmp_repo, manifest, task, impact, ct_path)
    att = tmp_repo / "att.txt"
    # drop one mandatory (always) contract from the attestation text
    text = r.stdout
    lines = text.split("\n")
    out = []
    skip = 0
    for i, ln in enumerate(lines):
        if ln.strip() == "explicit-state@1.0.0":
            skip = 3  # skip the id + receipt + status lines
            continue
        if skip > 0:
            skip -= 1
            continue
        out.append(ln)
    att.write_text("\n".join(out))
    v = run_ct(["verify-attestation", str(att), "--manifest", str(manifest)],
               cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode != 0
    assert "mandatory contract 'explicit-state'" in v.stdout


def test_stale_attestation_fails_after_library_change(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    r = _attest(tmp_repo, manifest, task, impact, ct_path)
    att = tmp_repo / "att.txt"
    att.write_text(r.stdout)
    # now change a contract and relock: the old attestation must fail
    target = tmp_repo / "contracts" / "core" / "TRUTH_AND_EVIDENCE.md"
    target.write_text(target.read_text().replace("Make honesty cheap.", "Make honesty cheap and durable."))
    run_ct(["lock"], cwd=str(tmp_repo), ct_path=ct_path)
    v = run_ct(["verify-attestation", str(att)], cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode != 0
    assert "bundle receipt mismatch" in v.stdout or "hash" in v.stdout


def test_conflict_state_representable(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    m = ct.load_adoption(manifest)
    lock = ct.load_lock()
    # fabricate an attestation with a CONFLICT and verify it parses + gates BLOCKED
    text = f"""CONTRACT_ATTESTATION v1

bundle:
  library_version: 0.1.0
  library_revision: test
  receipt: {ct.bundle_receipt(lock, {'truth-and-evidence'})}
  sha256: {ct.bundle_sha256(lock, {'truth-and-evidence'})}
  scope: resolved-set

loaded:
  truth-and-evidence@1.0.0
    receipt: wren-loam-sail
    status: CONFLICT

task-impact:
  - truth-and-evidence: evidence grades preserved in reports

conflicts: truth-and-evidence conflicts with explicit-state on unknown-vs-healthy rendering

CONTRACT GATE: BLOCKED
"""
    p = tmp_repo / "conflict.txt"
    p.write_text(text)
    errors = ct.verify_attestation(p)
    # CONFLICT with explanation is valid representation; nothing about shape should fail
    assert not any("status" in e for e in errors), errors


# --------------------------------------------------------------- operational commitment

_IMPACT_OK = {
    "truth-and-evidence": "rotation verified by live check, not by report",
    "explicit-state": "statuses use the shared vocabulary with observed_at",
    "recovery-and-reversibility": "rollback documented before rotation",
    "provenance-and-audit": "rotation journaled with actor and reason",
    "least-privilege": "deploy token scoped to the deploy job only",
    "ask-for-help": "unknown provider semantics asked, not guessed; WAITING_FOR_HELP over retry",
}


def _commit_args(manifest, task, impact, extra=()):
    args = ["commit", "--manifest", str(manifest), "--task", task]
    for k, v in impact.items():
        args += ["--impact", f"{k}={v}"]
    return list(args) + list(extra)


def test_commitment_activates_and_status_reports(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "rotate the deploy credentials and update the health checks"
    r = run_ct(_commit_args(manifest, task, _IMPACT_OK), cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "CONTRACT COMMITMENT: ACTIVE" in r.stdout
    assert "bundle_sha256:" in r.stdout
    s = run_ct(["session-status", "--manifest", str(manifest)], cwd=str(tmp_repo), ct_path=ct_path)
    assert s.returncode == 0, s.stdout
    assert "CONTRACT COMMITMENT: ACTIVE" in s.stdout


def test_commitment_blocked_without_impact(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    r = run_ct(["commit", "--manifest", str(manifest), "--task", "rotate things"],
               cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode == 2
    assert "CONTRACT COMMITMENT: INACTIVE" in r.stderr
    assert "BLOCKED" in r.stderr


def test_commitment_records_exact_bundle(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "rotate the deploy credentials and update the health checks"
    r = run_ct(_commit_args(manifest, task, _IMPACT_OK), cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode == 0
    # keyed artifact path, not a global singleton
    slug_dir = artifact_dir(tmp_repo)
    assert slug_dir.is_dir()
    arts = list(slug_dir.glob("session-*.json"))
    assert len(arts) == 1
    art = json.loads(arts[0].read_text())
    lock = ct.load_lock()
    selected = set(art["contracts"])
    # bundle identity is the RESOLVED set, not the whole library
    assert art["bundle_receipt"] == ct.bundle_receipt(lock, selected)
    assert art["bundle_sha256"] == ct.bundle_sha256(lock, selected)
    assert art["bundle_receipt"] != ct.bundle_receipt(lock)
    assert art["contract_gate"] == "PASS"
    assert art["commitment"] == "ACTIVE"
    assert selected == {
        "truth-and-evidence", "explicit-state", "recovery-and-reversibility",
        "provenance-and-audit", "least-privilege", "ask-for-help"}
    assert art["library_version"] == "0.2.1"  # semver from VERSION
    # no secrets by construction: artifact only carries ids/hashes/words
    blob = json.dumps(art).lower()
    for bad in ("token", "secret", "password", "api_key"):
        assert bad not in blob or bad in ("task",)  # task text mentions credentials, fine


def test_resolved_set_bundle_differs_by_scope(tmp_repo):
    """Two different task scopes resolve different bundle identities (hardening #1)."""
    ct = _load_ct_from(tmp_repo)
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    lock = ct.load_lock()
    broad = set(ct.resolve_set(ct.load_adoption(manifest),
                               "rotate the deploy credentials and update the health checks")["selected"])
    narrow = set(ct.resolve_set(ct.load_adoption(manifest),
                                "update a compose file")["selected"])
    assert ct.bundle_receipt(lock, broad) != ct.bundle_receipt(lock, narrow)
    assert ct.bundle_sha256(lock, broad) != ct.bundle_sha256(lock, narrow)
    # same scope → identical identity (deterministic)
    assert ct.bundle_receipt(lock, broad) == ct.bundle_receipt(lock, set(broad))


def test_library_version_vs_revision(tmp_repo):
    """Library semver and adopted git revision are distinct concepts (hardening #2)."""
    ct = _load_ct_from(tmp_repo)
    assert ct.library_version() == "0.2.1"          # semver from VERSION file
    rev = ct.library_revision()
    assert rev != "unknown"
    assert rev != ct.library_version()              # git SHA when repo initialized


def test_stale_bundle_invalidates_commitment(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "rotate the deploy credentials and update the health checks"
    assert run_ct(_commit_args(manifest, task, _IMPACT_OK), cwd=str(tmp_repo), ct_path=ct_path).returncode == 0
    # change the library → relock → commitment must go STALE
    target = tmp_repo / "contracts" / "core" / "TRUTH_AND_EVIDENCE.md"
    target.write_text(target.read_text().replace("Make honesty cheap.", "Make honesty cheap and durable."))
    run_ct(["lock"], cwd=str(tmp_repo), ct_path=ct_path)
    s = run_ct(["session-status", "--manifest", str(manifest), "--task", task],
               cwd=str(tmp_repo), ct_path=ct_path)
    assert s.returncode != 0
    assert "STALE" in s.stdout
    assert "re-attest and re-commit" in s.stdout


def test_task_change_requires_reresolution(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    assert run_ct(_commit_args(manifest, task, impact), cwd=str(tmp_repo), ct_path=ct_path).returncode == 0
    s = run_ct(["session-status", "--manifest", str(manifest)],
               cwd=str(tmp_repo), ct_path=ct_path)
    # same task → still ACTIVE
    assert s.returncode == 0
    # rewrite the recorded task to one that triggers more; simulate scope expansion
    art_path = next((artifact_dir(tmp_repo)).glob("session-*.json"))
    art = json.loads(art_path.read_text())
    art["task_fingerprint"] = "rotate the deploy credentials and update the health checks"
    art_path.write_text(json.dumps(art))
    s2 = run_ct(["session-status", "--manifest", str(manifest)], cwd=str(tmp_repo), ct_path=ct_path)
    assert s2.returncode != 0
    assert "additional contracts not in the commitment" in s2.stdout
    assert "least-privilege" in s2.stdout


def test_worker_commitment_requires_parent_bundle(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    r = run_ct(_commit_args(manifest, task, impact, extra=["--worker"]),
               cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode != 0
    assert "parent-bundle" in r.stderr or "inherited bundle" in r.stderr


def test_worker_rejects_invented_parent_hash(tmp_repo):
    """Real inheritance (hardening #3): a worker may not claim an arbitrary parent
    hash — the parent bundle must exist as a recorded commitment."""
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    fake = "f" * 64
    r = run_ct(_commit_args(manifest, task, impact, extra=["--worker", "--parent-bundle", fake]),
               cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode != 0
    assert "parent bundle not found" in r.stderr


def test_worker_commitment_inherits_real_parent(tmp_repo):
    """End-to-end propagation: orchestrator commits first; worker inherits its
    recorded bundle; inheritance lines appear; parent constraints preserved."""
    ct = _load_ct_from(tmp_repo)
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    # 1. orchestrator commits on a broad task
    orch_task = "rotate the deploy credentials and update the health checks"
    r0 = run_ct(_commit_args(manifest, orch_task, _IMPACT_OK, extra=["--role", "orchestrator"]),
                cwd=str(tmp_repo), ct_path=ct_path)
    assert r0.returncode == 0, r0.stdout + r0.stderr
    orch_art = json.loads(
        next((artifact_dir(tmp_repo)).glob("orchestrator-*.json")).read_text())
    parent_sha = orch_art["bundle_sha256"]

    # 2. worker with a narrower task inherits the orchestrator's bundle;
    #    inherited contracts join the resolved set (union — dropping is impossible)
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    impact["least-privilege"] = "inherited from parent: deploy token scoped to the deploy job"
    r = run_ct(_commit_args(manifest, task, impact, extra=["--worker", "--parent-bundle", parent_sha]),
               cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "INHERITED CONTRACT BUNDLE:" in r.stdout
    assert "PARENT CONTRACT COMMITMENT: ACTIVE" in r.stdout
    art_path = next((artifact_dir(tmp_repo)).glob("worker-*.json"))
    art = json.loads(art_path.read_text())
    assert art["role"] == "worker"
    assert art["inherited_bundle"] == parent_sha
    # the parent's whole applicable set is preserved via the union
    for cid in ("truth-and-evidence", "explicit-state", "recovery-and-reversibility",
                "provenance-and-audit", "least-privilege"):
        assert cid in art["contracts"]
    # worker artifact verifies: parent recorded + no dropped constraints
    errs = ct.verify_commitment_artifact(art, manifest)
    assert errs == [], errs


def test_worker_attestation_covers_exact_union(tmp_repo):
    """Hardening: the contract set ATTESTED must be exactly the set COMMITTED.
    A worker inherits a parent-only contract (least-privilege); that inherited
    contract must appear in the worker's attestation, and the attested set
    must equal the committed set — including the parent-only contract."""
    ct = _load_ct_from(tmp_repo)
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    # orchestrator on a broad task resolves least-privilege (credentials trigger)
    orch_task = "rotate the deploy credentials and update the health checks"
    r0 = run_ct(_commit_args(manifest, orch_task, _IMPACT_OK, extra=["--role", "orchestrator"]),
                cwd=str(tmp_repo), ct_path=ct_path)
    assert r0.returncode == 0, r0.stdout + r0.stderr
    parent_sha = json.loads(
        next((artifact_dir(tmp_repo)).glob("orchestrator-*.json")).read_text())["bundle_sha256"]

    # worker's own task does NOT trigger least-privilege...
    worker_task = "update a compose file"
    own = set(ct.resolve_set(ct.load_adoption(manifest), worker_task)["selected"])
    assert "least-privilege" not in own
    # ...so when it inherits, least-privilege is a parent-only addition
    impact = {cid: "applied" for cid in own}
    impact["least-privilege"] = "inherited: deploy token scoped to the deploy job"
    # capture the attestation the worker's commitment used
    atts = {}
    orig_make_attestation = ct.make_attestation
    def spy(mpath, task, task_impact, revision="uncommitted", format_text=True,
            task_tags=None, resolved_ids=None):
        out = orig_make_attestation(mpath, task, task_impact, revision, format_text,
                                    task_tags, resolved_ids)
        if not format_text:
            atts["resolved_ids"] = resolved_ids
            atts["loaded"] = {e["contract_id"] for e in out["loaded"]}
        return out
    ct.make_attestation = spy
    try:
        w_art, _ = ct.build_commitment(manifest, worker_task, impact, role="worker",
                                      parent_bundle=parent_sha, worker=True)
    finally:
        ct.make_attestation = orig_make_attestation
    # inherited parent-only contract IS in the attested set and committed set
    assert "least-privilege" in atts["loaded"]
    assert atts["loaded"] == set(w_art["contracts"]), "attested set != committed set"
    assert atts["resolved_ids"] is not None and set(atts["resolved_ids"]) == atts["loaded"]


def test_worker_missing_impact_for_inherited_contract_blocks(tmp_repo):
    """Missing task-impact for an inherited (parent-only) contract blocks
    attestation/commitment — inherited contracts are attested, not assumed."""
    ct = _load_ct_from(tmp_repo)
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    orch_task = "rotate the deploy credentials and update the health checks"
    orch_art, _ = ct.build_commitment(manifest, orch_task, dict(_IMPACT_OK), role="orchestrator")
    ct.write_session_artifact(orch_art)
    worker_task = "update a compose file"
    own = set(ct.resolve_set(ct.load_adoption(manifest), worker_task)["selected"])
    assert "least-privilege" not in own
    w_impact = {cid: "applied" for cid in own}  # NO impact for least-privilege
    import pytest as _pq
    with _pq.raises(ct.CTError) as exc:
        ct.build_commitment(manifest, worker_task, w_impact, role="worker",
                            parent_bundle=orch_art["bundle_sha256"], worker=True)
    assert "least-privilege" in str(exc.value)


def test_worker_cannot_drop_parent_constraints(tmp_repo):
    """A worker claiming inheritance without acknowledging the inherited contracts
    is rejected — the union is forced, so weakening requires explicit refusal
    (which fails closed), not silent omission."""
    ct = _load_ct_from(tmp_repo)
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    # orchestrator commits on the credentials task (resolves least-privilege too)
    orch_task = "rotate the deploy credentials and update the health checks"
    orch_art, _ = ct.build_commitment(manifest, orch_task, dict(_IMPACT_OK), role="orchestrator")
    ct.write_session_artifact(orch_art)
    # a worker claims inheritance but does not acknowledge least-privilege's impact
    worker_task = "update a compose file"  # does not itself trigger least-privilege
    w_impact = {cid: "applied" for cid in
                ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    import pytest as _pq
    with _pq.raises(ct.CTError) as exc:
        ct.build_commitment(manifest, worker_task, w_impact, role="worker",
                            parent_bundle=orch_art["bundle_sha256"], worker=True)
    assert "inherited contracts need task-impact" in str(exc.value) or "least-privilege" in str(exc.value)


def test_session_safe_keyed_artifacts(tmp_repo):
    """Parallel lanes get distinct artifacts (hardening #4) — no global singleton."""
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    t1 = "update a compose file"
    t2 = "rotate the deploy credentials and update the health checks"
    i1 = {cid: "applied" for cid in
          ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    assert run_ct(_commit_args(manifest, t1, i1), cwd=str(tmp_repo), ct_path=ct_path).returncode == 0
    assert run_ct(_commit_args(manifest, t2, _IMPACT_OK), cwd=str(tmp_repo), ct_path=ct_path).returncode == 0
    arts = list((artifact_dir(tmp_repo)).glob("session-*.json"))
    assert len(arts) == 2  # keyed by task; both coexist
    # status default picks the newest, but keyed lookup finds each
    s1 = run_ct(["session-status", "--manifest", str(manifest), "--task", t1], cwd=str(tmp_repo), ct_path=ct_path)
    s2 = run_ct(["session-status", "--manifest", str(manifest), "--task", t2], cwd=str(tmp_repo), ct_path=ct_path)
    assert s1.returncode == 0 and s2.returncode == 0
    assert t1 in s1.stdout and t2 in s2.stdout


def test_session_isolation_across_projects(tmp_repo, tmp_path):
    """Hardening: two consuming PROJECTS with identical task strings and roles
    produce distinct commitment state — artifacts live in the consuming
    project's context, never a global library path."""
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    task = "identical integration task"
    role = "session"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility",
               "provenance-and-audit", "ask-for-help")}
    # two consumer projects, each with its own .contracts/ adoption manifest
    proj_a = tmp_path / "project-a"
    proj_b = tmp_path / "project-b"
    for proj in (proj_a, proj_b):
        (proj / ".contracts").mkdir(parents=True)
        shutil.copy(tmp_repo / "examples" / "homelab.adoption.yaml",
                    proj / ".contracts" / "adoption.yaml")
    for proj in (proj_a, proj_b):
        r = run_ct(_commit_args(proj / ".contracts" / "adoption.yaml", task, impact),
                   cwd=str(proj), ct_path=ct_path)
        assert r.returncode == 0, r.stdout + r.stderr
    # distinct artifact files in each project's own context
    art_a = json.loads(next((proj_a / ".contracts" / "sessions").glob(f"{role}-*.json")).read_text())
    art_b = json.loads(next((proj_b / ".contracts" / "sessions").glob(f"{role}-*.json")).read_text())
    assert art_a["session_dir"] != art_b["session_dir"]
    assert str(proj_a) in art_a["session_dir"] and str(proj_b) not in art_a["session_dir"]
    assert str(proj_b) in art_b["session_dir"] and str(proj_a) not in art_b["session_dir"]
    # the library checkout itself stays untouched — no workflow-state singleton
    assert not (tmp_repo / ".contract-commitments").exists() or \
        not list((tmp_repo / ".contract-commitments").glob(f"{role}-*.json"))
    # worktree isolation: CONTRACTCTL_SESSION_DIR pins a private dir per lane
    lane_dir = tmp_path / "lane-wt" / "sessions"
    r = run_ct(_commit_args(proj_a / ".contracts" / "adoption.yaml", task, impact),
               cwd=str(proj_a), ct_path=ct_path,
               env={"CONTRACTCTL_SESSION_DIR": str(lane_dir)})
    assert r.returncode == 0
    assert (lane_dir / f"{role}-{re.sub(r'[^a-z0-9-]+', '-', task.lower()).strip('-')[:48]}.json").is_file()


def test_attestation_fails_closed_on_lock_drift(tmp_repo):
    """Hardening #5: attestation cannot be produced against a drifted lockfile."""
    ct = _load_ct_from(tmp_repo)
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    # corrupt the lockfile (simulate drift)
    lock = tmp_repo / "contracts.lock.json"
    data = json.loads(lock.read_text())
    data["contracts"][0]["sha256"] = "0" * 64
    lock.write_text(json.dumps(data))
    import pytest as _pq
    with _pq.raises(ct.CTError) as exc:
        ct.make_attestation(manifest, "update a compose file",
                            {c: "x" for c in ("truth-and-evidence", "explicit-state",
                                              "recovery-and-reversibility", "provenance-and-audit")})
    assert "lockfile drift" in str(exc.value)


def test_commit_impact_file(tmp_repo):
    """Hardening #6: commit --impact-file parses 'id = sentence' lines."""
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    impact_file = tmp_repo / "impact.txt"
    impact_file.write_text(
        "truth-and-evidence = unknown stays unknown\n"
        "explicit-state = vocabulary with observed_at\n"
        "recovery-and-reversibility = rollback documented\n"
        "provenance-and-audit = journaled with actor\n"
        "ask-for-help = provider semantics asked, not guessed\n"
        "# comment line ignored\n"
    )
    r = run_ct(["commit", "--manifest", str(manifest),
                "--task", "update a compose file",
                "--impact-file", str(impact_file)],
               cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "CONTRACT COMMITMENT: ACTIVE" in r.stdout


def test_commitment_hash_mismatch_prevents_active(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit", "ask-for-help")}
    # corrupt the lockfile: a selected contract's hash no longer matches the file
    lock = tmp_repo / "contracts.lock.json"
    data = json.loads(lock.read_text())
    for e in data["contracts"]:
        if e["id"] == "truth-and-evidence":
            e["sha256"] = "0" * 64
    lock.write_text(json.dumps(data))
    r = run_ct(_commit_args(manifest, task, impact), cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode != 0
    assert "hash mismatch" in r.stderr or "BLOCKED" in r.stderr


def test_session_status_inactive_when_no_artifact(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    s = run_ct(["session-status"], cwd=str(tmp_repo), ct_path=ct_path)
    assert s.returncode == 1
    assert "INACTIVE" in s.stdout


# --------------------------------------------------------------- receipt rotation enforcement

def test_receipt_rotation_enforced_for_meaningful_changes(tmp_repo):
    """Git-history rule: a canonical contract whose version changed MINOR/MAJOR
    (meaningful) without rotating its receipt fails validation."""
    ct = _load_ct_from(tmp_repo)
    # HEAD has play-nice-together @1.1.0 with the rotated receipt. Bump the
    # version MINOR again WITHOUT rotating the receipt -> violation.
    target = tmp_repo / "contracts" / "core" / "PLAY_NICE_TOGETHER.md"
    text = target.read_text()
    assert "version: 1.1.0" in text
    target.write_text(text.replace("version: 1.1.0", "version: 1.2.0")
                      .replace("Make honesty cheap.", "Make honesty cheap and durable."))
    errors = ct.check_receipt_rotation(ct.load_library())
    assert any("receipt did not rotate" in e and "PLAY_NICE" in e for e in errors), errors


def test_receipt_rotation_not_required_for_patch(tmp_repo):
    """PATCH-clarification content changes do not require receipt rotation."""
    ct = _load_ct_from(tmp_repo)
    target = tmp_repo / "contracts" / "core" / "TRUTH_AND_EVIDENCE.md"
    text = target.read_text()
    assert "version: 1.0.0" in text
    target.write_text(text.replace("version: 1.0.0", "version: 1.0.1")
                      .replace("Make honesty cheap.", "Make honesty cheap and durable."))
    errors = ct.check_receipt_rotation(ct.load_library())
    assert not any("TRUTH_AND_EVIDENCE" in e for e in errors), errors


def test_receipt_rotation_clean_when_compliant(tmp_repo):
    """No false positives on the current tree (rotations done correctly)."""
    ct = _load_ct_from(tmp_repo)
    errors = ct.check_receipt_rotation(ct.load_library())
    assert errors == [], errors


# --------------------------------------------------------------- ask-for-help

def test_ask_for_help_contract_exists(lib):
    ids = {c["front_matter"]["contract_id"] for c in lib.load_library()}
    assert "ask-for-help" in ids
    c = [x for x in lib.load_library() if x["front_matter"]["contract_id"] == "ask-for-help"][0]
    assert c["front_matter"]["layer"] == "core"
    assert c["receipts"] == ["vellum-harbor-quill"]
    for concept in ("NEEDS_HELP", "WAITING_FOR_HELP", "recommendation"):
        assert concept in c["text"]


def test_play_nice_references_ask_for_help(lib):
    c = [x for x in lib.load_library() if x["front_matter"]["contract_id"] == "play-nice-together"][0]
    assert "Ask for Help" in c["text"]
    assert c["front_matter"]["version"] == "1.1.0"


GOOD_QUESTION = {
    "schema": "play-nice/question-v1",
    "question_id": "q-01842",
    "status": "WAITING",
    "requester": {"type": "agent", "id": "frontend-worker"},
    "target": {"type": "human", "role": "owner"},
    "reason": "Two approved visual references disagree about navigation placement.",
    "question": "Which navigation composition should govern the Settings screen?",
    "choices": [{"id": "rail", "label": "Left rail"}, {"id": "top-nav", "label": "Top navigation"}],
    "recommended": "rail",
    "recommendation_reason": "It matches the newer approved desktop frame.",
    "blocking": True,
    "safe_to_continue_without_answer": False,
    "affected_scope": ["SettingsScreen"],
    "evidence": ["design/screens/settings-desktop.png"],
    "created_at": "2026-09-11T14:00:00Z",
}


def test_validate_question_good(tmp_path):
    q = tmp_path / "q.json"
    q.write_text(json.dumps(GOOD_QUESTION))
    r = run_ct(["validate-question", str(q)])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "QUESTION VALID" in r.stdout


def test_validate_question_bad(tmp_path):
    bad = dict(GOOD_QUESTION)
    bad.pop("question")
    q = tmp_path / "q.json"
    q.write_text(json.dumps(bad))
    r = run_ct(["validate-question", str(q)])
    assert r.returncode != 0
    assert "missing required field 'question'" in r.stdout

    bad2 = dict(GOOD_QUESTION)
    bad2["schema"] = "play-nice/not-a-schema"
    q2 = tmp_path / "q2.json"
    q2.write_text(json.dumps(bad2))
    r2 = run_ct(["validate-question", str(q2)])
    assert r2.returncode != 0

    bad3 = dict(GOOD_QUESTION)
    bad3["recommended"] = "not-a-choice"
    q3 = tmp_path / "q3.json"
    q3.write_text(json.dumps(bad3))
    r3 = run_ct(["validate-question", str(q3)])
    assert r3.returncode != 0
    assert "not one of the choice ids" in r3.stdout


def test_validate_question_secret_shapes_rejected(tmp_path):
    bad = dict(GOOD_QUESTION)
    bad["context"] = {"api_key": "sk-something-realistic"}
    q = tmp_path / "q.json"
    q.write_text(json.dumps(bad))
    r = run_ct(["validate-question", str(q)])
    assert r.returncode != 0
    assert "possible inline secret" in r.stdout


def test_validate_help_request_requires_capability(tmp_path):
    req = {
        "schema": "play-nice/help-request-v1",
        "question_id": "help-442",
        "status": "OPEN",
        "requester": {"type": "worker", "id": "glm-worker-3"},
        "target": {"type": "agent", "id": "browser-specialist"},
        "question": "Compare live Settings composition against current design reference.",
        "blocking": True,
        "created_at": "2026-09-11T14:00:00Z",
    }
    q = tmp_path / "req.json"
    q.write_text(json.dumps(req))
    r = run_ct(["validate-question", str(q)])
    assert r.returncode != 0
    assert "needed_capability" in r.stdout
    req["needed_capability"] = "browser-visual-inspection"
    q.write_text(json.dumps(req))
    r2 = run_ct(["validate-question", str(q)])
    assert r2.returncode == 0, r2.stdout + r2.stderr


def test_validate_help_response(tmp_path):
    resp = {
        "schema": "play-nice/help-response-v1",
        "question_id": "help-442",
        "status": "answered",
        "requester": {"type": "worker", "id": "glm-worker-3"},
        "target": {"type": "agent", "id": "browser-specialist"},
        "question": "Compare live Settings composition against current design reference.",
        "result": {"summary": "Live screen uses card-per-section; reference uses grouped rows."},
        "confidence": "high",
        "blocking": False,
        "safe_to_continue_without_answer": True,
        "created_at": "2026-09-11T14:05:00Z",
    }
    q = tmp_path / "resp.json"
    q.write_text(json.dumps(resp))
    r = run_ct(["validate-question", str(q)])
    assert r.returncode == 0, r.stdout + r.stderr


def test_question_lifecycle_states_in_schema():
    schema = json.loads((REPO / "schema" / "question.schema.json").read_text())
    states = schema["properties"]["status"]["enum"]
    for s in ("OPEN", "WAITING", "ANSWERED", "DECLINED", "EXPIRED", "SUPERSEDED", "CANCELLED"):
        assert s in states
    # answers are never authorization — documented
    assert "NEVER authorization" in schema["properties"]["answer"]["description"]


# --------------------------------------------------------------- stale pins

def test_stale_pin_detected(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    m = tmp_repo / "examples" / "vefr.adoption.yaml"
    m.write_text(m.read_text().replace("revision: 0000000", "revision: deadbeef"))
    v = run_ct(["adopt", "--manifest", str(m)], cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode != 0
    assert "stale pin" in v.stdout


def test_fresh_pin_passes(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    m = tmp_repo / "examples" / "vefr.adoption.yaml"
    # a fresh pin uses the library's git revision (semver VERSION is not the pin)
    m.write_text(m.read_text().replace("revision: 0000000", f"revision: {ct.library_revision()}"))
    v = run_ct(["adopt", "--manifest", str(m)], cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode == 0, v.stdout + v.stderr


# --------------------------------------------------------------- offline + CLI

def test_offline_validation_works():
    # contractctl uses only stdlib + local files; validate runs with no network
    r = run_ct(["validate"])
    assert r.returncode == 0
    assert "VALID" in r.stdout


def test_cli_status():
    r = run_ct(["status"])
    assert r.returncode == 0
    assert "contracts: 61" in r.stdout


def test_cli_show():
    r = run_ct(["show", "truth-and-evidence"])
    assert r.returncode == 0
    assert "contract-receipt: wren-loam-sail" in r.stdout


def test_cli_list():
    r = run_ct(["list"])
    assert r.returncode == 0
    assert "truth-and-evidence" in r.stdout


def test_cli_show_unknown():
    r = run_ct(["show", "not-a-thing"])
    assert r.returncode != 0


# --------------------------------------------------------------- privacy

def test_no_secrets_or_private_material():
    # built by concatenation so this scanner's own banned list does not
    # contain the literal shapes it scans for
    banned = [
        # credential shapes (realistic prefixes)
        "gh" + "p_", "gh" + "o_", "AK" + "IA",
        "BEGIN PRIVATE " + "KEY", "BEGIN " + "RSA",
        # private topology from the homelab
        "192.168" + ".", "hulganfamily.duck" + "dns.org", "10.0" + ".",
    ]
    for f in REPO.rglob("*"):
        if not f.is_file() or ".git" in f.parts or "tests" in f.parts or ".venv" in f.parts:
            continue
        try:
            text = f.read_text()
        except (UnicodeDecodeError, ValueError):
            continue
        for b in banned:
            assert b not in text, f"{f.relative_to(REPO)} contains {b!r}"


def test_no_medical_history():
    # engineering requirements are fine; personal diagnoses are not
    banned_words = ["hemiplegic", "cluster headache", "my diagnosis", "my medication",
                    "dyslexic migraine", "I have migraines", "Rylee has"]
    for f in REPO.rglob("*.md"):
        if ".git" in f.parts:
            continue
        text = f.read_text()
        low = text.lower()
        for b in banned_words:
            assert b.lower() not in low, f"{f.relative_to(REPO)} contains {b!r}"