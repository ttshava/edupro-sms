"""Parent email delivery for Report Cards — docs/06_Email_System.md.

Triggered automatically when a Report Card reaches the Published workflow
state (see report_card.py `on_workflow_state_change`, wired via
hooks.py doc_events). Runs as a background job, never synchronously.
"""

import frappe
from frappe.utils import get_url, now_datetime
from frappe.utils.pdf import get_pdf

# Email delivery is on: the school's SMTP account (First Class High
# Outgoing, mail.firstclasshigh.ac.zw) is configured and verified working
# (see 2026-07-06 test send, Email Queue status "Sent").
EMAIL_DELIVERY_ENABLED = True

EMAIL_BODY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; }}
    .container {{ max-width: 600px; margin: 0 auto; }}
    .header {{ background: #1a5276; color: white; padding: 20px; text-align: center; }}
    .content {{ padding: 20px; }}
    .student-info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
    .cta-button {{
      display: inline-block;
      padding: 12px 24px;
      background: #2ecc71;
      color: white;
      text-decoration: none;
      border-radius: 5px;
    }}
    .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Report Card Available</h1>
      <p>{school_name}</p>
    </div>
    <div class="content">
      <h2>Dear {parent_name},</h2>
      <p>We are pleased to inform you that the report card for <strong>{student_name}</strong>
      for <strong>{term} - {academic_year}</strong> is now available.</p>
      <div class="student-info">
        <p><strong>Academic Summary:</strong></p>
        <ul>
          <li>Average Score: {average}%</li>
          <li>Overall Grade: {grade}</li>
          <li>Class Position: {position}/{total_students}</li>
        </ul>
      </div>
      <p>Please log in to the parent portal to view and download the complete report card.</p>
      <div style="text-align: center; margin: 30px 0;">
        <a href="{portal_url}" class="cta-button">View Report Card</a>
      </div>
      <p>If you have any questions, please contact the school administration.</p>
      <p>Best regards,<br><strong>{school_name} Administration</strong></p>
    </div>
    <div class="footer">
      <p>This is an automated message. Please do not reply to this email.</p>
      <p>&copy; {year} {school_name} | All Rights Reserved</p>
    </div>
  </div>
</body>
</html>
"""


@frappe.whitelist()
def resend_report_card_email(report_card_name: str):
	"""Manual "Email to Parent" action from the portal -- reuses the same
	background job the Published workflow transition already enqueues,
	gated by the same permission check Report Card itself uses."""
	from doctype.report_card.report_card import has_permission

	if not EMAIL_DELIVERY_ENABLED:
		frappe.throw(frappe._("Email delivery is currently disabled."))

	doc = frappe.get_doc("Report Card", report_card_name)
	if not has_permission(doc):
		frappe.throw(frappe._("Not permitted."), frappe.PermissionError)
	if doc.workflow_state != "Published":
		frappe.throw(frappe._("This report card hasn't been published yet."))

	frappe.enqueue(
		"edupro_sms.edupro_sms.doctype.report_card.notify.send_report_card_emails",
		queue="short",
		report_card_name=doc.name,
	)
	return {"queued": True}


def send_report_card_emails(report_card_name: str):
	"""Background job: email every guardian linked to this Report Card's
	student. Enqueued from report_card.py, never called synchronously
	from a request."""
	if not EMAIL_DELIVERY_ENABLED:
		return

	doc = frappe.get_doc("Report Card", report_card_name)
	if doc.workflow_state != "Published":
		return

	student = frappe.get_doc("Student", doc.student)
	guardians = [
		frappe.get_doc("Guardian", row.guardian) for row in student.guardians if row.guardian
	]
	recipients_with_email = [g for g in guardians if g.email_address]

	if not recipients_with_email:
		frappe.log_error(
			title="Report Card email: no guardian email",
			message=f"{report_card_name}: no linked guardian has an email address.",
		)
		return

	pdf_bytes = _get_or_generate_pdf(doc)
	school_name = frappe.db.get_single_value("School Settings", "school_name") or "Edupro School"

	sent_count = 0
	for guardian in recipients_with_email:
		try:
			_send_one(doc, student, guardian, school_name, pdf_bytes)
			sent_count += 1
		except Exception:
			frappe.log_error(
				title="Report Card email failed",
				message=f"{report_card_name} -> {guardian.email_address}\n{frappe.get_traceback()}",
			)

	if sent_count:
		frappe.db.set_value("Report Card", report_card_name, "sent_to_parent_at", now_datetime())
		frappe.db.commit()


def _get_or_generate_pdf(doc) -> bytes:
	if doc.pdf:
		file_doc = frappe.get_doc("File", {"file_url": doc.pdf})
		return file_doc.get_content()

	html = frappe.get_print("Report Card", doc.name, "IGCSE Report Card")
	pdf_bytes = get_pdf(html)

	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"{doc.name}.pdf",
			"attached_to_doctype": "Report Card",
			"attached_to_name": doc.name,
			"content": pdf_bytes,
			"is_private": 1,
		}
	)
	file_doc.insert(ignore_permissions=True)
	frappe.db.set_value("Report Card", doc.name, "pdf", file_doc.file_url)
	return pdf_bytes


def _send_one(doc, student, guardian, school_name: str, pdf_bytes: bytes):
	subject = f"Report Card - {doc.student_name} - {doc.academic_term}, {doc.academic_year}"
	body = EMAIL_BODY_TEMPLATE.format(
		school_name=school_name,
		parent_name=guardian.guardian_name,
		student_name=doc.student_name,
		term=doc.academic_term,
		academic_year=doc.academic_year,
		average=f"{doc.average_percentage:.1f}" if doc.average_percentage else "-",
		grade=doc.overall_grade or "-",
		position=doc.position,
		total_students=doc.number_of_students,
		portal_url=get_url("/my-reports"),
		year=now_datetime().year,
	)

	frappe.sendmail(
		recipients=[guardian.email_address],
		subject=subject,
		message=body,
		attachments=[{"fname": f"{doc.student_name} - {doc.academic_term}.pdf", "fcontent": pdf_bytes}],
		reference_doctype="Report Card",
		reference_name=doc.name,
	)
