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
    """A copy of the library for mutation tests (keeps the real tree safe)."""
    dest = tmp_path / "play-nice-contracts"
    shutil.copytree(REPO, dest / "play-nice-contracts", symlinks=True)
    # contractctl resolves REPO_ROOT from its own path; run against the copy
    ct_path = dest / "play-nice-contracts" / "tools" / "contractctl" / "contractctl.py"
    (dest / "play-nice-contracts" / ".tests-ct-path").write_text(str(ct_path))
    yield dest / "play-nice-contracts"


def run_ct(args, cwd=None, ct_path=None):
    ct = ct_path or CT
    return subprocess.run(
        [sys.executable, str(ct), *args],
        capture_output=True, text=True, cwd=cwd or str(REPO), timeout=60,
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
    assert len(lib.load_library()) == 60


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
    text = text.replace("timber-juniper-velvet", "driftwood-thicket-jetty")
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
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
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
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
    r = _attest(tmp_repo, manifest, task, impact, ct_path)
    assert "PASS" in r.stdout
    att = tmp_repo / "att.txt"
    att.write_text(r.stdout)
    # corrupt one hash in the lockfile underneath
    lock = tmp_repo / "contracts.lock.json"
    data = json.loads(lock.read_text())
    for e in data["contracts"]:
        if e["id"] == "explicit-state":
            e["sha256"] = "0" * 64
    lock.write_text(json.dumps(data))
    v = run_ct(["verify-attestation", str(att)], cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode != 0
    assert "wrong hash" in v.stdout or "bundle receipt mismatch" in v.stdout


def test_omitted_mandatory_contract_fails_verification(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
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
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
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
    res = ct.resolve_set(m, task="x")
    # fabricate an attestation with a CONFLICT and verify it parses + gates BLOCKED
    text = f"""CONTRACT_ATTESTATION v1

bundle:
  revision: test
  receipt: {ct.bundle_receipt(ct.load_lock())}

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
    art = json.loads((tmp_repo / ".contract-commitment.json").read_text())
    lock = ct.load_lock()
    assert art["bundle_receipt"] == ct.bundle_receipt(lock)
    assert art["bundle_sha256"] == ct.bundle_sha256(lock)
    assert art["contract_gate"] == "PASS"
    assert art["commitment"] == "ACTIVE"
    assert set(art["contracts"]) == {
        "truth-and-evidence", "explicit-state", "recovery-and-reversibility",
        "provenance-and-audit", "least-privilege"}
    # no secrets by construction: artifact only carries ids/hashes/words
    blob = json.dumps(art).lower()
    for bad in ("token", "secret", "password", "api_key"):
        assert bad not in blob or bad in ("task",)  # task text mentions credentials, fine


def test_stale_bundle_invalidates_commitment(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "rotate the deploy credentials and update the health checks"
    assert run_ct(_commit_args(manifest, task, _IMPACT_OK), cwd=str(tmp_repo), ct_path=ct_path).returncode == 0
    # change the library → relock → commitment must go STALE
    target = tmp_repo / "contracts" / "core" / "TRUTH_AND_EVIDENCE.md"
    target.write_text(target.read_text().replace("Make honesty cheap.", "Make honesty cheap and durable."))
    run_ct(["lock"], cwd=str(tmp_repo), ct_path=ct_path)
    s = run_ct(["session-status"], cwd=str(tmp_repo), ct_path=ct_path)
    assert s.returncode != 0
    assert "STALE" in s.stdout
    assert "re-attest and re-commit" in s.stdout


def test_task_change_requires_reresolution(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
    assert run_ct(_commit_args(manifest, task, impact), cwd=str(tmp_repo), ct_path=ct_path).returncode == 0
    # now the SAME session's task text triggers additional contracts (credentials → least-privilege)
    s = run_ct(["session-status", "--manifest", str(manifest)],
               cwd=str(tmp_repo), ct_path=ct_path)
    # same task → still ACTIVE
    assert s.returncode == 0
    # rewrite the recorded task to one that triggers more; simulate scope expansion
    art_path = tmp_repo / ".contract-commitment.json"
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
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
    r = run_ct(_commit_args(manifest, task, impact, extra=["--worker"]),
               cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode != 0
    assert "parent-bundle" in r.stderr or "inherited bundle" in r.stderr


def test_worker_commitment_inherits_bundle(tmp_repo):
    ct = _load_ct_from(tmp_repo)
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
    parent = ct.bundle_sha256(ct.load_lock())
    r = run_ct(_commit_args(manifest, task, impact, extra=["--worker", "--parent-bundle", parent]),
               cwd=str(tmp_repo), ct_path=ct_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "INHERITED CONTRACT BUNDLE:" in r.stdout
    assert "PARENT CONTRACT COMMITMENT: ACTIVE" in r.stdout
    art = json.loads((tmp_repo / ".contract-commitment.json").read_text())
    assert art["role"] == "worker"
    assert art["inherited_bundle"] == parent


def test_commitment_may_strengthen_not_weaken(tmp_repo):
    """Worker resolving MORE contracts than the parent is allowed; fewer is a defect
    detectable at integration review. Tooling check: artifact records the full
    resolved set, so a parent can diff inherited vs actual."""
    ct = _load_ct_from(tmp_repo)
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    # parent (orchestrator) committed with a broader task
    orch_impact = dict(_IMPACT_OK)
    orch_task = "rotate the deploy credentials and update the health checks"
    art, _ = ct.build_commitment(manifest, orch_task, orch_impact)
    assert "least-privilege" in art["contracts"]
    # worker with the narrower compose task still carries ALL mandatory (always) contracts
    worker_task = "update a compose file"
    w_impact = {cid: "applied" for cid in
                ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
    w_art, _ = ct.build_commitment(manifest, worker_task, w_impact, role="worker",
                                   parent_bundle=art["bundle_sha256"])
    # always-contracts survive the narrowing — a worker may not lose the floor
    for floor_cid in ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit"):
        assert floor_cid in w_art["contracts"]


def test_commitment_hash_mismatch_prevents_active(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    manifest = tmp_repo / "examples" / "homelab.adoption.yaml"
    task = "update a compose file"
    impact = {cid: "applied" for cid in
              ("truth-and-evidence", "explicit-state", "recovery-and-reversibility", "provenance-and-audit")}
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


# --------------------------------------------------------------- stale pins

def test_stale_pin_detected(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    m = tmp_repo / "examples" / "vefr.adoption.yaml"
    m.write_text(m.read_text().replace("revision: 0000000", "revision: deadbeef"))
    v = run_ct(["adopt", "--manifest", str(m)], cwd=str(tmp_repo), ct_path=ct_path)
    assert v.returncode != 0
    assert "stale pin" in v.stdout


def test_fresh_pin_passes(tmp_repo):
    ct_path = tmp_repo / "tools" / "contractctl" / "contractctl.py"
    m = tmp_repo / "examples" / "vefr.adoption.yaml"
    m.write_text(m.read_text().replace("revision: 0000000", "revision: 0.1.0"))
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
    assert "contracts: 60" in r.stdout


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
    banned = [
        # credential shapes (realistic prefixes; example-marked forms allowed)
        "ghp_", "gho_", "AKIA", "BEGIN PRIVATE KEY", "BEGIN RSA",
        # private topology from the homelab
        "192.168.", "hulganfamily.duckdns.org", "10.0.",
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