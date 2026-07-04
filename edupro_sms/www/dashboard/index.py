from collections import Counter

import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/dashboard"
		raise frappe.Redirect

	context.no_cache = 1
	roles = set(frappe.get_roles())

	if "Headmaster" in roles or "System Manager" in roles:
		context.dashboard_role = "headmaster"
		context.summary = _headmaster_summary()
		context.csrf_token = frappe.sessions.get_csrf_token()
	elif "Instructor" in roles:
		from edupro_sms.edupro_sms.grading import get_grade_boundaries

		context.dashboard_role = "teacher"
		context.classes = _teacher_classes()
		context.teacher_summary = _teacher_summary(context.classes)
		context.grade_boundaries = get_grade_boundaries()
	else:
		context.dashboard_role = None

	context.title = "Dashboard"


def _teacher_summary(classes: list[dict]) -> dict:
	from edupro_sms.edupro_sms.academic_calendar import get_current_term

	term = get_current_term()
	academic_year = frappe.db.get_value("Academic Term", term, "academic_year") if term else None

	assigned_subjects = {row["course"] for row in classes}
	assigned_groups = {row["student_group"] for row in classes}
	total_students = sum(
		frappe.db.count("Student Group Student", {"parent": group, "active": 1}) for group in assigned_groups
	)
	marks_entered = sum(row["marks_entered"] for row in classes)
	marks_expected = sum(row["total_students"] for row in classes)

	return {
		"academic_year": academic_year,
		"current_term": term,
		"assigned_subjects": len(assigned_subjects),
		"total_students": total_students,
		"marks_entered": marks_entered,
		"marks_expected": marks_expected,
		"marks_pending": marks_expected - marks_entered,
	}


def _headmaster_summary():
	from education.education.api import get_grade

	from edupro_sms.edupro_sms.academic_calendar import get_current_term
	from edupro_sms.edupro_sms.class_review import get_class_summary_rows, get_recent_activity, get_subject_analysis

	term = get_current_term()
	academic_year = frappe.db.get_value("Academic Term", term, "academic_year") if term else None

	class_rows = get_class_summary_rows(term)
	total_students = frappe.db.count("Student", {"enabled": 1})

	states = Counter(
		frappe.get_all(
			"Report Card", filters={"academic_term": term, "docstatus": ["!=", 2]}, pluck="workflow_state"
		)
	)
	reports_published = states.get("Published", 0)
	reports_pending_approval = sum(v for k, v in states.items() if k != "Published")
	reports_approved = states.get("Approved", 0)

	averages = [r["average_percentage"] for r in class_rows if r["average_percentage"] is not None]
	overall_average = (sum(averages) / len(averages)) if averages else None
	overall_grade = get_grade("IGCSE Standard", overall_average) if overall_average is not None else None

	return {
		"academic_year": academic_year,
		"current_term": term,
		"total_students": total_students,
		"total_instructors": frappe.db.count("Instructor"),
		"total_classes": len(class_rows),
		"classes": class_rows,
		"report_card_states": states,
		"reports_published": reports_published,
		"reports_expected": total_students,
		"reports_pending_approval": reports_pending_approval,
		"reports_approved": reports_approved,
		"overall_average": overall_average,
		"overall_grade": overall_grade,
		"subject_analysis": get_subject_analysis(term),
		"recent_activity": get_recent_activity(),
	}


def _teacher_classes():
	# Reuse the My Classes report's row logic instead of duplicating it --
	# frappe.get_list inside it already scopes to the logged-in Instructor's
	# own classes via teacher_permissions.py, same as on the Desk report.
	from edupro_sms.edupro_sms.report.my_classes.my_classes import _rows

	rows = _rows()
	for row in rows:
		# The subject/class selector on the dashboard serializes this list
		# with Jinja's |tojson, which can't handle a raw date object.
		if row.get("schedule_date"):
			row["schedule_date"] = str(row["schedule_date"])
	return rows
