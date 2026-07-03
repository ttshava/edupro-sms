import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/my-reports"
		raise frappe.Redirect

	context.no_cache = 1

	roles = set(frappe.get_roles())
	context.viewer_role = "guardian" if "Guardian" in roles else "student" if "Student" in roles else None

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
		order_by="student_name asc, academic_term desc",
	)

	# Group by student so a Guardian with multiple children gets a clear
	# per-child breakdown rather than one flat list.
	by_student = {}
	for card in cards:
		by_student.setdefault(card.student, {"student_name": card.student_name, "reports": []})
		by_student[card.student]["reports"].append(card)

	context.children = list(by_student.values())
	context.title = "My Reports"
