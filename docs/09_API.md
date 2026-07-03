# 09 — API

## 9.1 Approach

MVP is Frappe Desk + Frappe portal pages for Student/Parent access — no
separate public API surface is required to ship MVP. Frappe's standard
REST API (`/api/resource/<DocType>`, `/api/method/<path>`) is
auto-generated and available for any future integration (mobile app,
external portal) without extra work.

## 9.2 Authentication

The source spec calls for JWT authentication. For MVP, use **Frappe's
native session-cookie authentication** for Desk/portal users — that's what
Frappe Desk and portal pages use natively, and adding JWT on top would be
unnecessary complexity for a server-rendered MVP. For any programmatic/API
client access (e.g. a future custom frontend), use **Frappe API Key/Secret
token auth**, which Frappe supports out of the box.

Revisit JWT specifically only if/when a separate SPA or mobile client is
built post-MVP and needs stateless auth across a different domain.

## 9.3 Conventions (for any custom `@frappe.whitelist()` endpoints)

- RESTful shape where practical; Frappe's method whitelisting convention
  is `/api/method/edupro_sms.<module>.<file>.<function>` for anything not
  covered by the generic resource API.
- Use Frappe's standard response codes/exceptions (`frappe.throw`,
  `frappe.PermissionError`, etc.) rather than inventing a custom error
  envelope.
- Paginate list-returning endpoints (Frappe's `frappe.get_list` supports
  `limit_start`/`limit_page_length` natively — use it).
- Every custom endpoint must go through the same permission checks as the
  Desk UI would (`frappe.has_permission`) — never assume `@frappe.whitelist`
  alone is sufficient access control.

## 9.4 Rate Limiting

Not built into Frappe by default. If the pilot school's site is
internet-facing, add rate limiting at the Nginx layer rather than in
application code (see `docs/08_Deployment.md` §8.4).

## 9.5 Custom Endpoints Log

Document any `@frappe.whitelist()` methods here as they're added:

### Template

**`<method path>`** — Purpose / Method (GET/POST) / Auth (role required) /
Params / Returns

None implemented yet.
