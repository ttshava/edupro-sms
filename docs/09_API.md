# 09 — API

## 9.1 Approach

The system is Frappe Desk + Frappe portal pages for Student/Guardian
access — no separate public API surface is required. Frappe's standard
REST API (`/api/resource/<DocType>`, `/api/method/<path>`) is
auto-generated and available for any future integration (mobile app,
external portal) without extra work.

## 9.2 Authentication

- **Desk/portal users:** Frappe's native session-cookie authentication —
  the same mechanism Desk and portal pages use natively.
- **Programmatic/API clients:** Frappe API Key/Secret token auth, which
  Frappe supports out of the box.

## 9.3 Conventions

- RESTful shape where practical; custom whitelisted endpoints follow
  `/api/method/edupro_sms.<module>.<function>`.
- Use Frappe's standard response/exception patterns (`frappe.throw`,
  `frappe.PermissionError`) rather than inventing a custom error
  envelope.
- Paginate list-returning endpoints (`frappe.get_list`'s
  `limit_start`/`limit_page_length`).
- Every custom endpoint must go through the same permission checks as
  the Desk UI would (`frappe.has_permission`) — `@frappe.whitelist`
  alone is not access control.

## 9.4 Rate Limiting

Not built into Frappe by default. Add at the reverse-proxy layer if the
site is ever exposed to high-volume external traffic.

## 9.5 Custom Endpoints

Whitelisted methods worth knowing about:

| Method | Purpose |
|---|---|
| `edupro_sms.report_card.generate_report_cards` | Generate/update Report Cards for a Student Group + Academic Term |
| `edupro_sms.qr.report_card_verification_qr_data_uri` | Jinja helper — QR code for report-card authenticity |
| `edupro_sms.watermark.report_card_watermark_data_uri` | Jinja helper — report-card watermark image |
| `edupro_sms.fees.get_student_fee_statement` / `get_student_ledger` | Jinja helpers — fee statement / ledger rendering |
