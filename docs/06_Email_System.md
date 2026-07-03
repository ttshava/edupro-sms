# 06 — Email System

**Built and verified, Sprint 7** (`edupro_sms/edupro_sms/doctype/report_card/notify.py`).
Real SMTP delivery is still a deployment-time task — see §6.6.

## 6.1 Approach

- Outbound email via Frappe's built-in Email Queue (SMTP), configured
  against an Email Account in Frappe settings — no separate email service
  for MVP.
- Bulk sends (report cards to all parents in a class/term) are enqueued as
  RQ background jobs (`frappe.enqueue`) — never sent synchronously in a
  request/response cycle. Target: 1,000 emails/hr (single school), see
  `docs/08_Deployment.md`.
- Delivery status is logged per recipient (sent/failed), surfaced on the
  `Report Card` (`sent_to_parent_at`) and available for a Headmaster/Admin
  delivery report.

## 6.2 Trigger

| Trigger | Recipient | Attachment |
|---|---|---|
| Report Card status → `Published` (end of `docs/04` §4.2 workflow) | All guardians linked to the student (`Student.guardians`) | Report Card PDF |

## 6.3 Subject Line

```
📊 Report Card - {Student Name} - {Term} - {Academic Year}
```

## 6.4 Email Body Template

Rendered as an HTML email (Frappe email template / Jinja), summarizing
results with a link into the parent portal:

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; }
    .container { max-width: 600px; margin: 0 auto; }
    .header { background: #1a5276; color: white; padding: 20px; text-align: center; }
    .content { padding: 20px; }
    .student-info { background: #f8f9fa; padding: 15px; border-radius: 5px; }
    .cta-button {
      display: inline-block;
      padding: 12px 24px;
      background: #2ecc71;
      color: white;
      text-decoration: none;
      border-radius: 5px;
    }
    .footer { margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📋 Report Card Available</h1>
      <p>{School Name}</p>
    </div>
    <div class="content">
      <h2>Dear {Parent Name},</h2>
      <p>We are pleased to inform you that the report card for <strong>{Student Name}</strong>
      for <strong>{Term} - {Academic Year}</strong> is now available.</p>
      <div class="student-info">
        <p><strong>📊 Academic Summary:</strong></p>
        <ul>
          <li>📈 Average Score: {Average}%</li>
          <li>🏆 Overall Grade: {Grade}</li>
          <li>📚 Class Position: {Position}/{Total Students}</li>
        </ul>
      </div>
      <p>Please log in to the parent portal to view and download the complete report card.</p>
      <div style="text-align: center; margin: 30px 0;">
        <a href="{Portal_URL}" class="cta-button">📂 View Report Card</a>
      </div>
      <p>If you have any questions, please contact the school administration.</p>
      <p>Best regards,<br><strong>{School Name} Administration</strong></p>
    </div>
    <div class="footer">
      <p>This is an automated message. Please do not reply to this email.</p>
      <p>© {Year} {School Name} | All Rights Reserved</p>
    </div>
  </div>
</body>
</html>
```

Placeholders (`{Student Name}`, `{Parent Name}`, etc.) are filled from the
`Report Card` + `Student` + `Student Guardian` + `School Settings` records
at send time.

## 6.5 Failure Handling

Failed sends stay visible (not silently dropped): a per-guardian failure
is caught and logged via `frappe.log_error` (visible in the Desk Error
Log to Admin/System Manager) rather than crashing the whole batch or
silently swallowing it — verified with a real failure (no Email Account
configured) that logged correctly and left `sent_to_parent_at` unset.
**Not yet built:** a friendlier Headmaster-facing delivery report (vs.
digging through Error Log) — Sprint 8 polish candidate. Retry policy:
default to Frappe Email Queue's built-in retry behavior.

## 6.6 SMTP Setup (deployment-time TODO)

The pipeline is verified end-to-end (correct recipient, subject, body,
PDF attachment — confirmed by creating a placeholder `Email Account`,
triggering a send, inspecting the resulting `Email Queue` record, then
removing the placeholder). What's *not* done: pointing it at a real SMTP
provider. Before pilot-school go-live:

1. Create an `Email Account` in Frappe (Desk → Email Account) with real
   SMTP credentials, `enable_outgoing = 1`, `default_outgoing = 1`.
2. Do **not** commit credentials to `edupro_sms` or any doc — they live
   only in the site's database (or `frappe_docker/.env` for local dev,
   already gitignored).
3. Send a real test email (e.g. re-run `notify.send_report_card_emails`
   for one Report Card) and confirm actual delivery, not just queuing.
