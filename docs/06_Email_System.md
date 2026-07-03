# 06 — Email System

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

Failed sends stay visible (not silently dropped) — surface in a Headmaster/
Admin-facing report so undelivered report cards can be resent manually.
Retry policy: TBD at implementation, default to Frappe Email Queue's
built-in retry behavior unless it proves insufficient.
