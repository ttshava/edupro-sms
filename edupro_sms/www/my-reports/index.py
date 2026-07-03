import frappe


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
		fields=[
			"name",
			"student",
			"student_name",
			"student_group",
			"academic_term",
			"academic_year",
			"overall_grade",
			"average_percentage",
			"position",
			"number_of_students",
			"workflow_state",
		],
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
	context.title = "My Reports"


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

	courses = []
	if student_group and student_group.program:
		program = frappe.get_doc("Program", student_group.program)
		courses = [c.course for c in program.courses]

	guardian_emails = [
		frappe.db.get_value("Guardian", row.guardian, "email_address")
		for row in student.guardians
		if row.guardian
	]
	guardian_emails = [e for e in guardian_emails if e]

	return {
		"student": student.name,
		"student_name": student.student_name,
		"student_group": student_group.name if student_group else None,
		"program": student_group.program if student_group else None,
		"courses": courses,
		"guardian_emails": guardian_emails,
	}
