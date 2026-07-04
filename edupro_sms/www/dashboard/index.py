from collections import Counter

import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/dashboard"
		raise frappe.Redirect

	context.no_cache = 1
	roles = set(frappe.get_roles())

	if "Headmaster" in roles or "System Manager" in roles:
		from edupro_sms.edupro_sms.approvals import get_pending_report_cards

		context.dashboard_role = "headmaster"
		context.summary = _headmaster_summary()
		context.pending_report_cards = get_pending_report_cards()
		context.csrf_token = frappe.sessions.get_csrf_token()
	elif "Instructor" in roles:
		context.dashboard_role = "teacher"
		context.classes = _teacher_classes()
	else:
		context.dashboard_role = None

	context.title = "Dashboard"


def _headmaster_summary():
	groups = frappe.get_all("Student Group", fields=["name", "program", "class_teacher"], order_by="name asc")

	class_rows = []
	for group in groups:
		student_count = frappe.db.count("Student Group Student", {"parent": group.name, "active": 1})
		class_teacher_name = None
		if group.class_teacher:
			class_teacher_name = frappe.db.get_value("Instructor", group.class_teacher, "instructor_name")
		class_rows.append(
			{
				"name": group.name,
				"program": group.program,
				"student_count": student_count,
				"class_teacher": class_teacher_name or "Not assigned",
			}
		)

	return {
		"total_students": frappe.db.count("Student", {"enabled": 1}),
		"total_instructors": frappe.db.count("Instructor"),
		"total_classes": len(groups),
		"classes": class_rows,
		"report_card_states": Counter(frappe.get_all("Report Card", pluck="workflow_state")),
	}


def _teacher_classes():
	# Reuse the My Classes report's row logic instead of duplicating it --
	# frappe.get_list inside it already scopes to the logged-in Instructor's
	# own classes via teacher_permissions.py, same as on the Desk report.
	from edupro_sms.edupro_sms.report.my_classes.my_classes import _rows

	return _rows()
