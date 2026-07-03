# Changelog — Edupro SMS

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/); dates in
YYYY-MM-DD.

## [Unreleased]

### Added

- Project documentation scaffolding: `.claude/CLAUDE.md`,
  `PROJECT_CONTEXT.md`, `TASKS.md`, `DECISIONS.md`, `CODING_STANDARDS.md`,
  `CHANGELOG.md`, and `docs/01`–`10` skeletons.
- Ingested full IGCSE functional specification (roles, data model, IGCSE
  grading, approval workflow, print/email specs, testing, deployment) into
  `docs/01`–`11`, replacing the earlier generic skeletons with real specs.
  `docs/` is now the technical source of truth per module; `.claude/`
  updated to point into it rather than duplicate content.
- Added `docs/11_Roles_And_Permissions.md` (new — role capability matrix,
  not in the original 10-file skeleton).
- Logged two open architecture decisions in `DECISIONS.md`: 0004
  (multi-tenancy via site-per-school, not shared `School` table — default
  recommendation, pending owner confirmation) and 0005 (evaluate reusing
  Frappe's Education app before building DocTypes from scratch — open,
  decide before Sprint 2).
- Updated MVP scope, role list (added Class Teacher), and sprint plan in
  `PROJECT_CONTEXT.md`/`TASKS.md` to match the ingested spec.
- Resolved both open decisions: 0004 (site-per-school multi-tenancy)
  accepted; 0005 (Frappe Education app) accepted as "spike first in
  Sprint 1, then decide build path" — see `DECISIONS.md`.

---

## 2026-07-03

### Added

- Initial project scaffolding decided: Frappe Framework, Docker-on-Windows
  dev environment, custom app `edupro_sms`. See `DECISIONS.md` 0001–0003.
