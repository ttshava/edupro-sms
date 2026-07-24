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
		from edupro_sms.grading import get_grade_boundaries

		context.dashboard_role = "teacher"
		context.classes = _teacher_classes()
		context.teacher_summary = _teacher_summary(context.classes)
		# A teacher can teach across more than one grading band (e.g. both an
		# O Level and an A Level class), so show boundaries for every scale
		# actually in use across their classes, not one hardcoded default.
		scales_in_use = sorted({row["grading_scale"] for row in context.classes if row.get("grading_scale")})
		context.grade_boundaries_by_scale = [
			{"scale": scale, "rows": get_grade_boundaries(scale)} for scale in scales_in_use
		]
		if "Class Teacher" in roles:
			context.class_teacher_of = _class_teacher_of()
			context.class_teacher_reviews = _class_teacher_reviews()
			context.csrf_token = frappe.sessions.get_csrf_token()
	else:
		context.dashboard_role = None

	context.title = "Dashboard"


def _teacher_summary(classes: list[dict]) -> dict:
	from edupro_sms.academic_calendar import get_current_term

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
	from edupro_sms.academic_calendar import get_current_term
	from edupro_sms.class_review import get_class_summary_rows, get_recent_activity, get_subject_analysis
	from edupro_sms.fees import get_class_fee_summary, get_school_fee_totals
	from edupro_sms.grading import DEFAULT_GRADING_SCALE, get_grade_for_percentage

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
	# Whole-school average spans every grading band, so there's no single
	# scale that's strictly "correct" here -- fall back to the default one
	# just to express the number as a letter grade too.
	overall_grade = get_grade_for_percentage(DEFAULT_GRADING_SCALE, overall_average)

	return {
		"academic_year": academic_year,
		"current_term": term,
		"total_students": total_students,
		"total_instructors": frappe.db.count("Instructor"),
		"total_classes": len(class_rows),
		"total_subjects": frappe.db.count("Course"),
		"fee_totals": get_school_fee_totals(),
		"class_fee_summary": get_class_fee_summary(),
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


def _class_teacher_of():
	"""Classes the logged-in Instructor is the Class Teacher of -- always
	shown regardless of pending reviews, distinct from the subject
	classes in _teacher_classes()/context.classes. A teacher can be the
	Class Teacher of a class without teaching any subject in it (or vice
	versa), so these two lists deliberately aren't merged."""
	instructor = frappe.db.get_value("Instructor", {"user": frappe.session.user}, "name")
	if not instructor:
		return []

	groups = frappe.get_all(
		"Student Group", filters={"class_teacher": instructor}, fields=["name", "program"], order_by="name asc"
	)
	for g in groups:
		g["student_count"] = frappe.db.count("Student Group Student", {"parent": g["name"], "active": 1})
	return groups


def _class_teacher_reviews():
	"""Report cards sitting in Pending Approval for classes where the
	logged-in Instructor is the Class Teacher -- their own "Review" step
	in the Report Card Approval workflow (see approvals.py), surfaced
	here since Desk access was removed for this role (DECISIONS.md 0014)."""
	from edupro_sms.academic_calendar import get_current_term

	instructor = frappe.db.get_value("Instructor", {"user": frappe.session.user}, "name")
	if not instructor:
		return []

	term = get_current_term()
	groups = frappe.get_all("Student Group", filters={"class_teacher": instructor}, pluck="name")

	rows = []
	for group in groups:
		pending = frappe.db.count(
			"Report Card",
			{"student_group": group, "academic_term": term, "workflow_state": "Pending Approval"},
		)
		if pending:
			rows.append({"student_group": group, "academic_term": term, "pending_count": pending})
	return rows


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
