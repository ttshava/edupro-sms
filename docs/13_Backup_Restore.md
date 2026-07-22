# 13 — Backup & Restore

## 13.1 What's in a Backup

A Frappe site backup is four files, generated together by one
`bench backup --with-files` run:

| File | Contents |
|---|---|
| `<timestamp>-<site>-database.sql.gz` | Full MariaDB dump — every DocType record |
| `<timestamp>-<site>-files.tar` | Public files (e.g. the School Settings logo) |
| `<timestamp>-<site>-private-files.tar` | Private files (generated PDFs, attachments) |
| `<timestamp>-<site>-site_config_backup.json` | A copy of `site_config.json` — `db_name`, `db_password`, `encryption_key`, `host_name` |

The four files together are self-contained: restoring them recreates
the site exactly, including decrypting encrypted fields, without
needing anything else from the original machine.

## 13.2 Production (Frappe Cloud)

Use the site's **Backups** tab in the Frappe Cloud dashboard for
scheduled/on-demand backups, and **Actions → Restore with files** to
restore from an uploaded backup.

**When restoring a backup from a different app version** (e.g. a local
v15 backup onto a v16 site), Frappe Cloud runs the schema migration
automatically as part of the restore — see `docs/08_Deployment.md` §8.2
for the known search-index migration issue and its workaround.

**If the source site had apps not installed on the target bench,** they
must either be added to the bench first, or excluded from the restore.
Frappe Cloud's restore flow will uninstall apps it can't find on the
target bench rather than fail outright — confirm afterward that no
needed app/data was silently dropped.

## 13.3 Local Development (Docker)

```bash
docker exec <backend-container> bench --site edupro.localhost backup --with-files
```

Pull the four resulting files out of the container onto the host:

```bash
docker cp <backend-container>://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-database.sql.gz       "backups/"
docker cp <backend-container>://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-files.tar               "backups/"
docker cp <backend-container>://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-private-files.tar       "backups/"
docker cp <backend-container>://home/frappe/frappe-bench/sites/edupro.localhost/private/backups/<timestamp>-edupro_localhost-site_config_backup.json "backups/"
```

(Note the double slash after the container name on Git Bash for
Windows — otherwise the absolute container path gets mangled into a
Windows path.)

### Restoring locally

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
permanently unreadable. Always pull the key from the
`site_config_backup.json` generated in the *same* backup run as the
database dump being restored.

## 13.4 Repository Hygiene

`backups/` is gitignored — routine backups are working data, not
source, and committing recurring database dumps permanently grows repo
history while exposing student PII and financial records to anyone with
repo access. Don't add an exception without a specific, deliberate
reason.

## 13.5 What This Is Not

A one-off backup is a **snapshot**, not a **backup strategy** — it goes
stale the moment new marks, payments, or students are entered. For
actual ongoing protection:

- Schedule backups (Frappe Cloud's dashboard, or cron/Task Scheduler
  locally).
- Keep backups out of git; sync to dedicated backup storage with its
  own retention policy.
- Periodically test the restore procedure against a scratch site — a
  backup that's never been restored is unverified.
