#!/usr/bin/env bash
# Restore drill for the local Galactica Workshop SQLite database.
#
# Copies a backup into a throwaway temp directory, opens the copy read-only and
# checks it (integrity, required tables, row counts vs. the manifest). It never
# opens or writes the live db.sqlite3.
#
# Usage:  ./scripts/restore_drill.sh [backup_path]
#         (default: newest *.sqlite3 under runtime/backups)
# Env:    GALACTICA_BACKUP_DIR   where to look for backups (default: <repo>/runtime/backups)
#         KEEP_DRILL=1           keep the temp dir for inspection
#         PYTHON                 interpreter (default: <repo>/.venv/bin/python, else python3)
#
# Exit codes: 0 PASS, 1 FAIL (details on stderr).
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${GALACTICA_BACKUP_DIR:-$APP_DIR/runtime/backups}"
LIVE_DB="$APP_DIR/db.sqlite3"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  sed -n '2,18p' "${BASH_SOURCE[0]}"
  exit 0
fi

PYTHON="${PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if [ -x "$APP_DIR/.venv/bin/python" ]; then
    PYTHON="$APP_DIR/.venv/bin/python"
  else
    PYTHON="python3"
  fi
fi
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "ERROR: python interpreter not found: $PYTHON" >&2
  exit 1
fi

BACKUP="${1:-}"
if [ -z "$BACKUP" ]; then
  if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERROR: backup directory not found: $BACKUP_DIR" >&2
    exit 1
  fi
  BACKUP="$(find "$BACKUP_DIR" -maxdepth 1 -type f -name '*.sqlite3' -printf '%T@ %p\n' \
    | sort -n | tail -n 1 | cut -d' ' -f2-)"
  if [ -z "$BACKUP" ]; then
    echo "ERROR: no *.sqlite3 backup found in $BACKUP_DIR" >&2
    exit 1
  fi
fi

if [ ! -f "$BACKUP" ]; then
  echo "ERROR: backup not found: $BACKUP" >&2
  exit 1
fi
BACKUP="$(cd "$(dirname "$BACKUP")" && pwd)/$(basename "$BACKUP")"
MANIFEST="$BACKUP.json"

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/galactica-restore-drill.XXXXXXXX")"
cleanup() {
  local status=$?
  if [ "${KEEP_DRILL:-0}" = "1" ]; then
    echo "kept temp dir: $TMP_DIR" >&2
  else
    rm -rf "$TMP_DIR"
  fi
  return "$status"
}
trap cleanup EXIT

RESTORED="$TMP_DIR/restored.sqlite3"
cp -- "$BACKUP" "$RESTORED"

# Informational only: the live db may legitimately change if the app is writing
# to it while the drill runs. The drill never opens it.
LIVE_DB_STATE="absent"
if [ -f "$LIVE_DB" ]; then
  LIVE_DB_STATE="sha256=$(sha256sum "$LIVE_DB" | cut -d' ' -f1) bytes=$(stat -c %s "$LIVE_DB")"
fi

echo "restore drill"
echo "  backup:   $BACKUP"
echo "  manifest: $([ -f "$MANIFEST" ] && echo "$MANIFEST" || echo 'none (counts not cross-checked)')"
echo "  temp:     $TMP_DIR (copy: $(basename "$RESTORED"))"
echo "  live db:  $LIVE_DB_STATE (not opened by this drill)"
echo

drill_status=0
"$PYTHON" - "$BACKUP" "$MANIFEST" "$RESTORED" <<'PY' || drill_status=$?
import hashlib
import json
import os
import sqlite3
import sys

backup_path, manifest_path, restored_path = sys.argv[1:4]
required_tables = [
    "core_article",
    "core_revision",
    "core_publicationevent",
    "core_claim",
    "core_citation",
    "core_searchdocument",
    "core_search_fts",
    "core_idempotencyrecord",
]
failures = []
warnings = []


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def report(ok, label, detail=""):
    mark = "ok  " if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f": {detail}" if detail else ""))
    if not ok:
        failures.append(f"{label}: {detail}" if detail else label)


print("checks")

# 1. Manifest (optional) and checksum.
manifest = None
if os.path.isfile(manifest_path):
    try:
        with open(manifest_path, encoding="utf-8") as fh:
            manifest = json.load(fh)
        report(True, "manifest", os.path.basename(manifest_path))
    except (OSError, ValueError) as exc:
        report(False, "manifest", f"unreadable: {exc}")
else:
    warnings.append("no manifest next to backup; row counts not cross-checked")
    report(True, "manifest", "none (skipped)")

backup_sha = sha256_file(backup_path)
if manifest is not None:
    expected = manifest.get("sha256")
    if expected:
        report(backup_sha == expected, "backup sha256", backup_sha)
    else:
        report(False, "backup sha256", "manifest has no sha256 field")
    expected_bytes = manifest.get("byte_count")
    if expected_bytes is not None:
        actual = os.path.getsize(backup_path)
        report(actual == expected_bytes, "byte_count", f"{actual} (manifest {expected_bytes})")
    report(
        manifest.get("integrity_check") == "ok",
        "manifest integrity_check",
        str(manifest.get("integrity_check")),
    )

restored_sha = sha256_file(restored_path)
report(restored_sha == backup_sha, "restored copy sha256 matches backup", restored_sha)
report(
    os.path.getsize(restored_path) == os.path.getsize(backup_path),
    "restored copy size matches backup",
    f"{os.path.getsize(restored_path)} bytes",
)

# 2. Open the restored copy read-only and verify it.
conn = None
try:
    conn = sqlite3.connect(f"file:{restored_path}?mode=ro", uri=True, timeout=5)
    rows = conn.execute("PRAGMA integrity_check").fetchall()
    integrity = "; ".join(row[0] for row in rows)
    report(integrity == "ok", "PRAGMA integrity_check", integrity)

    present = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    missing = [t for t in required_tables if t not in present]
    report(not missing, "required tables present", f"{len(required_tables)} tables"
           if not missing else f"missing: {', '.join(missing)}")

    counts = {}
    for table in required_tables:
        if table in present:
            counts[table] = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

    print("row counts")
    for table in required_tables:
        if table in counts:
            print(f"  {table:<28} {counts[table]}")

    if manifest is not None and manifest.get("row_counts"):
        mismatch = []
        for table, expected in manifest["row_counts"].items():
            actual = counts.get(table)
            if actual != expected:
                mismatch.append(f"{table}: backup={actual} manifest={expected}")
        report(not mismatch, "row counts match manifest",
               "all match" if not mismatch else "; ".join(mismatch))
    elif manifest is not None:
        warnings.append("manifest has no row_counts; skipped count comparison")
except sqlite3.Error as exc:
    report(False, "open restored copy read-only", str(exc))
finally:
    if conn is not None:
        conn.close()

print()
for warning in warnings:
    print(f"  note: {warning}")
if failures:
    print()
    print("FAIL: restore drill failed")
    for item in failures:
        print(f"  - {item}")
    sys.exit(1)
print("PASS: restore drill succeeded")
PY

echo
if [ "$drill_status" -ne 0 ]; then
  echo "RESULT: FAIL (drill exit $drill_status)" >&2
  exit 1
fi

if [ -f "$MANIFEST" ]; then
  echo "RESULT: PASS — restored copy opened read-only, integrity ok, required tables present, counts match manifest"
else
  echo "RESULT: PASS — restored copy opened read-only, integrity ok, required tables present (no manifest to compare)"
fi
echo "live db was not opened or modified by this drill: $LIVE_DB"
exit 0
