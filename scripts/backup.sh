#!/usr/bin/env bash
# Online backup of the local Galactica Workshop SQLite database.
#
# Uses the SQLite online backup API, which is safe while the app is running
# and in WAL mode. Produces:
#   <backup_dir>/galactica-<UTC timestamp>.sqlite3      the backup
#   <backup_dir>/galactica-<UTC timestamp>.sqlite3.json manifest (sha256, counts, ...)
#
# Usage:  ./scripts/backup.sh [db_path]
# Env:    GALACTICA_DB           source db (default: <repo>/db.sqlite3)
#         GALACTICA_BACKUP_DIR   output dir (default: <repo>/runtime/backups)
#         PYTHON                 interpreter (default: <repo>/.venv/bin/python, else python3)
#
# Exit codes: 0 backup written and verified, 1 any failure.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="${GALACTICA_DB:-$APP_DIR/db.sqlite3}"
BACKUP_DIR="${GALACTICA_BACKUP_DIR:-$APP_DIR/runtime/backups}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  sed -n '2,18p' "${BASH_SOURCE[0]}"
  exit 0
fi
if [ -n "${1:-}" ]; then
  DB="$1"
fi

if [ ! -f "$DB" ]; then
  echo "ERROR: source database not found: $DB" >&2
  exit 1
fi
if [ ! -r "$DB" ]; then
  echo "ERROR: source database not readable: $DB" >&2
  exit 1
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

mkdir -p "$BACKUP_DIR"
if [ ! -w "$BACKUP_DIR" ]; then
  echo "ERROR: backup directory not writable: $BACKUP_DIR" >&2
  exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
TARGET="$BACKUP_DIR/galactica-$STAMP.sqlite3"
if [ -e "$TARGET" ]; then
  TARGET="$BACKUP_DIR/galactica-$STAMP-$$.sqlite3"
fi
MANIFEST="$TARGET.json"
TMP_MANIFEST="$MANIFEST.tmp.$$"
trap 'rm -f "$TMP_MANIFEST"' EXIT

DB="$DB" TARGET="$TARGET" PYTHON="$PYTHON" TMP_MANIFEST="$TMP_MANIFEST" \
  "$PYTHON" - <<'PY'
import hashlib
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone

db_path = os.path.abspath(os.environ["DB"])
target = os.path.abspath(os.environ["TARGET"])
manifest_path = os.path.abspath(os.environ["TMP_MANIFEST"])
final_manifest = target + ".json"
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
started = time.time()


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def store_counts(conn):
    counts = {}
    for table in required_tables:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()
        if not exists:
            fail(f"required table missing in backup: {table}")
        counts[table] = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    return counts


# 1. Online backup via the SQLite backup API (equivalent to `.backup`).
#    Prefer a read-only source connection; fall back to a normal one when the
#    WAL sidecar files are missing (a read-only connection cannot create -shm).
open_mode = "read-only"
try:
    src = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
    src.execute("SELECT 1 FROM sqlite_master LIMIT 1").fetchone()
except sqlite3.Error:
    open_mode = "read-write"
    src = sqlite3.connect(db_path, timeout=5)

journal_mode = src.execute("PRAGMA journal_mode").fetchone()[0]
src.execute("PRAGMA busy_timeout = 10000")

dst = sqlite3.connect(target, timeout=5)
try:
    with dst:
        src.backup(dst, pages=-1)
    # Normalise the copy to a rollback journal so the backup is one
    # self-contained file: no -wal/-shm sidecars are needed to read it.
    dst.execute("PRAGMA journal_mode=DELETE").fetchone()
    dst.execute("SELECT 1 FROM sqlite_master LIMIT 1").fetchone()
finally:
    dst.close()
    src.close()

# A stale sidecar next to the backup is never restored, so treat any non-empty
# one as a failure; empty leftovers are safe to drop.
for suffix in ("-wal", "-shm"):
    sidecar = target + suffix
    if os.path.exists(sidecar):
        if os.path.getsize(sidecar) == 0:
            os.remove(sidecar)
        else:
            fail(f"unexpected non-empty sidecar next to backup: {sidecar}")

if not os.path.isfile(target) or os.path.getsize(target) == 0:
    fail(f"backup file missing or empty: {target}")

# 2. Verify the backup itself: integrity + schema + row counts.
conn = sqlite3.connect(f"file:{target}?mode=ro", uri=True, timeout=5)
try:
    integrity_rows = conn.execute("PRAGMA integrity_check").fetchall()
    integrity = "; ".join(row[0] for row in integrity_rows)
    if integrity != "ok":
        fail(f"backup integrity_check failed: {integrity}")
    row_counts = store_counts(conn)
    sqlite_version = conn.execute("SELECT sqlite_version()").fetchone()[0]
    backup_journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
finally:
    conn.close()

# 3. Checksum and manifest.
h = hashlib.sha256()
with open(target, "rb") as fh:
    for chunk in iter(lambda: fh.read(1024 * 1024), b""):
        h.update(chunk)
sha256 = h.hexdigest()
byte_count = os.path.getsize(target)

manifest = {
    "schema_version": 1,
    "kind": "sqlite-online-backup",
    "tool": "scripts/backup.sh",
    "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "source_path": db_path,
    "backup_path": target,
    "sha256": sha256,
    "byte_count": byte_count,
    "integrity_check": integrity,
    "source_journal_mode": journal_mode,
    "source_open_mode": open_mode,
    "backup_journal_mode": backup_journal_mode,
    "sqlite_version": sqlite_version,
    "required_tables": required_tables,
    "row_counts": row_counts,
    "elapsed_ms": int((time.time() - started) * 1000),
    "note": "local M0 drill backup; not a production backup or off-host copy",
}

with open(manifest_path, "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=2, sort_keys=True)
    fh.write("\n")
os.replace(manifest_path, final_manifest)

print(f"backup:      {target}")
print(f"manifest:    {final_manifest}")
print(f"sha256:      {sha256}")
print(f"bytes:       {byte_count}")
print(f"integrity:   {integrity}")
print(f"journal:     source={journal_mode}, backup={backup_journal_mode} (opened {open_mode})")
print("row_counts:")
for name in required_tables:
    print(f"  {name:<28} {row_counts[name]}")
print(f"elapsed_ms:  {manifest['elapsed_ms']}")
print("OK: backup completed and verified")
PY

if [ ! -s "$MANIFEST" ]; then
  echo "ERROR: manifest was not written: $MANIFEST" >&2
  exit 1
fi

echo "OK: $TARGET"
