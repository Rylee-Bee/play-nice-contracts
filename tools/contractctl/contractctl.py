#!/usr/bin/env python3
"""contractctl — resolve, validate, lock, and attest play-nice contracts.

Minimal-dependency (stdlib-only) CLI for the play-nice-contracts library.

Subcommands:
  list                  list contracts (id, version, status, layer)
  show <id>             print a contract's canonical content
  validate              validate the whole library (schemas, receipts, index)
  resolve               resolve the applicable contract set for a task
  lock                  generate contracts.lock.json (deterministic)
  attest                produce a CONTRACT_ATTESTATION v1 block
  verify-attestation    re-verify an attestation against the library
  adopt                 validate a project adoption manifest
  status                one-line library health summary

Run with --help or <subcommand> --help for details.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACTS_DIR = REPO_ROOT / "contracts"
SCHEMA_DIR = REPO_ROOT / "schema"
LOCKFILE = REPO_ROOT / "contracts.lock.json"
INDEX_FILE = REPO_ROOT / "CONTRACT_INDEX.md"
VERSION_FILE = REPO_ROOT / "VERSION"
QUESTION_SCHEMA = SCHEMA_DIR / "question.schema.json"

FM_DELIM = "---"
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
RECEIPT_RE = re.compile(r"<!--\s*contract-receipt:\s*([a-z]+(?:-[a-z]+){2})\s*-->")
CONTRACT_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
LAYER_DIRS = {
    "core": "core",
    "human": "human",
    "experience": "experience",
    "interoperability": "interoperability",
    "security": "security",
    "engineering": "engineering",
    "agents": "agents",
    "interfaces": "interfaces",
}
VALID_STATUS = {"canonical", "draft", "deprecated", "retired"}
ATTEST_STATUSES = {"ACCEPTED", "CONFLICT", "N/A"}

ATTESTATION_FORMAT = "CONTRACT_ATTESTATION v1"


class CTError(Exception):
    """A contractctl failure with a stable message."""


# ---------------------------------------------------------------- yaml subset
# Minimal YAML front-matter parser for the shapes this library actually uses.
# Supports: nested maps, lists of scalars, one level of list-of-maps, scalars.

def _parse_scalar(s: str):
    s = s.strip()
    # strip trailing YAML comments (unquoted ' #' to end of line)
    if " #" in s and not s.startswith('"'):
        s = s.split(" #", 1)[0].strip()
    if s in ("null", "~", ""):
        return None
    if s == "none":
        return "none"  # keep the literal; conflicts: none is meaningful
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(p.strip()) for p in inner.split(",")]
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        return s[1:-1]
    return s


def _yaml_block_to_dict(lines: list[str], indent_stack=None) -> dict:
    """Parse a small YAML subset: mapping keys, nested via indentation."""
    out: dict = {}
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            raise CTError(f"yaml: cannot parse line: {line!r}")
        indent, key, rest = m.group(1), m.group(2), m.group(3).strip()
        if rest in (">-", ">", "|-", "|", ">"):
            # folded/literal block scalar: consume deeper-indented lines
            child_indent = len(indent)
            block: list[str] = []
            j = i + 1
            while j < n:
                nxt = lines[j]
                if nxt.strip() == "":
                    block.append(nxt)
                    j += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip())
                if nxt_indent <= child_indent:
                    break
                block.append(nxt.strip())
                j += 1
            joined = " ".join(block).strip()
            out[key] = " ".join(joined.split())
            i = j
            continue
        if rest:
            out[key] = _parse_scalar(rest)
            i += 1
            continue
        # child block: collect lines deeper than this key's indent
        child_indent = len(indent)
        block: list[str] = []
        j = i + 1
        while j < n:
            nxt = lines[j]
            if nxt.strip() == "":
                block.append(nxt)
                j += 1
                continue
            nxt_indent = len(nxt) - len(nxt.lstrip())
            if nxt_indent <= child_indent:
                break
            block.append(nxt)
            j += 1
        # list or map child? A block is a list only if its first
        # non-empty line is a dash item; otherwise it is a map whose
        # values may themselves be lists (map-of-lists).
        first = next((b for b in block if b.strip() and not b.lstrip().startswith("#")), "")
        if re.match(r"^\s*-\s", first):
            out[key] = _yaml_list(block)
        else:
            out[key] = _yaml_block_to_dict(block)
        i = j
    return out


def _yaml_list(block: list[str]):
    """Parse a list whose items are '- scalar' or '- key: val' map items,
    including nested lists/maps inside those items (indentation-based)."""
    items: list = []
    i = 0
    n = len(block)
    while i < n:
        line = block[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^(\s*)-\s+(.*)$", line)
        if not m:
            raise CTError(f"yaml: cannot parse list line: {line!r}")
        dash_indent, rest = len(m.group(1)), m.group(2)
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", rest)
        if not kv:
            items.append(_parse_scalar(rest))
            i += 1
            continue
        # map item: collect this item's lines (deeper than the dash, or
        # continuation keys at the item's key indent) until the next dash item
        item_indent = dash_indent + 2
        item_lines = [rest]
        j = i + 1
        while j < n:
            nxt = block[j]
            if nxt.strip() == "":
                j += 1
                continue
            nxt_indent = len(nxt) - len(nxt.lstrip())
            if nxt_indent <= dash_indent and re.match(r"^\s*-\s", nxt):
                break
            if nxt_indent < item_indent:
                break
            item_lines.append(nxt)
            j += 1
        # parse the item as a mini-document starting at the key
        items.append(_yaml_block_to_dict([" " * item_indent + l if k else l for k, l in enumerate(item_lines)]))
        i = j
    return items


def parse_front_matter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        raise CTError("front matter: missing '---' delimited YAML header")
    lines = m.group(1).split("\n")
    data = _yaml_block_to_dict(lines)
    # 'applies'/'triggers' etc. may be inline lists from _parse_scalar already
    return data


# ---------------------------------------------------------------- discovery

def find_contract_files() -> list[Path]:
    files = []
    for layer, dirname in LAYER_DIRS.items():
        d = CONTRACTS_DIR / dirname
        if d.is_dir():
            files.extend(d.glob("*.md"))
    return sorted(files)


def parse_contract_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        fm = parse_front_matter(text)
    except CTError as e:
        raise CTError(f"{path.relative_to(REPO_ROOT)}: {e}")
    receipts = RECEIPT_RE.findall(text)
    return {
        "path": path,
        "rel_path": str(path.relative_to(REPO_ROOT)),
        "front_matter": fm,
        "receipts": receipts,  # all receipt comments in the file
        "text": text,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def load_library() -> list[dict]:
    out = []
    for f in find_contract_files():
        out.append(parse_contract_file(f))
    return out


# ---------------------------------------------------------------- validation

def validate_library(lib: list[dict] | None = None) -> list[str]:
    errors: list[str] = []
    if lib is None:
        lib = load_library()
    if not lib:
        return ["library: no contracts found under contracts/"]

    seen_ids: dict[str, str] = {}
    seen_receipts: dict[str, str] = {}
    fm_contract_schema = _load_json_schema("contract.schema.json")

    for c in lib:
        fm = c["front_matter"]
        p = c["rel_path"]

        # required keys + types per contract.schema.json (structural re-check)
        for key in ("contract_id", "title", "version", "status"):
            if key not in fm:
                errors.append(f"{p}: front matter missing required key '{key}'")
        if errors and errors[-1].startswith(f"{p}: front matter missing"):
            continue

        cid = fm.get("contract_id", "")
        version = str(fm.get("version", ""))
        status = fm.get("status", "")

        if not CONTRACT_ID_RE.match(str(cid)):
            errors.append(f"{p}: invalid contract_id {cid!r}")
        if not SEMVER_RE.match(version):
            errors.append(f"{p}: invalid version {version!r}")
        if status not in VALID_STATUS:
            errors.append(f"{p}: invalid status {status!r} (valid: {sorted(VALID_STATUS)})")
        layer = fm.get("layer", "")
        if layer not in LAYER_DIRS:
            errors.append(f"{p}: missing/invalid layer {layer!r}")

        # filename should match id
        stem = c["path"].stem
        expected = str(cid).upper().replace("-", "_")
        if stem != expected:
            errors.append(f"{p}: filename {stem}.md does not match contract_id {cid}")

        # id uniqueness
        if cid in seen_ids:
            errors.append(f"{p}: duplicate contract_id {cid} (also {seen_ids[cid]})")
        else:
            seen_ids[cid] = p

        # receipt: exactly one, in canonical form, unique across library
        if len(c["receipts"]) == 0:
            errors.append(f"{p}: missing receipt comment (<!-- contract-receipt: word-word-word -->)")
        elif len(c["receipts"]) > 1:
            errors.append(f"{p}: multiple receipt comments found ({c['receipts']})")
        else:
            r = c["receipts"][0]
            if r in seen_receipts:
                errors.append(f"{p}: duplicate receipt {r} (also in {seen_receipts[r]})")
            else:
                seen_receipts[r] = p

        # applies/triggers shape
        for key in ("applies", "triggers"):
            v = fm.get(key)
            if v is None:
                continue
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                errors.append(f"{p}: '{key}' must be a list of strings")

        # schema-level validation of the front matter (subset; JSON Schema
        # keyword coverage is enforced where jsonschema is unavailable)
        err = _validate_against_contract_schema(fm, fm_contract_schema, p)
        if err:
            errors.extend(err)

    # CONTRACT_INDEX.md must reference every canonical contract id
    index_ids = _index_contract_ids()
    for cid in seen_ids:
        if cid not in index_ids:
            errors.append(f"index drift: contract '{cid}' missing from CONTRACT_INDEX.md")
    for cid in index_ids:
        if cid not in seen_ids:
            errors.append(f"index drift: CONTRACT_INDEX.md lists unknown contract '{cid}'")

    # Receipt-rotation discipline: meaningful changes must rotate receipts
    errors.extend(check_receipt_rotation(lib))

    return errors


def _load_json_schema(name: str) -> dict:
    p = SCHEMA_DIR / name
    if not p.is_file():
        raise CTError(f"schema file missing: {name}")
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_against_contract_schema(fm: dict, schema: dict, where: str) -> list[str]:
    """Structural enforcement of contract.schema.json rules (no jsonschema dep)."""
    errs = []
    props = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
        if key not in fm:
            errs.append(f"{where}: schema requires '{key}'")
    for key, val in fm.items():
        if key not in props:
            if schema.get("additionalProperties") is False:
                errs.append(f"{where}: schema forbids additional property '{key}'")
            continue
        ps = props[key]
        if "enum" in ps and val not in ps["enum"]:
            errs.append(f"{where}: '{key}' value {val!r} not in enum {ps['enum']}")
        if ps.get("type") == "string":
            if not isinstance(val, str):
                errs.append(f"{where}: '{key}' must be a string")
            elif "pattern" in ps and not re.match(ps["pattern"], val):
                errs.append(f"{where}: '{key}' violates pattern {ps['pattern']}")
            elif "maxLength" in ps and isinstance(val, str) and len(val) > ps["maxLength"]:
                errs.append(f"{where}: '{key}' exceeds maxLength {ps['maxLength']}")
        if ps.get("type") == "array":
            if not isinstance(val, list):
                errs.append(f"{where}: '{key}' must be an array")
            elif "minItems" in ps and len(val) < ps["minItems"]:
                errs.append(f"{where}: '{key}' needs >= {ps['minItems']} items")
    return errs


def _index_contract_ids() -> set[str]:
    ids: set[str] = set()
    if INDEX_FILE.is_file():
        text = INDEX_FILE.read_text(encoding="utf-8")
        for m in re.finditer(r"\| `([a-z0-9-]+)`", text):
            ids.add(m.group(1))
    return ids


# ---------------------------------------------------------------- lockfile

def build_lock(lib: list[dict] | None = None) -> dict:
    if lib is None:
        lib = load_library()
    entries = []
    for c in sorted(lib, key=lambda x: x["front_matter"].get("contract_id", "")):
        fm = c["front_matter"]
        entries.append(
            {
                "id": fm["contract_id"],
                "version": str(fm["version"]),
                "path": c["rel_path"],
                "sha256": c["sha256"],
                "receipt": c["receipts"][0] if c["receipts"] else None,
                "status": fm["status"],
            }
        )
    return {
        "schema": "play-nice/lock-v1",
        "generated_from": {
            "contract_count": len(entries),
        },
        "contracts": entries,
    }


def write_lock() -> dict:
    lock = build_lock()
    LOCKFILE.write_text(json.dumps(lock, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return lock


def load_lock() -> dict:
    if not LOCKFILE.is_file():
        raise CTError("contracts.lock.json not found; run 'contractctl lock'")
    return json.loads(LOCKFILE.read_text(encoding="utf-8"))


def verify_lock(lib: list[dict] | None = None) -> list[str]:
    errors = []
    if lib is None:
        lib = load_library()
    lock = load_lock()
    current = {c["front_matter"]["contract_id"]: c for c in lib}
    locked = {e["id"]: e for e in lock.get("contracts", [])}

    for cid, e in locked.items():
        if cid not in current:
            errors.append(f"lock drift: locked contract '{cid}' no longer exists in library")
            continue
        c = current[cid]
        if e["sha256"] != c["sha256"]:
            errors.append(f"lock drift: '{cid}' content hash changed (was {e['sha256'][:12]}, now {c['sha256'][:12]})")
        if str(e["version"]) != str(c["front_matter"]["version"]):
            errors.append(f"lock drift: '{cid}' version changed ({e['version']} → {c['front_matter']['version']})")
        if e.get("receipt") != (c["receipts"][0] if c["receipts"] else None):
            errors.append(f"lock drift: '{cid}' receipt changed ({e.get('receipt')} → {c['receipts'][0] if c['receipts'] else None})")
    for cid in current:
        if cid not in locked:
            errors.append(f"lock drift: library contract '{cid}' missing from contracts.lock.json (run lock)")
    return errors


# ---------------------------------------------------------------- bundle identity
# Bundle identity represents the RESOLVED contract set (the contracts selected
# for a task), not the whole library. Two sessions resolving different task
# scopes get different bundle identities; the same scope + same library gets
# a byte-stable identity. The full library is itself representable as a set
# (all contracts) for lockfile purposes.

def _bundle_material(contract_refs: list[str]) -> str:
    """Canonical material: sorted id@version#sha256 refs."""
    return "|".join(sorted(contract_refs))


def resolved_refs(lock: dict, contract_ids: list[str] | set[str] | None = None) -> list[str]:
    """id@version#sha256 refs for the given ids (all lockfile entries if None)."""
    ids = set(contract_ids) if contract_ids is not None else None
    refs = []
    for e in lock["contracts"]:
        if ids is None or e["id"] in ids:
            refs.append(f"{e['id']}@{e['version']}#{e['sha256']}")
    return refs


def bundle_receipt(lock: dict, contract_ids: list[str] | set[str] | None = None) -> str:
    """Deterministic three-word bundle receipt for the RESOLVED set.

    Not a credential; identifies a set of contract versions/hashes.
    """
    material = _bundle_material(resolved_refs(lock, contract_ids))
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    words = _RECEIPT_WORDS
    n = len(words)
    i = int(digest[:16], 16)
    w1 = words[(i >> 0) % n]
    w2 = words[(i >> 24) % n]
    w3 = words[(i >> 48) % n]
    return f"{w1}-{w2}-{w3}"


def bundle_sha256(lock: dict, contract_ids: list[str] | set[str] | None = None) -> str:
    """SHA-256 over the exact resolved-set material (id@version#sha256)."""
    material = _bundle_material(resolved_refs(lock, contract_ids))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


_RECEIPT_WORDS = (
    "amber", "aster", "basalt", "beacon", "bramble", "cedar", "cinder", "clover",
    "compass", "dell", "dovetail", "driftwood", "echo", "ember", "fable",
    "fathom", "fern", "gable", "gatehouse", "harbor", "heather", "hollow",
    "inkstone", "jetty", "juniper", "kindle", "lantern", "latch", "ledger",
    "loam", "maple", "marble", "meadow", "nectar", "north", "opal", "orchard",
    "orbit", "prairie", "quartz", "quay", "ridge", "rill", "river", "sable",
    "sail", "stone", "thicket", "timber", "tundra", "urnfield", "vellum",
    "velvet", "window", "willow", "wren", "yarrow", "zenith",
)


# ---------------------------------------------------------------- resolution

def load_adoption(manifest_path: Path) -> dict:
    if not manifest_path.is_file():
        raise CTError(f"adoption manifest not found: {manifest_path}")
    text = manifest_path.read_text(encoding="utf-8")
    # strip front-matter delimiter style if present, else parse whole as yaml
    m = FM_RE.match(text)
    body = m.group(1) if m else re.sub(r"\A---\s*\n", "", text)
    try:
        data = _yaml_block_to_dict(body.split("\n"))
    except CTError as e:
        raise CTError(f"adoption manifest: {e}")
    if data.get("schema") != "play-nice/adoption-v1":
        raise CTError(
            f"adoption manifest: schema must be 'play-nice/adoption-v1', got {data.get('schema')!r}"
        )
    return data


def resolve_set(manifest: dict, task: str = "", task_tags: list[str] | None = None) -> dict:
    """Resolve the smallest applicable contract set.

    Selection sources (in order): manifest always; manifest triggers whose
    surface tag matches task tags found in the task description; a baseline
    floor of core truth contracts is NOT forced here — adoption manifests are
    expected to put those in 'always'. Unknown contract references fail.
    """
    lib = {c["front_matter"]["contract_id"]: c for c in load_library()}
    selected: dict[str, str] = {}  # id -> why
    errors: list[str] = []

    def add(cid: str, why: str):
        if cid in lib:
            selected[cid] = why
        else:
            errors.append(f"manifest references unknown contract '{cid}'")

    for cid in manifest.get("always", []) or []:
        add(cid, "always")

    tags = set(task_tags or [])
    if task:
        tl = task.lower()
        for surface, cids in (manifest.get("triggers", {}) or {}).items():
            surface_l = str(surface).lower()
            # surface matches if the tag was passed explicitly or appears in the task text
            if surface_l in tags or surface_l in tl or _surface_words_match(surface_l, tl):
                for cid in cids or []:
                    add(cid, f"trigger:{surface}")

    # library-level trigger matching: contracts whose own triggers appear in the task
    for cid, c in lib.items():
        trig = c["front_matter"].get("triggers") or []
        for t in trig:
            t = str(t).lower()
            if t == "always":
                continue
            if t in tags or (task and f" {t} " in f" {tl} ") or (task and t in tl):
                add(cid, f"library-trigger:{t}")
                break

    return {"selected": selected, "errors": errors, "library_size": len(lib)}


def _surface_words_match(surface: str, task_lower: str) -> bool:
    """Loose match: 'external-api' matches tasks mentioning 'external api' or 'api'."""
    words = surface.replace("-", " ")
    if words in task_lower:
        return True
    head = words.split()[0]
    return head in ("external", "agent", "human", "ui", "api", "cli", "web", "integration") and words.split()[-1] in task_lower


# ---------------------------------------------------------------- attestation

COMMITMENT_BODY = """I have loaded and verified the complete applicable contract set for this task.

I accept these contracts as operating constraints for this session and will
actively use their information when making decisions.

I will apply them to improve the interaction between every relevant side,
including humans, agents, tools, APIs, services, interfaces, automation,
data, repositories, and future maintainers.

I will prefer behavior that is:

- truthful
- accessible
- understandable
- interoperable
- respectful of finite human attention
- respectful of external systems
- inspectable
- recoverable
- reversible where practical
- explicit about uncertainty
- provider/tool neutral where appropriate
- friendly to both human and machine consumers

I will not treat these contracts as passive documentation.

I will not silently weaken, bypass, contradict, or ignore an applicable
contract for convenience.

When implementation choices create tension between participants, I will use
the applicable contracts to seek an outcome that improves the interaction
between them rather than optimizing one side at the unnecessary expense of
another.

If contracts genuinely conflict, required evidence is unavailable, or the
safe interpretation is unclear, I will preserve that state honestly and
surface the conflict rather than inventing certainty.

I understand that "play nice together" means designing the boundary between
systems as carefully as the systems themselves."""


def make_attestation(manifest_path: Path, task: str, task_impact: dict[str, str],
                     revision: str = "uncommitted", format_text: str = True,
                     task_tags: list[str] | None = None,
                     resolved_ids: set[str] | None = None) -> dict | str:
    """Attest an exact contract set.

    resolved_ids: when provided (e.g. by build_commitment for workers), attest
    EXACTLY this set — no re-resolution. This is the governing invariant:
    the contract set attested must be exactly the contract set committed.
    """
    manifest = load_adoption(manifest_path)
    if resolved_ids is not None:
        # verify every id is real and known to the lockfile; no re-resolution
        lib_all = {c["front_matter"]["contract_id"]: c for c in load_library()}
        unknown = [cid for cid in resolved_ids if cid not in lib_all]
        if unknown:
            raise CTError("attestation: unknown contract ids in resolved set: " + ", ".join(sorted(unknown)))
        res = {"selected": {cid: "inherited-or-resolved" for cid in resolved_ids}, "errors": [], "library_size": len(lib_all)}
    else:
        res = resolve_set(manifest, task, task_tags)
    if res["errors"]:
        raise CTError("resolution errors:\n  " + "\n  ".join(res["errors"]))
    lib = {c["front_matter"]["contract_id"]: c for c in load_library()}
    lock = load_lock()
    # Fail closed on lock drift: an attestation against a drifted lockfile
    # would pin stale hashes and must not be produced.
    drift = verify_lock(list(lib.values()))
    if drift:
        raise CTError("attestation blocked — lockfile drift (run contractctl lock):\n  " + "\n  ".join(drift))
    locked = {e["id"]: e for e in lock["contracts"]}
    selected_ids = set(res["selected"])
    b_receipt = bundle_receipt(lock, selected_ids)

    loaded = []
    conflicts = []
    for cid, why in sorted(res["selected"].items()):
        c = lib[cid]
        entry = locked.get(cid)
        impact = task_impact.get(cid)
        status = "ACCEPTED"
        conflict = None
        if impact is None:
            status = "CONFLICT"
            conflict = "missing task-impact acknowledgement (see contract-attestation rule 6)"
            conflicts.append(f"{cid}: {conflict}")
        loaded.append(
            {
                "contract_id": cid,
                "version": str(c["front_matter"]["version"]),
                "sha256": c["sha256"],
                "receipt": c["receipts"][0],
                "status": status,
                "conflict": conflict,
            }
        )

    gate = "PASS" if not conflicts else "BLOCKED"
    att = {
        "format": ATTESTATION_FORMAT,
        "bundle": {
            "library_version": library_version(),
            "library_revision": revision,
            "receipt": b_receipt,
            "sha256": bundle_sha256(lock, selected_ids),
            "scope": "resolved-set",
        },
        "loaded": loaded,
        "task_impact": [f"{k}: {v}" for k, v in sorted(task_impact.items())],
        "conflicts": "; ".join(conflicts) if conflicts else "none",
        "gate": gate,
    }
    if format_text:
        return format_attestation_text(att, res)
    return att


def format_attestation_text(att: dict, res: dict) -> str:
    lines = [ATTESTATION_FORMAT, ""]
    lines.append("bundle:")
    lines.append(f"  library_version: {att['bundle'].get('library_version', '?')}")
    lines.append(f"  library_revision: {att['bundle'].get('library_revision', '?')}")
    lines.append(f"  receipt: {att['bundle']['receipt']}")
    lines.append(f"  sha256: {att['bundle'].get('sha256', '?')}")
    lines.append("  scope: resolved-set")
    lines.append("")
    lines.append("loaded:")
    for e in att["loaded"]:
        lines.append(f"  {e['contract_id']}@{e['version']}")
        lines.append(f"    receipt: {e['receipt']}")
        lines.append(f"    sha256: {e['sha256']}")
        lines.append(f"    status: {e['status']}")
    lines.append("")
    lines.append("task-impact:")
    for t in att["task_impact"]:
        lines.append(f"  - {t}")
    lines.append("")
    lines.append(f"conflicts: {att['conflicts']}")
    lines.append("")
    lines.append(f"CONTRACT GATE: {att['gate']}")
    return "\n".join(lines)


def verify_attestation(att_path: Path, manifest_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    raw = att_path.read_text(encoding="utf-8")
    # Accept the text block format; parse it
    parsed = _parse_attestation_text(raw)
    if parsed is None:
        # try JSON
        try:
            att = json.loads(raw)
        except json.JSONDecodeError:
            return ["attestation: unparseable (neither text block nor JSON)"]
    else:
        att = parsed

    lib = {c["front_matter"]["contract_id"]: c for c in load_library()}
    lock = load_lock()
    locked = {e["id"]: e for e in lock["contracts"]}

    if att.get("format") != ATTESTATION_FORMAT:
        errors.append(f"attestation: format must be {ATTESTATION_FORMAT!r}")
    gate = att.get("gate")
    if gate not in ("PASS", "BLOCKED"):
        errors.append(f"attestation: gate must be PASS or BLOCKED, got {gate!r}")

    # lock drift fails closed: cannot verify against a stale lockfile
    drift = verify_lock(list(lib.values()))
    if drift:
        errors.extend(f"lock drift: {d}" for d in drift)
        return errors

    # bundle checks: the bundle is the RESOLVED set (the loaded contracts)
    b = att.get("bundle", {})
    loaded_ids = {e.get("contract_id") for e in att.get("loaded", []) if e.get("contract_id")}
    expected_receipt = bundle_receipt(lock, loaded_ids)
    if b.get("receipt") != expected_receipt:
        errors.append(
            f"attestation: bundle receipt mismatch (attested {b.get('receipt')!r}, current resolved-set receipt {expected_receipt!r}) — library changed, resolution changed, or stale attestation"
        )
    if b.get("sha256") and b.get("sha256") != bundle_sha256(lock, loaded_ids):
        errors.append("attestation: resolved-set bundle sha256 mismatch")

    loaded = att.get("loaded", [])
    if not loaded:
        errors.append("attestation: no contracts loaded")
    for e in loaded:
        cid = e.get("contract_id", "")
        if cid not in lib:
            errors.append(f"attestation: unknown contract '{cid}'")
            continue
        c = lib[cid]
        if e.get("receipt") != (c["receipts"][0] if c["receipts"] else None):
            errors.append(f"attestation: wrong receipt for '{cid}' (got {e.get('receipt')!r}, want {c['receipts'][0]!r})")
        if e.get("sha256") != c["sha256"]:
            errors.append(f"attestation: wrong hash for '{cid}'")
        if e.get("version") != str(c["front_matter"]["version"]):
            errors.append(f"attestation: wrong version for '{cid}' ({e.get('version')} vs {c['front_matter']['version']})")
        if e.get("status") not in ATTEST_STATUSES:
            errors.append(f"attestation: invalid status {e.get('status')!r} for '{cid}'")
        if e.get("status") == "CONFLICT" and not e.get("conflict"):
            errors.append(f"attestation: CONFLICT for '{cid}' without explanation")

    if not att.get("task_impact"):
        errors.append("attestation: missing task-impact acknowledgement")

    # mandatory contracts from manifest must be present
    if manifest_path is not None:
        manifest = load_adoption(manifest_path)
        loaded_ids = {e.get("contract_id") for e in loaded}
        for cid in manifest.get("always", []) or []:
            if cid not in loaded_ids:
                errors.append(f"attestation: mandatory contract '{cid}' (manifest always) not loaded")

    # gate consistency
    if gate == "PASS":
        if any(e.get("status") == "CONFLICT" for e in loaded):
            errors.append("attestation: gate PASS but a loaded contract is CONFLICT")
        if att.get("conflicts") not in (None, "none", ""):
            errors.append("attestation: gate PASS but conflicts recorded")
    return errors


def _parse_attestation_text(raw: str) -> dict | None:
    """Parse the CONTRACT_ATTESTATION v1 text block back into data."""
    if ATTESTATION_FORMAT not in raw:
        return None
    loaded = []
    cur = None
    task_impact = []
    bundle = {"library_version": None, "library_revision": None,
              "receipt": None, "sha256": None, "scope": None}
    conflicts = None
    gate = None
    in_impact = False
    for line in raw.split("\n"):
        s = line.strip()
        if s.startswith("library_version:") and cur is None:
            bundle["library_version"] = s.split(":", 1)[1].strip()
        elif s.startswith("library_revision:") and cur is None:
            bundle["library_revision"] = s.split(":", 1)[1].strip()
        elif s.startswith("receipt:") and cur is None:
            bundle["receipt"] = s.split(":", 1)[1].strip()
        elif s.startswith("sha256:") and cur is None:
            bundle["sha256"] = s.split(":", 1)[1].strip()
        elif s.startswith("scope:") and cur is None:
            bundle["scope"] = s.split(":", 1)[1].strip()
        elif re.match(r"^[a-z0-9-]+@\d+\.\d+\.\d+$", s):
            cid, ver = s.split("@")
            cur = {"contract_id": cid, "version": ver}
        elif cur is not None and s.startswith("receipt:"):
            cur["receipt"] = s.split(":", 1)[1].strip()
        elif cur is not None and s.startswith("sha256:"):
            cur["sha256"] = s.split(":", 1)[1].strip()
        elif cur is not None and s.startswith("status:"):
            cur["status"] = s.split(":", 1)[1].strip()
            loaded.append(cur)
            cur = None
        elif s.startswith("task-impact:"):
            in_impact = True
        elif s.startswith("conflicts:"):
            in_impact = False
            conflicts = s.split(":", 1)[1].strip()
        elif s.startswith("- ") and in_impact:
            task_impact.append(s[2:].strip())
        elif s.startswith("CONTRACT GATE:"):
            gate = s.split(":", 1)[1].strip()
    if gate is None:
        return None
    return {
        "format": ATTESTATION_FORMAT,
        "bundle": bundle,
        "loaded": loaded,
        "task_impact": task_impact,
        "conflicts": conflicts,
        "gate": gate,
    }


# ---------------------------------------------------------------- commitment

COMMITMENT_FORMAT = "CONTRACT OPERATIONAL COMMITMENT v1"
COMMITMENT_ACTIVE = "ACTIVE"
COMMITMENT_INACTIVE = "INACTIVE"


def _consumer_context_key(manifest_path: Path | None = None) -> str:
    """Identity of the consuming execution context.

    Resolution order:
    1. $CONTRACTCTL_SESSION_DIR — caller pins the artifact directory explicitly
       (any orchestration harness should set this per worktree/session).
    2. <manifest's consuming project root>/.contracts/sessions/ — the
       directory containing the adoption manifest (or its .contracts/ parent)
       anchors the artifacts to THAT project, so two consuming projects or two
       worktrees of the same project never collide.
    3. <library>/.contract-commitments/ — last-resort fallback when running
       inside the library itself with no manifest context.
    """
    env = os.environ.get("CONTRACTCTL_SESSION_DIR")
    if env:
        return env
    if manifest_path is not None:
        m = Path(manifest_path).resolve()
        if m.parent.name == ".contracts":
            root = m.parent          # <project>/.contracts/
            return str(root / "sessions")
        return str(m.parent / ".contracts" / "sessions")
    return str(REPO_ROOT / ".contract-commitments")


def default_artifact_path(role: str = "session", task: str = "",
                          manifest_path: Path | None = None) -> Path:
    """Project/worktree/session-safe artifact path.

    Artifacts live in the CONSUMING execution context (the project that owns
    the adoption manifest), never a global path in the contract library.
    Keyed by role+task so parallel sessions/workers coexist; callers may pin
    the directory with CONTRACTCTL_SESSION_DIR or --output.
    """
    d = Path(_consumer_context_key(manifest_path))
    d.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9-]+", "-", task.lower()).strip("-")[:48] or "untitled"
    return d / f"{role}-{slug}.json"


def build_commitment(manifest_path: Path, task: str, task_impact: dict[str, str],
                     revision: str = "uncommitted",
                     role: str = "session", parent_bundle: str | None = None,
                     parent_manifest: Path | None = None,
                     worker: bool = False,
                     task_tags: list[str] | None = None) -> tuple[dict, str]:
    """Build the operational commitment for a task.

    Returns (artifact_dict, text_block). Raises CTError on any failure that
    must prevent the ACTIVE state: resolution errors, missing task-impact,
    conflicts, lock drift, or (for workers) an unverifiable parent bundle.
    """
    manifest = load_adoption(manifest_path)
    res = resolve_set(manifest, task, task_tags)
    if res["errors"]:
        raise CTError("commitment: resolution errors:\n  " + "\n  ".join(res["errors"]))

    lib = {c["front_matter"]["contract_id"]: c for c in load_library()}
    lock = load_lock()
    selected_ids = set(res["selected"])

    if worker:
        # Real inheritance: the parent bundle must be a resolvable bundle in
        # this library. The worker's resolved set is the UNION of the parent's
        # applicable contracts and the worker's own task-triggered contracts —
        # workers load inherited contracts, add task-specific ones, and therefore
        # cannot silently drop a parent constraint.
        if not parent_bundle:
            raise CTError("commitment: worker commitment requires --parent-bundle (inherited bundle sha256)")
        parent = find_commitment_by_bundle(parent_bundle, manifest_path)
        if parent is None:
            raise CTError(
                "commitment: parent bundle not found — an orchestrator commitment "
                "with this bundle_sha256 must exist under .contract-commitments/ "
                "(workers inherit a real parent bundle, not an arbitrary hash)"
            )
        parent_contracts = set(parent.get("contracts", []))
        inherited_only = parent_contracts - selected_ids
        if inherited_only:
            # inherited contracts join the worker's resolved set; the worker must
            # acknowledge their impact too (attesting them, not merely inheriting)
            missing_impact = [c for c in inherited_only if c not in task_impact]
            if missing_impact:
                raise CTError(
                    "commitment: worker inherited contracts need task-impact "
                    f"acknowledgement too ({', '.join(sorted(missing_impact))}) — "
                    "a worker loads and attests the parent's applicable set, "
                    "never silently drops it"
                )
            selected_ids |= inherited_only
            res["selected"] = {cid: "inherited" if cid in inherited_only else why
                               for cid, why in res["selected"].items()}
            for cid in inherited_only:
                res["selected"][cid] = "inherited"
        role = "worker"

    # every selected contract needs an impact acknowledgement (incl. inherited)
    missing_all = [cid for cid in selected_ids if cid not in task_impact]
    if missing_all:
        raise CTError(
            "commitment: missing task-impact acknowledgement for "
            f"{', '.join(sorted(missing_all))}"
        )

    # A PASS attestation over the EXACT (possibly unioned) set is a precondition;
    # its machinery also fails closed on lock drift. Governing invariant:
    # the set attested must be exactly the set committed.
    att = make_attestation(manifest_path, task, task_impact, revision, format_text=False,
                           resolved_ids=selected_ids)
    if att["gate"] != "PASS":
        raise CTError(
            "commitment: contract gate is BLOCKED — conflicts prevent the ACTIVE state:\n  "
            + str(att["conflicts"])
        )
    # defensive: the attested set must equal the committed set
    attested_ids = {e["contract_id"] for e in att["loaded"]}
    if attested_ids != selected_ids:
        raise CTError(
            "commitment: attestation/commitment set mismatch "
            f"(attested-only: {sorted(attested_ids - selected_ids)}, "
            f"committed-only: {sorted(selected_ids - attested_ids)})"
        )

    artifact = {
        "format": COMMITMENT_FORMAT,
        "role": role,                      # session | orchestrator | worker
        "contract_gate": "PASS",
        "commitment": COMMITMENT_ACTIVE,
        "library_version": library_version(),
        "library_revision": revision,
        "bundle_receipt": bundle_receipt(lock, selected_ids),
        "bundle_sha256": bundle_sha256(lock, selected_ids),
        "bundle_scope": "resolved-set",
        "task": task,
        "task_fingerprint": task,
        "session_dir": str(default_artifact_path(role, task, manifest_path=manifest_path).parent),
        "resolved_contracts": sorted(f"{cid}@{lib[cid]['front_matter']['version']}" for cid in selected_ids),
        "contracts": sorted(selected_ids),
        "inherited_bundle": parent_bundle,
        "activated_at": None,  # filled by caller with real timestamps if desired
    }

    text = format_commitment_text(artifact)
    return artifact, text


def _artifact_search_dirs(manifest_path: Path | None = None) -> list[Path]:
    """Directories to search for commitment artifacts, consumer-context first."""
    dirs: list[Path] = []
    seen: set[str] = set()
    primary = Path(_consumer_context_key(manifest_path))
    dirs.append(primary)
    # fallbacks: explicit env dirs may differ; library-local dir for
    # in-library sessions; never duplicate
    for d in (primary, Path(os.environ.get("CONTRACTCTL_SESSION_DIR", "")) if os.environ.get("CONTRACTCTL_SESSION_DIR") else None,
              REPO_ROOT / ".contract-commitments"):
        if d is None:
            continue
        key = str(d.resolve()) if d.exists() or d.parent.exists() else str(d)
        if key not in seen:
            seen.add(key)
            if d not in dirs:
                dirs.append(d)
    return [d for d in dirs if d.is_dir()]


def find_commitment_by_bundle(bundle_sha: str, manifest_path: Path | None = None) -> dict | None:
    """Find a recorded commitment (orchestrator or session) by its bundle sha256.

    Inheritance validates against recorded parent state in the SAME consuming
    context (plus the library-local fallback), so a worker cannot claim an
    invented parent.
    """
    for d in _artifact_search_dirs(manifest_path):
        for f in sorted(d.glob("*.json")):
            try:
                a = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if a.get("bundle_sha256") == bundle_sha and a.get("commitment") == COMMITMENT_ACTIVE:
                if a.get("role") in ("orchestrator", "session"):
                    return a
    return None


def format_commitment_text(a: dict) -> str:
    lines = [COMMITMENT_FORMAT, ""]
    lines.append(COMMITMENT_BODY)
    lines.append("")
    lines.append(f"bundle: {a['bundle_receipt']}")
    lines.append(f"bundle_sha256: {a['bundle_sha256']}")
    lines.append(f"bundle_scope: {a.get('bundle_scope', 'resolved-set')}")
    if a.get("inherited_bundle"):
        lines.append(f"INHERITED CONTRACT BUNDLE: {a['inherited_bundle']}")
        lines.append("PARENT CONTRACT COMMITMENT: ACTIVE")
    lines.append(f"role: {a['role']}")
    lines.append(f"task: {a['task']}")
    lines.append("")
    lines.append(f"CONTRACT COMMITMENT: {a['commitment']}")
    return "\n".join(lines)


def write_session_artifact(artifact: dict, path: Path | None = None,
                           manifest_path: Path | None = None) -> Path:
    """Persist the commitment into the consuming context (no secrets, by construction)."""
    p = path or default_artifact_path(artifact.get("role", "session"), artifact.get("task", ""),
                                      manifest_path=manifest_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return p


def load_session_artifact(path: Path | None = None, role: str = "session", task: str = "",
                          manifest_path: Path | None = None) -> dict | None:
    """Load the artifact for this role+task key, or the newest artifact when
    only a path/role is given. Searches the consuming context. Returns None
    when absent."""
    if path is not None:
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    slug = re.sub(r"[^a-z0-9-]+", "-", task.lower()).strip("-")[:48] or "untitled"
    for d in _artifact_search_dirs(manifest_path):
        candidates = sorted(d.glob(f"{role}-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if task:
            exact = d / f"{role}-{slug}.json"
            if exact.is_file():
                candidates = [exact] + [c for c in candidates if c != exact]
        for c in candidates:
            try:
                return json.loads(c.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
    return None


def session_status(manifest_path: Path | None = None, artifact_path: Path | None = None,
                   role: str = "session", task: str = "") -> tuple[str, list[str]]:
    """Report the current commitment state and any staleness.

    Returns (status_line, problems). Staleness rules:
    - library changed → resolved-set bundle receipt/sha no longer match → STALE
    - artifact task triggers additional contracts vs what was resolved → RE-RESOLVE
    - worker artifacts: parent bundle must still be a real recorded commitment
    """
    problems: list[str] = []
    artifact = load_session_artifact(artifact_path, role=role, task=task, manifest_path=manifest_path)
    if artifact is None:
        return "CONTRACT COMMITMENT: INACTIVE (no session artifact)", ["no commitment recorded for this session"]

    lock = load_lock()
    recorded = set(artifact.get("contracts", []))
    cur_receipt = bundle_receipt(lock, recorded)
    cur_sha = bundle_sha256(lock, recorded)

    if artifact.get("commitment") != COMMITMENT_ACTIVE:
        problems.append("recorded commitment is not ACTIVE")
    if artifact.get("bundle_receipt") != cur_receipt or artifact.get("bundle_sha256") != cur_sha:
        problems.append(
            f"stale bundle — commitment was made against {artifact.get('bundle_receipt')}/{str(artifact.get('bundle_sha256'))[:12]}, "
            f"library now yields {cur_receipt}/{cur_sha[:12]} for this resolved set — re-attest and re-commit"
        )

    if manifest_path is not None and artifact.get("task_fingerprint"):
        manifest = load_adoption(manifest_path)
        res = resolve_set(manifest, artifact["task_fingerprint"])
        now = set(res["selected"])
        missing = now - recorded
        if missing:
            problems.append(
                "task now triggers additional contracts not in the commitment "
                f"({', '.join(sorted(missing))}) — re-resolution required"
            )

    if artifact.get("role") == "worker" and artifact.get("inherited_bundle"):
        parent = find_commitment_by_bundle(artifact["inherited_bundle"], manifest_path)
        if parent is None:
            problems.append(
                "parent commitment no longer recorded — inherited bundle "
                f"{artifact['inherited_bundle'][:12]} cannot be verified — re-commit under a live parent"
            )

    state = "ACTIVE" if not problems else "STALE" if any("stale" in p for p in problems) else "INACTIVE"
    if problems and "not ACTIVE" in problems[0]:
        state = "INACTIVE"
    summary = (
        f"CONTRACT COMMITMENT: {state}\n"
        f"  bundle: {artifact.get('bundle_receipt')} ({str(artifact.get('bundle_sha256'))[:12]}...)\n"
        f"  task: {artifact.get('task')}\n"
        f"  contracts: {len(recorded)} resolved\n"
        f"  role: {artifact.get('role', 'session')}"
    )
    for p in problems:
        summary += f"\n  - {p}"
    return summary, problems


def verify_commitment_artifact(artifact: dict, manifest_path: Path | None = None) -> list[str]:
    """Verify a commitment artifact against the current library. Fail closed."""
    errors: list[str] = []
    if artifact.get("format") != COMMITMENT_FORMAT:
        errors.append(f"commitment: format must be {COMMITMENT_FORMAT!r}")
    if artifact.get("contract_gate") != "PASS":
        errors.append("commitment: requires a PASS contract gate")
    if artifact.get("commitment") != COMMITMENT_ACTIVE:
        errors.append("commitment: state is not ACTIVE")
    lock = load_lock()
    recorded = set(artifact.get("contracts", []))
    if artifact.get("bundle_receipt") != bundle_receipt(lock, recorded):
        errors.append("commitment: resolved-set bundle receipt does not match current library (stale)")
    if artifact.get("bundle_sha256") != bundle_sha256(lock, recorded):
        errors.append("commitment: resolved-set bundle sha256 does not match current library (stale)")
    if not artifact.get("contracts"):
        errors.append("commitment: no resolved contracts recorded")
    if not artifact.get("task"):
        errors.append("commitment: task not recorded")
    if artifact.get("role") == "worker":
        if not artifact.get("inherited_bundle"):
            errors.append("commitment: worker commitment missing inherited bundle")
        else:
            parent = find_commitment_by_bundle(artifact["inherited_bundle"], manifest_path)
            if parent is None:
                errors.append("commitment: worker's inherited bundle has no recorded parent commitment")
            else:
                dropped = set(parent.get("contracts", [])) - recorded
                if dropped:
                    errors.append(
                        f"commitment: worker dropped parent's applicable constraints ({', '.join(sorted(dropped))})"
                    )
    # every recorded contract must exist and hash-match
    locked = {e["id"]: e for e in lock["contracts"]}
    lib = {c["front_matter"]["contract_id"]: c for c in load_library()}
    for ref in artifact.get("contracts", []):
        if ref not in locked:
            errors.append(f"commitment: unknown contract '{ref}'")
        elif ref in lib and locked[ref]["sha256"] != lib[ref]["sha256"]:
            errors.append(f"commitment: contract '{ref}' content changed since commitment")
    return errors


def check_receipt_rotation(lib: list[dict]) -> list[str]:
    """Mechanical enforcement: meaningful contract changes rotate receipts.

    For each canonical contract with a committed previous version in Git
    history: if content changed AND the semantic version changed beyond a
    pure PATCH clarification, the receipt MUST also have changed. This makes
    'meaningful change -> version change -> receipt change' checkable rather
    than memory-driven. Skipped (reported, not failed) when Git history is
    unavailable (e.g. a fresh export).
    """
    import subprocess

    def git(*args: str) -> str | None:
        try:
            r = subprocess.run(
                ["git", "-C", str(REPO_ROOT), *args],
                capture_output=True, text=True, timeout=10,
            )
            return r.stdout if r.returncode == 0 else None
        except Exception:
            return None

    if git("rev-parse", "--git-dir") is None:
        return []  # no history available; cannot enforce (documented limitation)

    errors: list[str] = []
    for c in lib:
        fm = c["front_matter"]
        if fm.get("status") != "canonical":
            continue
        rel = c["rel_path"]
        prev = git("show", f"HEAD:{rel}")
        if prev is None or prev == c["text"]:
            continue  # unchanged or brand-new file
        prev_fm = None
        try:
            prev_fm = parse_front_matter(prev)
        except CTError:
            continue
        prev_version = str(prev_fm.get("version", ""))
        cur_version = str(fm.get("version", ""))
        if prev_version == cur_version:
            # content changed with NO version bump: that's a lock-drift class
            # error already caught elsewhere; here, unchanged receipt is expected
            continue
        # version changed: is it beyond a pure PATCH?
        try:
            pm, pd, pp = (int(x) for x in prev_version.split("."))
            cm, cd, cp = (int(x) for x in cur_version.split("."))
        except ValueError:
            continue
        patch_only = (pm == cm and pd == cd and cp == pp + 1) and cur_version != prev_version
        prev_receipts = RECEIPT_RE.findall(prev)
        cur_receipts = c["receipts"]
        if patch_only:
            # PATCH = clarification only: content may change without receipt
            # rotation, but any receipt change must stay unique (checked elsewhere)
            continue
        # MINOR/MAJOR = meaningful change: receipt MUST rotate
        if prev_receipts and cur_receipts and prev_receipts[0] == cur_receipts[0]:
            errors.append(
                f"{rel}: version changed {prev_version} -> {cur_version} "
                f"(meaningful) but receipt did not rotate (still {cur_receipts[0]})"
            )
    return errors


# ---------------------------------------------------------------- question/help artifacts

def validate_question(path: Path) -> list[str]:
    """Validate a play-nice/question|help-request|help-response artifact
    against schema/question.schema.json (structural subset enforcement)."""
    if not path.is_file():
        return [f"question: file not found: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"question: invalid JSON — {e}"]
    schema = json.loads(QUESTION_SCHEMA.read_text(encoding="utf-8"))
    errs: list[str] = []

    allowed_schemas = schema["properties"]["schema"]["enum"]
    if data.get("schema") not in allowed_schemas:
        errs.append(f"question: schema must be one of {allowed_schemas}, got {data.get('schema')!r}")
    for key in schema.get("required", []):
        if key not in data:
            errs.append(f"question: missing required field '{key}'")

    statuses = schema["properties"]["status"]["enum"]
    # documented migration aliases: legacy lowercase forms parse but are
    # normalized (never emitted canonically)
    ALIASES = {"waiting_for_answer": "WAITING", "answered": "ANSWERED"}
    raw_status = data.get("status")
    status = ALIASES.get(raw_status, raw_status)
    if status not in statuses:
        errs.append(f"question: invalid status {raw_status!r} (valid: {statuses})")

    for pkey in ("requester", "target"):
        p = data.get(pkey)
        if p is None:
            continue
        if not isinstance(p, dict) or p.get("type") not in schema["$defs"]["participant"]["properties"]["type"]["enum"]:
            errs.append(f"question: {pkey}.type must be one of {schema['$defs']['participant']['properties']['type']['enum']}")

    if data.get("schema") == "play-nice/help-request-v1" and not data.get("needed_capability"):
        errs.append("question: help-request-v1 requires 'needed_capability'")
    if data.get("schema") == "play-nice/help-response-v1":
        if not data.get("result"):
            errs.append("question: help-response-v1 requires 'result'")
        if status not in ("ANSWERED", "DECLINED", "EXPIRED"):
            errs.append("question: help-response status must be ANSWERED, DECLINED, or EXPIRED")

    if data.get("blocking") is False and data.get("safe_to_continue_without_answer") is False:
        errs.append("question: inconsistent — not blocking but not safe to continue")

    # secret-shape hygiene: help artifacts must not carry credential-like values
    blob = json.dumps(data).lower()
    for shape in ("api_key\":", "token\":", "password\":", "secret\":"):
        if shape in blob:
            errs.append(f"question: possible inline secret near '{shape}' — help artifacts reference secrets symbolically, never inline")

    # choices shape
    choices = data.get("choices")
    if choices is not None:
        if not isinstance(choices, list) or len(choices) < 2:
            errs.append("question: choices must be a list of at least 2 when present")
        else:
            for ch in choices:
                if not isinstance(ch, dict) or not ch.get("id") or not ch.get("label"):
                    errs.append("question: each choice needs 'id' and 'label'")
    rec = data.get("recommended")
    if rec is not None and choices is not None:
        if not any(c.get("id") == rec for c in choices):
            errs.append(f"question: recommended {rec!r} is not one of the choice ids")
    return errs


# ---------------------------------------------------------------- adoption

def validate_adoption_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_adoption(manifest_path)
    except CTError as e:
        return [str(e)]
    lib = {c["front_matter"]["contract_id"] for c in load_library()}
    schema = _load_json_schema("adoption.schema.json")
    # structural checks
    src = manifest.get("source")
    if not isinstance(src, dict) or not src.get("repository") or not src.get("revision"):
        errors.append("adoption: source.repository and source.revision are required")
    for cid in manifest.get("always", []) or []:
        if cid not in lib:
            errors.append(f"adoption: unknown contract in always: '{cid}'")
    for surface, cids in (manifest.get("triggers", {}) or {}).items():
        if not isinstance(cids, list):
            errors.append(f"adoption: triggers.{surface} must be a list")
            continue
        for cid in cids:
            if cid not in lib:
                errors.append(f"adoption: unknown contract in triggers.{surface}: '{cid}'")
    props = schema.get("properties", {})
    for key in manifest:
        if key not in props and schema.get("additionalProperties") is False:
            errors.append(f"adoption: schema forbids additional property '{key}'")
    return errors


def check_stale_pin(manifest_path: Path) -> list[str]:
    """Stale pin detection: the adoption revision must match this library's
    current git revision. The sentinel '0000000' marks an example/unadopted
    manifest and is reported as a reminder, not an error."""
    errors: list[str] = []
    try:
        manifest = load_adoption(manifest_path)
    except CTError as e:
        return [str(e)]
    current = library_revision()
    pinned = (manifest.get("source", {}) or {}).get("revision", "")
    if pinned == "0000000":
        # example placeholder: valid shape, but cannot be used for real adoption
        errors.append(
            "adoption: placeholder revision 0000000 — pin the adopted commit SHA "
            "before using this manifest in a project"
        )
        return errors
    if pinned and current and pinned != current:
        errors.append(
            f"adoption: stale pin — manifest pins revision {pinned}, library is at {current}"
        )
    return errors


def library_version() -> str:
    """Library semver (VERSION file). Independent from the adopted Git revision:
    version describes contract content; revision pins the exact adopted commit."""
    if VERSION_FILE.is_file():
        v = VERSION_FILE.read_text(encoding="utf-8").strip()
        if v:
            return v
    return "unknown"


def library_revision() -> str:
    """Adopted Git revision of the library (commit SHA when available, else VERSION)."""
    import subprocess
    try:
        sha = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if SHA256_RE.match(sha) or (len(sha) >= 7 and all(c in "0123456789abcdef" for c in sha)):
            return sha
    except Exception:
        pass
    return library_version()


# ---------------------------------------------------------------- project context / participant packs

CANONICALITY_STATES = {"canonical", "reference", "observed", "generated",
                       "historical", "superseded", "stale", "unknown"}
PARTICIPANT_TYPES = {"design-service", "forge", "agent", "automation", "test-tool",
                     "deployment-system", "database", "external-api", "monitoring",
                     "identity", "human-team", "other"}
SECRET_SHAPE_RE = re.compile(
    r"(api[_-]?key|token|password|secret|cookie|credential)\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{16,}",
    re.IGNORECASE,
)


def _load_yaml_file(path: Path) -> dict:
    if not path.is_file():
        raise CTError(f"file not found: {path}")
    try:
        return _yaml_block_to_dict(path.read_text(encoding="utf-8").split("\n"))
    except CTError as e:
        raise CTError(f"{path}: {e}")


def _check_no_secrets(root: Path, errs: list[str]) -> None:
    """Scan every file under a participant pack / project dir for secret shapes."""
    for f in sorted(root.rglob("*")):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, ValueError):
            continue
        for m in SECRET_SHAPE_RE.finditer(text):
            # allow symbolic references (values like 'vault: figma/oauth' won't
            # match the long-literal pattern; bare key: <long-literal> does)
            errs.append(
                f"{f}: possible inline secret near '{m.group(0)[:30]}...' — packs "
                "reference secrets symbolically (secret_reference:), never inline"
            )
            break  # one report per file is enough to act on


def validate_project(project_dir: Path) -> list[str]:
    """Validate a .project/ directory: manifest, adoption pointer, participants."""
    errs: list[str] = []
    d = Path(project_dir)
    if not d.is_dir():
        return [f"project: directory not found: {d}"]
    manifest = d / "project.yaml"
    if not manifest.is_file():
        errs.append("project: missing project.yaml (run: contractctl init-project)")
        return errs
    try:
        pm = _load_yaml_file(manifest)
    except CTError as e:
        return [str(e)]

    if pm.get("schema") != "play-nice/project-v1":
        errs.append(f"project: schema must be 'play-nice/project-v1', got {pm.get('schema')!r}")
    for key in ("id", "name"):
        if not pm.get(key):
            errs.append(f"project: missing required field '{key}'")
    own = pm.get("ownership")
    if not isinstance(own, dict) or not own.get("type"):
        errs.append("project: ownership.type is required")
    ctr = pm.get("contracts")
    if not isinstance(ctr, dict) or not ctr.get("manifest"):
        errs.append("project: contracts.manifest pointer is required")
    else:
        candidate = Path(d.parent / str(ctr["manifest"]))
        if not candidate.is_file() and (d / ctr["manifest"]).is_file():
            candidate = d / ctr["manifest"]
        if not candidate.is_file():
            errs.append(f"project: adoption manifest not found at {ctr['manifest']}")
    # README explains the model (required once, per framework rule 28)
    if not (d / "README.md").is_file():
        errs.append("project: missing README.md (durable-context explanation)")
    # secret hygiene
    _check_no_secrets(d, errs)
    # participants
    pdir = pm.get("participants", {})
    pdir_path = d / (pdir.get("directory", "participants") if isinstance(pdir, dict) else "participants")
    if pdir_path.is_dir():
        errs.extend(validate_participants(pdir_path))
    return [e for e in errs if e]


def validate_participants(participants_dir: Path) -> list[str]:
    """Validate every participant pack under a participants/ directory.
    Enforces ID uniqueness per project."""
    errs: list[str] = []
    d = Path(participants_dir)
    if not d.is_dir():
        return [f"participants: directory not found: {d}"]
    seen_ids: dict[str, str] = {}
    packs = sorted(p for p in d.iterdir() if p.is_dir())
    if not packs:
        return []  # no participants is valid
    for pack in packs:
        errs.extend(validate_participant(pack, seen_ids))
    return errs


def validate_participant(pack_dir: Path, seen_ids: dict[str] | None = None) -> list[str]:
    """Validate one participant pack directory (play-nice/participant-v1)."""
    errs: list[str] = []
    d = Path(pack_dir)
    if seen_ids is None:
        seen_ids = {}
    if not d.is_dir():
        return [f"participant: not a directory: {d}"]

    pman = d / "participant.yaml"
    if not pman.is_file():
        return [f"{d.name}: missing participant.yaml"]
    try:
        pm = _load_yaml_file(pman)
    except CTError as e:
        return [str(e)]

    pid = str(pm.get("id", ""))
    if pm.get("schema") != "play-nice/participant-v1":
        errs.append(f"{d.name}: schema must be 'play-nice/participant-v1', got {pm.get('schema')!r}")
    if not pid:
        errs.append(f"{d.name}: missing required field 'id'")
    if pid and pid != d.name:
        errs.append(f"{d.name}: directory name must match participant id '{pid}'")
    if pid and seen_ids is not None:
        if pid in seen_ids:
            errs.append(f"{d.name}: duplicate participant id '{pid}' (also {seen_ids[pid]})")
        else:
            seen_ids[pid] = d.name
    if not pm.get("name"):
        errs.append(f"{d.name}: missing required field 'name'")
    if pm.get("type") not in PARTICIPANT_TYPES:
        errs.append(f"{d.name}: invalid type {pm.get('type')!r} (valid: {sorted(PARTICIPANT_TYPES)})")

    rel = pm.get("relationship")
    if not isinstance(rel, dict):
        errs.append(f"{d.name}: relationship block is required")
    else:
        if not rel.get("role"):
            errs.append(f"{d.name}: relationship.role is required")
        if rel.get("optional") is not True:
            errs.append(f"{d.name}: relationship.optional must be true — required participants are an explicit, project-level justified exception, not a pack-level default")
        af = rel.get("authoritative_for")
        naf = rel.get("not_authoritative_for")
        if not isinstance(af, list) or not af:
            errs.append(f"{d.name}: relationship.authoritative_for list is required (may be narrow)")
        if not isinstance(naf, list) or not naf:
            errs.append(f"{d.name}: relationship.not_authoritative_for is required and non-empty — no participant owns everything")

    auth = pm.get("authentication")
    if isinstance(auth, dict):
        if "secret_reference" not in auth or "token" in str(auth).lower() and "vault" not in str(auth):
            errs.append(f"{d.name}: authentication must use symbolic secret_reference, never values")
    prov = pm.get("provenance")
    if not isinstance(prov, dict) or not prov.get("supplied_by") or not prov.get("observed_at"):
        errs.append(f"{d.name}: provenance (supplied_by, observed_at) is required")

    # capabilities (referenced or inline-required)
    caps_file = d / "capabilities.yaml"
    if caps_file.is_file():
        try:
            caps = _load_yaml_file(caps_file)
        except CTError as e:
            errs.append(str(e))
            caps = None
        if caps is not None:
            if caps.get("schema") != "play-nice/participant-capabilities-v1":
                errs.append(f"{d.name}: capabilities.schema must be 'play-nice/participant-capabilities-v1'")
            if caps.get("participant") != (pid or None):
                errs.append(f"{d.name}: capabilities.participant must match id '{pid}'")
            clist = caps.get("capabilities")
            if not isinstance(clist, list) or not clist:
                errs.append(f"{d.name}: capabilities list is required and non-empty (use real discovered capabilities)")
            else:
                for c in clist:
                    if not isinstance(c, dict) or not c.get("id") or not c.get("description"):
                        errs.append(f"{d.name}: each capability needs 'id' and 'description'")
            lims = caps.get("limitations")
            if not isinstance(lims, list) or not lims:
                errs.append(f"{d.name}: at least one honest limitation is required")

    # references
    refs_file = d / "references.yaml"
    if refs_file.is_file():
        try:
            refs = _load_yaml_file(refs_file)
        except CTError as e:
            errs.append(str(e))
            refs = None
        if refs is not None:
            if refs.get("schema") != "play-nice/references-v1":
                errs.append(f"{d.name}: references.schema must be 'play-nice/references-v1'")
            if refs.get("participant") != (pid or None):
                errs.append(f"{d.name}: references.participant must match id '{pid}'")
            rlist = refs.get("references")
            if not isinstance(rlist, list) or not rlist:
                errs.append(f"{d.name}: references list is required and non-empty")
            else:
                for r in rlist:
                    if not isinstance(r, dict) or not r.get("id") or not r.get("type"):
                        errs.append(f"{d.name}: each reference needs 'id' and 'type'")
                        continue
                    if r.get("status") not in CANONICALITY_STATES:
                        errs.append(f"{d.name}: reference '{r.get('id')}' status {r.get('status')!r} not in canonicality vocabulary {sorted(CANONICALITY_STATES)}")

    # secret hygiene across the whole pack
    _check_no_secrets(d, errs)
    return errs


PROJECT_INIT_FILES = {
    "project.yaml": """schema: play-nice/project-v1

id: {id}
name: {name}

purpose:
  summary: >
    (One or two sentences: what is this project for?)

ownership:
  type: human
  role: owner

contracts:
  manifest: {adoption_path}

participants:
  directory: participants

status:
  vocabulary: play-nice/status-v1
""",
    "README.md": """# Project Context

This directory contains durable context that helps humans, bots, tools, and
external services work with this project without rediscovering the same
information each session.

- **Contracts** define how participants behave together.
- **Project context** defines what this project is.
- **Participant packs** describe how optional collaborators interact with it.

Participant data may enrich project truth but does not silently replace it.
See the `project-context-and-participant-packs` contract in the Play-Nice
library for the full model. No secrets here — ever.
""",
    "CURRENT.md": """# Current State

(Where things stand right now: what works, what is in flight, what is next.)
""",
    "contracts/adoption.yaml": """# Play-Nice adoption manifest. Pin the revision to the commit you adopt.
schema: play-nice/adoption-v1
project: {id}
source:
  repository: Rylee-Bee/play-nice-contracts
  revision: PIN-TO-ADOPTED-SHA

always:
  - truth-and-evidence
  - explicit-state
  - ask-for-help

triggers: {{}}

notes: >-
  Start minimal; add trigger surfaces as the project grows.
""",
    "participants/README.md": """# Participants

Each subdirectory is a participant pack: a shared boundary document describing
how this project and one collaborator (service, agent, team, tool) work
together. See the `project-context-and-participant-packs` contract.

Create a pack with: participant.yaml, capabilities.yaml, interaction.md,
references.yaml — only the sections that earn their place.
""",
}


def init_project(target: Path, project_id: str, name: str, adoption_path: str = ".project/contracts/adoption.yaml") -> list[str]:
    """Create a minimal useful .project/ skeleton. No forest of empty dirs."""
    created: list[str] = []
    d = Path(target) / ".project"
    d.mkdir(parents=True, exist_ok=True)
    (d / "contracts").mkdir(exist_ok=True)
    (d / "participants").mkdir(exist_ok=True)
    for rel, template in PROJECT_INIT_FILES.items():
        p = d / rel
        if p.is_file():
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(template.format(id=project_id, name=name, adoption_path=adoption_path), encoding="utf-8")
        created.append(str(p))
    return created


# ---------------------------------------------------------------- commands

def cmd_list(_args) -> int:
    lib = load_library()
    errors = validate_library(lib)
    if errors:
        print("LIBRARY INVALID — fix before use:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    for c in sorted(lib, key=lambda x: x["front_matter"]["contract_id"]):
        fm = c["front_matter"]
        print(f"{fm['contract_id']:42s} {str(fm['version']):8s} {fm['status']:10s} {fm.get('layer', '?'):16s} {c['rel_path']}")
    print(f"\n{len(lib)} contracts")
    return 0


def cmd_show(args) -> int:
    lib = load_library()
    for c in lib:
        if c["front_matter"].get("contract_id") == args.contract_id:
            print(c["text"], end="")
            return 0
    print(f"unknown contract: {args.contract_id}", file=sys.stderr)
    return 1


def cmd_validate(_args) -> int:
    lib = load_library()
    errors = validate_library(lib)
    lock_errors = verify_lock(lib) if LOCKFILE.is_file() else ["contracts.lock.json missing (run lock)"]
    errors = errors + lock_errors
    if errors:
        print(f"INVALID — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"VALID — {len(lib)} contracts; lockfile verified; receipts unique; index in sync")
    return 0


def cmd_lock(_args) -> int:
    lib = load_library()
    errors = validate_library(lib)
    if errors:
        print("cannot lock an invalid library:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    lock = write_lock()
    print(f"wrote contracts.lock.json ({len(lock['contracts'])} contracts); bundle receipt: {bundle_receipt(lock)}")
    return 0


def cmd_resolve(args) -> int:
    manifest = Path(args.manifest) if args.manifest else Path(".contracts/adoption.yaml")
    m = load_adoption(manifest)
    res = resolve_set(m, args.task, (args.tag or []))
    if res["errors"]:
        print("resolution errors:", file=sys.stderr)
        for e in res["errors"]:
            print(f"  - {e}", file=sys.stderr)
        return 1
    groups: dict[str, list[str]] = {}
    for cid, why in res["selected"].items():
        groups.setdefault(why, []).append(cid)
    for why in sorted(groups):
        print(f"{why.upper()}")
        for cid in sorted(groups[why]):
            print(f"  {cid}")
        print()
    print(f"resolved {len(res['selected'])} of {res['library_size']} contracts for task: {args.task!r}")
    return 0


def cmd_attest(args) -> int:
    manifest = Path(args.manifest)
    impact = _read_impact_args(args)
    revision = args.revision or library_revision()
    out = make_attestation(manifest, args.task, impact, revision, task_tags=(getattr(args, "tag", None) or []))
    print(out)
    if "CONTRACT GATE: PASS" in str(out):
        print()
        print("Next: activate the operational commitment before mutating work:")
        print("  contractctl commit --manifest <m> --task <task> --impact id=sentence ...")
    return 0 if "CONTRACT GATE: PASS" in str(out) else 2


def _read_impact_args(args) -> dict[str, str]:
    impact: dict[str, str] = {}
    for item in getattr(args, "impact", None) or []:
        if "=" not in item:
            raise CTError(f"--impact expects contract_id=sentence, got {item!r}")
        k, v = item.split("=", 1)
        impact[k.strip()] = v.strip()
    impact_file = getattr(args, "impact_file", None)
    if impact_file:
        for line in Path(impact_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise CTError(f"impact file line needs 'id = sentence': {line!r}")
            k, v = line.split("=", 1)
            impact[k.strip()] = v.strip()
    return impact


def cmd_commit(args) -> int:
    manifest = Path(args.manifest)
    impact = _read_impact_args(args)
    revision = args.revision or library_revision()
    role = "worker" if args.worker else args.role
    try:
        artifact, text = build_commitment(
            manifest, args.task, impact, revision,
            role=role, parent_bundle=args.parent_bundle, worker=args.worker,
            task_tags=(getattr(args, "tag", None) or []),
        )
    except CTError as e:
        print(f"CONTRACT GATE: BLOCKED\nCONTRACT COMMITMENT: INACTIVE\n\n{e}", file=sys.stderr)
        return 2
    out = Path(args.output) if args.output else default_artifact_path(role, args.task, manifest_path=manifest)
    if args.text_only:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(text)
    print()
    print(f"session artifact written: {out}")
    return 0


def cmd_session_status(args) -> int:
    manifest = Path(args.manifest) if args.manifest else None
    artifact_path = Path(args.artifact) if getattr(args, "artifact", None) else None
    role = getattr(args, "role", "session") or "session"
    task = getattr(args, "task", "") or ""
    summary, problems = session_status(manifest, artifact_path, role=role, task=task)
    print(summary)
    return 0 if not problems else 1


def cmd_validate_question(args) -> int:
    errors = validate_question(Path(args.question))
    if errors:
        print(f"QUESTION INVALID — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    data = json.loads(Path(args.question).read_text(encoding="utf-8"))
    print(f"QUESTION VALID — {data.get('schema')} ({data.get('question_id', data.get('request_id', '?'))}), status={data.get('status')}, blocking={data.get('blocking')}")
    return 0


def _resolve_project_dir(path: str) -> Path:
    p = Path(path)
    if p.name == ".project" or (p / "project.yaml").is_file():
        return p
    candidate = p / ".project"
    if candidate.is_dir():
        return candidate
    return p  # let validate report the miss clearly


def cmd_init_project(args) -> int:
    created = init_project(Path(args.target), args.id, args.name)
    if created:
        print("created:")
        for c in created:
            print(f"  {c}")
        print("\nnext: edit project.yaml purpose; pin adoption revision; add participant packs as needed")
        return 0
    print(".project/ already initialized (no files changed)")
    return 0


def cmd_project_validate(args) -> int:
    d = _resolve_project_dir(args.path)
    errors = validate_project(d)
    if errors:
        print(f"PROJECT INVALID — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    pm = _load_yaml_file(d / "project.yaml")
    packs = sorted(p.name for p in (d / "participants").iterdir() if p.is_dir()) if (d / "participants").is_dir() else []
    print(f"PROJECT VALID — {pm.get('id')} ({pm.get('name')}): {len(packs)} participant pack(s)")
    for name in packs:
        print(f"  - {name}")
    return 0


def cmd_participant_validate(args) -> int:
    errors = validate_participant(Path(args.path))
    if errors:
        print(f"PARTICIPANT INVALID — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    pm = _load_yaml_file(Path(args.path) / "participant.yaml")
    af = pm.get("relationship", {}).get("authoritative_for", [])
    naf = pm.get("relationship", {}).get("not_authoritative_for", [])
    print(f"PARTICIPANT VALID — {pm.get('id')} ({pm.get('type')})")
    print(f"  authoritative for: {', '.join(af)}")
    print(f"  NOT authoritative for: {', '.join(naf)}")
    return 0


def cmd_participant_list(args) -> int:
    d = _resolve_project_dir(args.path)
    pdir = d / "participants"
    if not pdir.is_dir():
        print("no participants directory")
        return 0
    packs = sorted(p for p in pdir.iterdir() if p.is_dir())
    if not packs:
        print("no participant packs")
        return 0
    for pack in packs:
        pman = pack / "participant.yaml"
        if not pman.is_file():
            print(f"{pack.name}: (missing participant.yaml)")
            continue
        try:
            pm = _load_yaml_file(pman)
        except CTError:
            print(f"{pack.name}: (unparseable manifest)")
            continue
        rel = pm.get("relationship", {})
        help_ = pm.get("help", {})
        pid = str(pm.get("id", pack.name))
        ptype = str(pm.get("type", "?"))
        prole = str(rel.get("role", "?"))
        print(f"{pid:20s} {ptype:18s} role={prole}")
        if isinstance(help_, dict) and help_.get("can_answer"):
            print(f"{'':20s} can answer: {', '.join(help_['can_answer'])}")
    return 0


def cmd_verify_attestation(args) -> int:
    att_path = Path(args.attestation)
    manifest = Path(args.manifest) if args.manifest else None
    errors = verify_attestation(att_path, manifest)
    if errors:
        print(f"ATTESTATION FAILED — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("ATTESTATION VERIFIED — receipts, hashes, versions, and bundle match the current library")
    return 0


def cmd_adopt(args) -> int:
    errors = validate_adoption_manifest(Path(args.manifest))
    errors += check_stale_pin(Path(args.manifest))
    if errors:
        print(f"ADOPTION INVALID — {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    m = load_adoption(Path(args.manifest))
    print(f"ADOPTION VALID — {m.get('project', 'unnamed')}: always={len(m.get('always', []))} triggers={len(m.get('triggers', {}))}")
    return 0


# ---------------------------------------------------------------- onboard

ROLE_KEYWORDS = {
    "orchestrator": {"agents", "orchestration", "project-management", "delegation"},
    "worker": {"agents", "automation", "engineering"},
    "ui": {"ui", "web", "product", "design"},
    "cli": {"cli", "tools"},
    "service": {"api", "infrastructure", "operations", "integration"},
    "human": {"humans", "product", "ui"},
}

ROLE_HIGH_PRIORITY = {
    "orchestrator": [
        "play-nice-together", "truth-and-evidence", "ask-for-help",
        "orchestration", "model-routing", "bounded-work", "handoff",
        "contract-attestation", "agent-behavior", "worker-contract",
        "review-and-integration", "participation-and-contribution",
        "mutual-contribution", "collaborative-good-faith",
    ],
    "worker": [
        "play-nice-together", "truth-and-evidence", "ask-for-help",
        "agent-behavior", "bounded-work", "handoff", "worker-contract",
        "contract-attestation", "testing-and-verification",
    ],
    "ui": [
        "play-nice-together", "accessibility-floor", "human-reliability",
        "attention-and-focus", "quiet-when-healthy", "copy-and-language",
        "themes-and-personalization", "motion-and-feedback",
        "migraine-and-sensory-safety", "low-vision-and-reflow",
        "visual-fidelity-and-composition", "web-ui",
    ],
    "cli": [
        "play-nice-together", "truth-and-evidence", "cli",
        "machine-readable-output", "human-and-machine-parity",
        "failure-and-degradation", "explicit-state",
    ],
    "service": [
        "play-nice-together", "truth-and-evidence", "api",
        "friendly-api-client", "idempotency", "failure-and-degradation",
        "authorization", "authentication", "secrets",
        "external-mutations", "versioning-and-compatibility",
    ],
    "human": [
        "play-nice-together", "human-reliability", "ask-for-help",
        "attention-and-focus", "progress-and-closure",
        "collaborative-good-faith", "copy-and-language",
    ],
}


def cmd_onboard(args) -> int:
    lib = load_library()
    errors = validate_library(lib)
    if errors:
        print("LIBRARY INVALID — fix before onboarding:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    role = args.role
    keywords = ROLE_KEYWORDS.get(role, set())
    high_ids = set(ROLE_HIGH_PRIORITY.get(role, []))

    # Classify: high-priority (explicit list) vs applicable (by metadata match) vs remaining
    high = []
    applicable = []
    remaining = []

    for c in sorted(lib, key=lambda x: x["front_matter"]["contract_id"]):
        fm = c["front_matter"]
        cid = fm["contract_id"]
        applies = set(fm.get("applies") or [])
        triggers = set(fm.get("triggers") or [])
        meta = applies | triggers

        if cid in high_ids:
            high.append(c)
        elif keywords & meta or "always" in triggers or "always-applicable" in triggers:
            applicable.append(c)
        else:
            remaining.append(c)

    # Promote always-triggered from applicable to high if not already there
    for c in list(applicable):
        triggers = set(c["front_matter"].get("triggers") or [])
        if "always" in triggers or "always-applicable" in triggers:
            if c not in high:
                high.append(c)
                applicable.remove(c)

    if getattr(args, "json_output", False):
        out = {
            "role": role,
            "trusted_translation": "docs/principles/trusted-translation.md",
            "quick_reference": "docs/QUICK_REFERENCE.md",
            "high_priority": [
                {"id": c["front_matter"]["contract_id"],
                 "version": str(c["front_matter"]["version"]),
                 "title": c["front_matter"]["title"]}
                for c in high
            ],
            "applicable": [
                {"id": c["front_matter"]["contract_id"],
                 "version": str(c["front_matter"]["version"]),
                 "title": c["front_matter"]["title"]}
                for c in applicable
            ],
            "remaining": [
                {"id": c["front_matter"]["contract_id"],
                 "version": str(c["front_matter"]["version"]),
                 "title": c["front_matter"]["title"]}
                for c in remaining
            ],
            "note": "This is an onboarding plan, not an attestation. Reading order is a suggestion; all contracts remain applicable where their metadata matches your work.",
        }
        print(json.dumps(out, indent=2))
        return 0

    # Human-readable output
    lib_ver = library_version()
    print(f"PLAY-NICE ONBOARDING — role: {role}")
    print(f"library: {lib_ver} ({len(lib)} contracts)")
    print()

    print("=== FIRST: READ THESE ===")
    print()
    print("  1. Trusted Translation (5-minute mental model)")
    print("     docs/principles/trusted-translation.md")
    print()
    print("  2. Quick Reference (reminder card)")
    print("     docs/QUICK_REFERENCE.md")
    print()

    print(f"=== HIGH-PRIORITY CONTRACTS FOR {role.upper()} ({len(high)}) ===")
    print()
    print("  Read these first. They are most likely to shape your work.")
    print()
    for i, c in enumerate(high, 1):
        fm = c["front_matter"]
        print(f"  {i:2d}. {fm['contract_id']}@{fm['version']}  — {fm['title']}")
        print(f"      {c['rel_path']}")
    print()

    if applicable:
        print(f"=== ALSO APPLICABLE ({len(applicable)}) ===")
        print()
        print("  These apply based on your role's triggers and metadata.")
        print()
        for c in applicable:
            fm = c["front_matter"]
            print(f"  - {fm['contract_id']}@{fm['version']}  — {fm['title']}")
        print()

    if remaining:
        print(f"=== REMAINING ({len(remaining)}) ===")
        print()
        print("  These may apply to specific tasks. Consult the contract index.")
        print()
        for c in remaining:
            fm = c["front_matter"]
            print(f"  - {fm['contract_id']}@{fm['version']}  — {fm['title']}")
        print()

    print("=== NEXT ===")
    print()
    print("  After reading, produce a CONTRACT ATTESTATION v1 block:")
    print(f"    contractctl attest --task 'your task' --impact ...")
    print()
    print("  This tool prepares onboarding; you perform it.")
    print("  A role determines reading order and emphasis, not permission or exemptions.")
    print("  All contracts remain applicable where their metadata matches your work.")

    return 0


def cmd_status(_args) -> int:
    lib = load_library()
    errors = validate_library(lib)
    n_canon = sum(1 for c in lib if c["front_matter"].get("status") == "canonical")
    lock_ok = not verify_lock(lib) if LOCKFILE.is_file() else False
    print(f"contracts: {len(lib)} ({n_canon} canonical)")
    print(f"validate:  {'PASS' if not errors else 'FAIL (' + str(len(errors)) + ')'}")
    print(f"lockfile:  {'VERIFIED' if lock_ok else 'MISSING/DRIFTED'}")
    print(f"revision:  {library_revision()}")
    return 0 if (not errors and lock_ok) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="contractctl", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="list contracts")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="print a contract's canonical content")
    p.add_argument("contract_id")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("validate", help="validate library + lockfile")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("resolve", help="resolve applicable contracts for a task")
    p.add_argument("--manifest", default=".contracts/adoption.yaml")
    p.add_argument("--task", default="")
    p.add_argument("--tag", action="append", default=[])
    p.set_defaults(func=cmd_resolve)

    p = sub.add_parser("lock", help="regenerate contracts.lock.json")
    p.set_defaults(func=cmd_lock)

    p = sub.add_parser("attest", help="produce CONTRACT_ATTESTATION v1")
    p.add_argument("--manifest", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--impact", action="append", default=[], metavar="ID=SENTENCE",
                   help="contract_id=sentence task-impact acknowledgement (repeatable)")
    p.add_argument("--impact-file", help="file of 'id = sentence' lines")
    p.add_argument("--revision", default="")
    p.add_argument("--tag", action="append", default=[],
                   help="explicit surface tags for trigger matching (repeatable)")
    p.set_defaults(func=cmd_attest)

    p = sub.add_parser("commit", help="activate CONTRACT OPERATIONAL COMMITMENT v1")
    p.add_argument("--manifest", required=True)
    p.add_argument("--task", required=True)
    p.add_argument("--impact", action="append", default=[], metavar="ID=SENTENCE",
                   help="contract_id=sentence task-impact acknowledgement (repeatable)")
    p.add_argument("--impact-file", help="file of 'id = sentence' lines")
    p.add_argument("--revision", default="")
    p.add_argument("--tag", action="append", default=[],
                   help="explicit surface tags for trigger matching (repeatable)")
    p.add_argument("--role", default="session", choices=["session", "orchestrator", "worker"],
                   help="participant role in the propagation tree")
    p.add_argument("--worker", action="store_true",
                   help="shortcut for --role worker; requires --parent-bundle")
    p.add_argument("--parent-bundle", default=None,
                   help="inherited contract bundle hash (workers must carry the parent bundle)")
    p.add_argument("--output", default=None,
                   help="where to write the session artifact (default: .contract-commitment.json in the library root)")
    p.add_argument("--text-only", action="store_true",
                   help="write the human-readable commitment text instead of JSON")
    p.set_defaults(func=cmd_commit)

    p = sub.add_parser("session-status", help="report current commitment state (ACTIVE/STALE/INACTIVE)")
    p.add_argument("--manifest", default=None,
                   help="adoption manifest; enables task-change re-resolution detection")
    p.add_argument("--artifact", default=None,
                   help="specific commitment artifact path (default: keyed .contract-commitments/)")
    p.add_argument("--role", default="session", choices=["session", "orchestrator", "worker"])
    p.add_argument("--task", default="", help="task key when looking up the keyed artifact")
    p.set_defaults(func=cmd_session_status)

    p = sub.add_parser("init-project", help="create a minimal .project/ skeleton (no empty directory forest)")
    p.add_argument("target", nargs="?", default=".", help="project root (default: current directory)")
    p.add_argument("--id", required=True, help="stable machine id (e.g. personal-world)")
    p.add_argument("--name", required=True, help="human name")
    p.set_defaults(func=cmd_init_project)

    p = sub.add_parser("project", help="project-context subcommands")
    psub = p.add_subparsers(dest="project_command", required=True)
    pv = psub.add_parser("validate", help="validate a .project/ directory")
    pv.add_argument("path", help="path to the .project/ directory (or its parent)")
    pv.set_defaults(func=cmd_project_validate)

    p = sub.add_parser("participant", help="participant-pack subcommands")
    psub2 = p.add_subparsers(dest="participant_command", required=True)
    pav = psub2.add_parser("validate", help="validate one participant pack directory")
    pav.add_argument("path", help="path to the participant pack directory")
    pav.set_defaults(func=cmd_participant_validate)
    pal = psub2.add_parser("list", help="list participant packs in a project")
    pal.add_argument("path", help="path to the .project/ directory (or its parent)")
    pal.set_defaults(func=cmd_participant_list)

    p = sub.add_parser("validate-question", help="validate a play-nice question / help-request / help-response artifact")
    p.add_argument("question", help="path to the JSON artifact (play-nice/question-v1 family)")
    p.set_defaults(func=cmd_validate_question)

    p = sub.add_parser("verify-attestation", help="verify an attestation against the library")
    p.add_argument("attestation")
    p.add_argument("--manifest", default=None)
    p.set_defaults(func=cmd_verify_attestation)

    p = sub.add_parser("adopt", help="validate a project adoption manifest")
    p.add_argument("--manifest", required=True)
    p.set_defaults(func=cmd_adopt)

    p = sub.add_parser("onboard", help="guided onboarding plan for a role")
    p.add_argument("--role", required=True,
                   choices=["orchestrator", "worker", "ui", "cli", "service", "human"],
                   help="participant role determining reading order and emphasis")
    p.add_argument("--json", action="store_true", dest="json_output",
                   help="machine-readable JSON output")
    p.set_defaults(func=cmd_onboard)

    p = sub.add_parser("status", help="one-line library health")
    p.set_defaults(func=cmd_status)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except CTError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())