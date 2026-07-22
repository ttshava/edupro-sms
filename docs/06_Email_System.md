# 06 — Email System

Outbound email uses Frappe's built-in Email Account / Email Queue
mechanism (SMTP) — no separate email service. Configured and
live-tested in production on Frappe Cloud.

## 6.1 Approach

- Outbound mail is sent via a Frappe **Email Account** (SMTP), not a
  third-party transactional email API.
- Bulk sends (report cards to a whole class/term) should be enqueued as
  background jobs (`frappe.enqueue`) rather than sent synchronously in a
  request/response cycle.
- Delivery status is tracked per message on the `Communication` record
  (`delivery_status`) and surfaced on `Report Card.sent_to_parent_at`.

## 6.2 Email Accounts (production)

Two accounts, both on `mail.firstclasshigh.ac.zw`:

| Account | Address | Role | Default |
|---|---|---|---|
| First Class High Outgoing | `admin@firstclasshigh.ac.zw` | Academic notifications, report cards | Yes (system default incoming + outgoing) |
| First Class High Support | `support@firstclasshigh.ac.zw` | Technical/support routing | No |

**Server settings (both accounts):**

| Direction | Protocol | Host | Port | Encryption |
|---|---|---|---|---|
| Incoming | POP3 | `mail.firstclasshigh.ac.zw` | 995 | SSL |
| Outgoing | SMTP | `mail.firstclasshigh.ac.zw` | 465 | SSL |

Credentials are stored only in the Email Account's encrypted `password`
field on the live site — never committed to this repository.

## 6.3 Branding

Both accounts have a custom **footer** overriding Frappe's default
"Sent via ERPNext" boilerplate:

> Sent via **Edupro SMS** ([www.edupro.co.zw](https://www.edupro.co.zw))

`admin@` additionally has a **signature** reading "Edupro SMS" (replacing
an earlier "First Class High School" signature line). To change either,
edit the Email Account's `footer` / `signature` fields in Desk — leaving
`footer` blank reverts to Frappe's default boilerplate, so it must stay
set explicitly.

## 6.4 Trigger

| Trigger | Recipient | Attachment |
|---|---|---|
| Report Card `workflow_state → Published` (end of `docs/04_Workflows.md` §4.2) | All guardians linked to the student (`Student.guardians`) | Report Card PDF |

## 6.5 Failure Handling

A per-guardian send failure is caught and logged via `frappe.log_error`
(visible in Desk's Error Log to Admin/System Manager) rather than
crashing the whole batch. Retry policy defaults to Frappe Email Queue's
built-in retry behavior.

**Known constraint:** `mail.firstclasshigh.ac.zw` validates recipients —
any guardian email address that isn't a real mailbox on that domain (or
elsewhere) will bounce. Only guardians with a real, deliverable email
address will actually receive mail.

## 6.6 Verifying Email Is Working

Send a test message via the API (or Desk's "New Email" compose) and
check the resulting `Communication.delivery_status`:

```
POST /api/method/frappe.core.doctype.communication.email.make
  recipients=<address>
  sender=admin@firstclasshigh.ac.zw
  subject=...
  content=...
  send_email=1
  now=1
```

`delivery_status: "Sent"` confirms SMTP authentication and delivery
succeeded. Cross-check the Error Log for anything tied to the real
account names (not the harmless `Test`/`_Test Email Account 1` fixture
accounts that ship with a fresh Frappe site).
