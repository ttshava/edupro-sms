# 13 — Backup & Restore

## 13.1 What's backed up

A Frappe site backup is four files, all generated together by one
`bench backup --with-files` run:

| File | Contents |
|---|---|
| `<timestamp>-edupro_localhost-database.sql.gz` | Full MariaDB dump — every DocType record: students, guardians, staff, marks, fees, ledger entries, everything. |
| `<timestamp>-edupro_localhost-files.tar` | Public files (e.g. the School Settings logo). |
| `<timestamp>-edupro_localhost-private-files.tar` | Private files (generated report card / receipt / statement PDFs attached to documents). |
| `<timestamp>-edupro_localhost-site_config_backup.json` | A copy of `site_config.json` at backup time — `db_name`, `db_password`, `encryption_key`, `host_name`. |

The four files together are self-contained: restoring them recreates the
site exactly, including decrypting any encrypted fields, without needing
anything else from the original machine.

## 13.2 Where backups live in this repo

`backups/` is **gitignored by default** (`backups/*` in `.gitignore`) —
routine backups are working data, not source, and git is a poor fit for
recurring binary dumps (every backup permanently grows repo history, and
committing one implies everyone with repo access can read the full
student database, including old snapshots, forever — even if a later
commit deletes the file).

One dated snapshot is committed as a deliberate, explicit exception (see
the `.gitignore` comment above the `!backups/2026...` lines) — a
disaster-recovery baseline the owner asked to have in version control.
**This is not a standing policy.** Future backups stay untracked unless
someone deliberately un-ignores that exact filename the same way. Don't
change `backups/*` to a blanket allow.

**Handle this repo's access accordingly:** the committed backup contains
real student/guardian PII, financial records, and — via
`site_config_backup.json` — the live database password and encryption
key for the site that data came from. Treat repo access as equivalent to
database access.

## 13.3 Taking a new backup

```bash
docker exec edupro-backend-1 bench --site edupro.localhost backup --with-files
```

Pull the four resulting files out of the container onto the host (path
matches whatever `bench` printed as the backup summary):

```bash
docker cp edupro-backend-1://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-database.sql.gz       "backups/"
docker cp edupro-backend-1://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-files.tar               "backups/"
docker cp edupro-backend-1://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-private-files.tar       "backups/"
docker cp edupro-backend-1://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-site_config_backup.json "backups/"
```

(Note the double slash after the container name — `edupro-backend-1://home/...` — Git Bash on Windows otherwise mangles the absolute container path into a Windows path.)

## 13.4 Restoring from a backup

On a fresh or existing site, from inside the `backend` container
(`docker compose -p edupro -f compose.edupro.yaml exec backend bash`):

```bash
bench --site edupro.localhost restore \
  backups/<timestamp>-edupro_localhost-database.sql.gz \
  --with-public-files backups/<timestamp>-edupro_localhost-files.tar \
  --with-private-files backups/<timestamp>-edupro_localhost-private-files.tar \
  --encryption-key "<encryption_key from the matching site_config_backup.json>"
```

**The `--encryption-key` flag is not optional in practice.** Without the
original key, `bench restore` still succeeds, but every encrypted field
in the restored database (e.g. stored email account passwords) becomes
permanently unreadable — Frappe cannot re-derive a lost key. Always pull
the key from the `site_config_backup.json` that was generated in the
*same* `bench backup` run as the database dump you're restoring, never
from a different backup or from memory.

After restoring, re-point the site at whatever LAN IP the new machine
actually uses:

```bash
bench --site edupro.localhost set-config host_name "http://<new-ip>:8080"
```

See `docs/08_Deployment.md` §8.1 for the rest of a from-scratch server
setup (building the image, the `extra_hosts` hairpin-NAT fix, etc.) — a
restore is only the data half of standing up a new server.

## 13.5 What this is not

A one-off committed backup is a **snapshot**, not a **backup strategy**.
It captures the database as of the moment it was taken and goes stale
immediately as new marks, payments, and students are entered. For actual
ongoing protection:

- Automate `bench backup --with-files` on a schedule (cron / Windows
  Task Scheduler) — Frappe's own `bench` supports this directly.
- Keep the automated backups **out of git** (default `backups/*`
  behavior) and instead sync them to dedicated backup storage (encrypted
  cloud storage, a network drive, an offsite copy) with its own
  retention policy.
- Test the restore procedure above periodically against a scratch site —
  a backup that's never been restored is unverified.

`docs/01_Project_Overview.md` §1.6 has the target backup cadence for
ongoing support/maintenance once the school is live.
