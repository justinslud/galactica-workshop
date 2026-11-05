# Operations: SQLite online backup and restore drill

Status: **local M0 drill only.** These scripts have been run against this
checkout and the drill passed on **2026-11-05**. This is not a production
backup system: backups are manual, local-disk only, and never copied off-host.
Do not treat it as disaster recovery or as a guarantee of recoverability.

## What exists

| Path | Purpose |
| --- | --- |
| `scripts/backup.sh` | Online backup of `db.sqlite3` via the SQLite backup API, integrity check, SHA-256, JSON manifest |
| `scripts/restore_drill.sh` | Restores the newest (or a chosen) backup into a temp dir, opens it read-only, verifies it |
| `runtime/backups/` | Backup output; `runtime/` is gitignored, so nothing here is committed |

Requirements: `bash`, and Python 3 with the stdlib `sqlite3` module (the
`sqlite3` CLI is **not** installed on this VM, so the Python backup API is
used). No secrets are stored in the scripts or the manifest.

## Backup

```bash
cd /home/vboxuser/projects/galactica-workshop
./scripts/backup.sh                 # backs up ./db.sqlite3
./scripts/backup.sh /path/to.sqlite3  # explicit source
```

Optional environment overrides: `GALACTICA_DB`, `GALACTICA_BACKUP_DIR`,
`PYTHON`.

What it does, in order:

1. Creates `runtime/backups/` if missing.
2. Opens the source **read-only** where possible (falls back to a normal
   connection if the `-wal`/`-shm` sidecars are absent) and copies it with the
   SQLite online backup API. Safe while the app is running and in WAL mode.
3. Normalises the copy to a rollback journal, so a backup is **one
   self-contained `.sqlite3` file** with no `-wal`/`-shm` sidecars.
4. Runs `PRAGMA integrity_check` on the backup and requires `ok`.
5. Records SHA-256, byte count, and row counts for `core_article`,
   `core_revision`, `core_publicationevent`, `core_claim`, `core_citation`, `core_searchdocument`,
   `core_search_fts`, `core_idempotencyrecord`.
6. Writes a sidecar manifest next to the backup:
   `galactica-<UTC timestamp>.sqlite3.json` (created_at UTC ISO, source and
   backup paths, sha256, byte_count, integrity_check, row_counts, journal
   modes, sqlite version).

It prints the backup path, sha256, integrity and row counts, and exits non-zero
on any failure. The manifest is written after verification, so a `.json` only
exists for a backup that passed.

The backup file's SHA-256 **will not** equal the SHA-256 of the live
`db.sqlite3`: the copy is checkpointed and journal-normalised. Compare a backup
against its own manifest, never against the live file.

## Restore drill

```bash
cd /home/vboxuser/projects/galactica-workshop
./scripts/restore_drill.sh                       # newest backup in runtime/backups
./scripts/restore_drill.sh runtime/backups/galactica-YYYYmmddTHHMMSSZ.sqlite3
KEEP_DRILL=1 ./scripts/restore_drill.sh          # keep the temp dir for inspection
```

What it does: creates a temp dir, copies the chosen backup to
`<temp>/restored.sqlite3`, and opens **only the copy**, read-only. It checks:

- the backup SHA-256 and byte count match the manifest (when present);
- the restored copy's SHA-256 and size match the backup;
- `PRAGMA integrity_check` is `ok`;
- the eight required tables exist;
- row counts match the manifest's `row_counts` (when present).

It prints a per-check list plus a `PASS`/`FAIL` summary and exits non-zero on
failure. `KEEP_DRILL=1` keeps the temp dir. The temp dir is removed
otherwise, including on failure. The drill never opens the live `db.sqlite3`;
the live file's SHA-256/size are printed before the run for reference, and the
app may legitimately change them while the drill runs.

A missing manifest is not a failure: the drill runs in degraded mode (integrity
and tables only) and says row counts were not cross-checked.

## Restore procedure (manual, destructive)

Only do this when you intend to replace the live database. Keep the current
`db.sqlite3` first so the operation is reversible.

1. Stop the app: `./scripts/local.sh stop`
2. Confirm nothing is writing: `./scripts/local.sh status` should say
   `not running`.
3. Keep the current database:
   `mkdir -p runtime/backups && cp db.sqlite3 "runtime/backups/pre-restore-$(date -u +%Y%m%dT%H%M%SZ).sqlite3"`
4. Copy the chosen backup over the live path:
   `cp runtime/backups/galactica-<stamp>.sqlite3 db.sqlite3`
5. Remove stale WAL sidecars so old WAL frames cannot be replayed over the
   restored file: `rm -f db.sqlite3-wal db.sqlite3-shm`
6. Start the app: `./scripts/local.sh start`
7. Verify: the app loads; `./scripts/local.sh status` shows the processes; spot
   check article/dashboard counts against the manifest's `row_counts`; run
   `./scripts/restore_drill.sh` again if you want a second read of the chosen
   backup.

Do not copy a backup over `db.sqlite3` while the app is running, and do not
delete `db.sqlite3-wal` on a running app.

## RPO / RTO caveat

- **RPO:** there is no schedule. The recovery point is the last backup you ran
  by hand, so RPO is unbounded until someone runs `./scripts/backup.sh`. The
  scripts do not back up automatically, on write, or on a timer.
- **RTO:** roughly minutes (stop app, copy one file, remove sidecars, start,
  spot check), but it is a manual, un-rehearsed-on-real-data procedure. The
  drill verified the backup copy, not an actual live-database replacement.
- Backups live under the same `runtime/` tree on the same disk as the live
  database. Disk loss or host loss takes both. There is no off-host copy,
  retention policy, encryption, or pruning. Nothing here proves
  production readiness.

## An export is not a backup

A JSON/CSV export, an admin dump, or a `cp db.sqlite3` is **not** a backup:

- exports usually omit schema details, indexes, FTS tables, constraints, and
  internal SQLite state, and must be re-imported through application logic;
- a plain file copy of `db.sqlite3` can miss pages still in `db.sqlite3-wal`
  and is unsafe while the app runs;
- neither carries the integrity check, checksum, or row-count manifest that
  makes a restore verifiable.

Use `scripts/backup.sh` output (the `.sqlite3` plus `.json` sidecar) as the
only authoritative backup artefact.

## Drill record: 2026-11-05

Environment: local VM checkout, Django app running on `127.0.0.1:8001`, live db
in WAL mode, Python 3.14.4, SQLite 3.46.1. `sqlite3` CLI and `shellcheck` were
not installed; scripts were validated with `bash -n` and by running them.

Commands run (from the repo root):

```bash
./scripts/backup.sh
./scripts/restore_drill.sh
```

Backup produced:

- path: `runtime/backups/galactica-20261105T152506Z.sqlite3`
- sha256: `6e2463f6ad502e54bbef31766fd063d4b32c0c4024529d956804e99d760b94cd`
- bytes: 1,343,488
- integrity_check: `ok`
- source journal mode: `wal`; backup journal mode: `delete` (single file)

Row counts recorded in the manifest and re-verified by the drill:

| table | rows |
| --- | --- |
| `core_article` | 6 |
| `core_revision` | 25 |
| `core_publicationevent` | 6 |
| `core_claim` | 47 |
| `core_citation` | 263 |
| `core_searchdocument` | 3 |
| `core_search_fts` | 3 |
| `core_idempotencyrecord` | 0 |

Drill result: **PASS** — manifest checksum and byte count matched, the restored
copy's SHA-256 matched the backup, `PRAGMA integrity_check` returned `ok`, all
eight required tables were present, and every row count matched the manifest.
The drill wrote only to `/tmp`, removed its temp dir, and left the live
`db.sqlite3` untouched (same SHA-256 and mtime before and after; the app was
never stopped or restarted).

Caveats for this record:

- This validates the backup file, not a real restore into the live path.
- The backup remains local-only under `runtime/backups/`.
- `shellcheck` was unavailable, so linting was limited to `bash -n`.
- Row counts are a point-in-time snapshot; a running app can change them before
  the next backup.
