import frappe
from frappe.utils import now_datetime

from edupro_sms.edupro_sms.academic_calendar import get_current_term


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/my-reports"
		raise frappe.Redirect

	context.no_cache = 1

	roles = set(frappe.get_roles())
	context.viewer_role = "guardian" if "Guardian" in roles else "student" if "Student" in roles else None

	profile_students = _get_profile_students(context.viewer_role)

	cards = frappe.get_list(
		"Report Card",
		fields=["name", "student", "student_name", "academic_term", "workflow_state"],
		order_by="academic_term desc",
	)
	reports_by_student = {}
	for card in cards:
		reports_by_student.setdefault(card.student, []).append(card)

	# Show every student the viewer can see (same roster as the Profile
	# tab), not just the ones with a Report Card so far -- a child with no
	# report published yet used to disappear from this tab entirely
	# instead of showing a "not published yet" state.
	context.children = [
		{"student_name": p["student_name"], "reports": reports_by_student.get(p["student"], [])}
		for p in profile_students
	]
	context.profile_students = profile_students
	context.overview = _build_overview(profile_students)
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = "My Reports"


def _build_overview(profile_students: list[dict]) -> dict:
	term = get_current_term()
	academic_year = frappe.db.get_value("Academic Term", term, "academic_year") if term else None

	published = [p["latest_report"] for p in profile_students if p["latest_report"]]
	new_reports = [r for r in published if not r["viewed_by_parent_at"]]

	# Loading the overview counts as "seeing" any report shown on it --
	# the "New" badge is meant to behave like a notification indicator
	# that clears once opened, not a permanent unread marker.
	if new_reports:
		frappe.db.set_value(
			"Report Card",
			{"name": ["in", [r["name"] for r in new_reports]]},
			"viewed_by_parent_at",
			now_datetime(),
		)

	return {
		"academic_year": academic_year,
		"current_term": term,
		"children_count": len(profile_students),
		"reports_available": len(published),
		"new_reports": len(new_reports),
	}


def _get_profile_students(viewer_role):
	"""Profile info (class, subjects, guardian emails) for whichever
	students the current viewer has permission to see -- themselves, for
	a Student; their linked children, for a Guardian."""
	student_names = []

	if viewer_role == "student":
		student = frappe.db.get_value("Student", {"user": frappe.session.user}, "name")
		if student:
			student_names = [student]
	elif viewer_role == "guardian":
		guardian = frappe.db.get_value("Guardian", {"user": frappe.session.user}, "name")
		if guardian:
			student_names = frappe.get_all(
				"Student Guardian",
				filters={"guardian": guardian, "parenttype": "Student"},
				pluck="parent",
			)

	profiles = []
	for student_name in student_names:
		profiles.append(_build_profile(student_name))
	return profiles


def _build_profile(student_name):
	student = frappe.get_doc("Student", student_name)

	group_row = frappe.db.get_value(
		"Student Group Student", {"student": student_name, "active": 1}, "parent"
	)
	student_group = frappe.get_doc("Student Group", group_row) if group_row else None

	subjects = []
	class_teacher_name = None
	class_teacher_email = None
	if student_group:
		if student_group.class_teacher:
			class_teacher_name = frappe.db.get_value("Instructor", student_group.class_teacher, "instructor_name")
			class_teacher_email = frappe.db.get_value("Instructor", student_group.class_teacher, "user")
		if student_group.program:
			program = frappe.get_doc("Program", student_group.program)
			course_names = [c.course for c in program.courses]
			teacher_by_course = _latest_examiner_by_course(student_group.name, course_names)
			subjects = [
				{"course": course, "teacher": teacher_by_course.get(course) or "Not yet assigned"}
				for course in course_names
			]

	guardian_emails = [
		frappe.db.get_value("Guardian", row.guardian, "email_address")
		for row in student.guardians
		if row.guardian
	]
	guardian_emails = [e for e in guardian_emails if e]

	history = _report_history(student_name)

	return {
		"student": student.name,
		"student_name": student.student_name,
		"enabled": student.enabled,
		"student_group": student_group.name if student_group else None,
		"program": student_group.program if student_group else None,
		"class_teacher": class_teacher_name or "Not yet assigned",
		"class_teacher_email": class_teacher_email,
		"subjects": subjects,
		"guardian_emails": guardian_emails,
		"report_history": history,
		"latest_report": history[-1] if history else None,
		"has_history": len(history) >= 2,
	}


def _report_history(student_name):
	"""Every Published Report Card for this student, oldest first, each
	with its subject-level breakdown attached -- used for both the
	current Academic Summary (last entry) and the progress-over-terms
	panel (the full list). Currently only ever one entry long in real
	data (only Term 2 2026 has been run school-wide) -- callers must
	handle a single-entry or empty history gracefully, not assume a
	trend exists."""
	cards = frappe.get_all(
		"Report Card",
		filters={"student": student_name, "workflow_state": "Published"},
		fields=[
			"name",
			"academic_term",
			"academic_year",
			"total_score",
			"maximum_score",
			"average_percentage",
			"overall_grade",
			"position",
			"number_of_students",
			"viewed_by_parent_at",
			"sent_to_parent_at",
		],
	)

	term_starts = {
		t.name: t.term_start_date for t in frappe.get_all("Academic Term", fields=["name", "term_start_date"])
	}
	cards.sort(key=lambda c: term_starts.get(c.academic_term) or frappe.utils.getdate("1900-01-01"))

	for card in cards:
		card["subjects"] = frappe.get_all(
			"Report Card Assessment Result",
			filters={"parent": card.name},
			fields=["course", "total_score", "maximum_score", "grade", "comment"],
			order_by="course asc",
		)
		card["star_rating"] = _star_rating(card["overall_grade"])
	return cards


def _star_rating(grade: str | None) -> int:
	if not grade:
		return 0
	return {"A*": 5, "A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "F": 1}.get(grade, 0)


def _latest_examiner_by_course(student_group, course_names):
	"""Best-known teacher per subject for this class: the examiner set on
	that subject's most recent Assessment Plan, since that's the one real,
	persisted subject-to-teacher link in the data model (Student Group
	Instructor only lists the class's teachers as a flat pool, not which
	subject each one teaches)."""
	if not course_names:
		return {}

	plans = frappe.get_all(
		"Assessment Plan",
		filters={"student_group": student_group, "course": ["in", course_names], "examiner": ["is", "set"]},
		fields=["course", "examiner", "creation"],
		order_by="creation desc",
	)
	result = {}
	for plan in plans:
		result.setdefault(plan.course, frappe.db.get_value("Instructor", plan.examiner, "instructor_name"))
	return result
