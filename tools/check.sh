#!/usr/bin/env bash
# check.sh — the full deterministic gate, one command (mirrors CI's library job).
#
# Usage: ./tools/check.sh          (from a library checkout)
# Exit 0 = everything green. Any failure prints what failed and why.
set -euo pipefail

cd "$(dirname "$0")/.."
CT="python3 tools/contractctl/contractctl.py"

echo "==> validate library + lockfile"
$CT validate

echo "==> lock determinism (regenerate twice, byte-compare)"
tmp1=$(mktemp); tmp2=$(mktemp)
trap 'rm -f "$tmp1" "$tmp2"' EXIT
cp contracts.lock.json "$tmp1"
$CT lock >/dev/null
cp contracts.lock.json "$tmp2"
$CT lock >/dev/null
cmp -s "$tmp1" contracts.lock.json || {
  echo "FAIL: committed lock differs from regeneration — run: $CT lock and commit"; exit 1; }
cmp -s "$tmp2" contracts.lock.json || {
  echo "FAIL: lock regeneration is not deterministic (two runs differ)"; exit 1; }
echo "lock regeneration byte-identical"

echo "==> test suite"
if python3 -c "import pytest, yaml" 2>/dev/null; then
  python3 -m pytest tests/ -q
else
  echo "(pytest/pyyaml not in this interpreter; using uv)"
  uv run --python 3.12 --with pytest,pyyaml python3 -m pytest tests/ -q
fi

echo "==> secret / private-material scan (library surfaces)"
python3 - <<'PYEOF'
import sys
from pathlib import Path
banned = ["gh" + "p_", "gh" + "o_", "AK" + "IA",
          "BEGIN PRIVATE " + "KEY", "BEGIN " + "RSA",
          "192.168" + ".", "hulganfamily.duck" + "dns.org", "10.0" + "."]
repo = Path(".")
hits = []
for f in repo.rglob("*"):
    if not f.is_file() or any(p in f.parts for p in (".git", ".venv", "__pycache__", ".pytest_cache", ".contract-commitments")):
        continue
    try:
        text = f.read_text()
    except (UnicodeDecodeError, ValueError):
        continue
    for b in banned:
        if b in text:
            hits.append(f"{f}: contains {b!r}")
if hits:
    print("\n".join(hits))
    sys.exit(1)
print("secret/private-material scan clean")
PYEOF

echo "==> commit identity guard (last 20 commits vs allowed classes)"
# Mirrors CI's guard: a commit whose committer is exactly the GitHub
# wrapper (noreply@github.com) is skipped wholesale — its author email was
# checked when the PR event ran, and wrapper authors come from account
# settings, not local git config.
BAD=$(git log -20 --format='%ae %ce' | awk \
      '$2=="noreply@github.com"{next} {print $1; print $2}' | sort -u \
      | grep -Ev '@users\.noreply\.github\.com$|@[A-Za-z0-9.-]*[.]invalid$' || true)
if [ -n "$BAD" ]; then
  echo "FAIL: disallowed identity emails in recent history:"; echo "$BAD"; exit 1
fi
echo "identity guard: all recent emails noreply/.invalid"

echo ""
echo "CHECK: PASS"
