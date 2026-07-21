import frappe

from fees import BOARDING_FEE, get_student_fee_statement


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/bursar"
		raise frappe.Redirect

	roles = set(frappe.get_roles())
	if not (roles & {"Bursar", "Headmaster", "System Manager"}):
		frappe.throw("You are not permitted to view this page.", frappe.PermissionError)

	context.no_cache = 1
	context.boarding_types = list(BOARDING_FEE.keys())
	context.students = _students_with_statements()
	context.summary = _summary(context.students)
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = "Bursar"
	context.active_nav = "dashboard"


def _students_with_statements() -> list[dict]:
	students = frappe.get_all(
		"Student",
		filters={"enabled": 1, "student_email_id": ["not like", "%example.edupro.test"]},
		fields=["name", "student_name", "boarding_type"],
		order_by="student_name asc",
	)

	groups = {
		row.student: row.parent
		for row in frappe.get_all("Student Group Student", filters={"active": 1}, fields=["student", "parent"])
	}

	rows = []
	for s in students:
		statement = get_student_fee_statement(s.name)
		rows.append(
			{
				"student": s.name,
				"student_name": s.student_name,
				"student_group": groups.get(s.name) or "Unassigned",
				"boarding_type": s.boarding_type or "Day Boarder",
				"total_balance": statement["total_balance"],
				"terms": statement["terms"],
			}
		)
	return rows


def _summary(students: list[dict]) -> dict:
	total_billed = 0.0
	total_paid = 0.0
	total_balance = 0.0
	for s in students:
		for t in s["terms"]:
			if t["billed"]:
				total_billed += t["amount"]
				total_paid += t["amount_paid"]
		total_balance += s["total_balance"]

	return {
		"total_students": len(students),
		"total_billed": total_billed,
		"total_paid": total_paid,
		"total_balance": total_balance,
	}
