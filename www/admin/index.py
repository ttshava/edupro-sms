import frappe


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/admin"
		raise frappe.Redirect

	roles = set(frappe.get_roles())
	if not (roles & {"Headmaster", "System Manager"}):
		frappe.throw("You are not permitted to view this page.", frappe.PermissionError)

	context.no_cache = 1
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = "Admin"
	context.genders = frappe.get_all("Gender", pluck="name")
	context.student_groups = frappe.get_all(
		"Student Group", filters={"disabled": 0}, fields=["name"], order_by="name asc"
	)
	context.guardians = frappe.get_all(
		"Guardian",
		filters={"email_address": ["not like", "%example.edupro.test"]},
		fields=["name", "guardian_name"],
		order_by="guardian_name asc",
	)
	context.students = frappe.get_all(
		"Student",
		filters={"enabled": 1, "student_email_id": ["not like", "%example.edupro.test"]},
		fields=["name", "student_name"],
		order_by="student_name asc",
	)
	context.courses = frappe.get_all("Course", fields=["name"], order_by="name asc")
	context.instructors = frappe.get_all(
		"Instructor", fields=["name", "instructor_name"], order_by="instructor_name asc"
	)
	context.academic_years = frappe.get_all("Academic Year", fields=["name"], order_by="name desc")
