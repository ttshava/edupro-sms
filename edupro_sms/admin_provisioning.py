"""Headmaster-facing account provisioning -- create Student/Guardian/
Instructor logins and enroll students into classes, all in one call
instead of the multi-step Desk-only process this previously required.

Email delivery is disabled (see doctype/report_card/notify.py), so there
is no welcome email: every create_* function returns a freshly generated
temporary password that the portal shows once, for the Headmaster to
hand to the new user directly.
"""

import secrets
from contextlib import contextmanager

import frappe

from edupro_sms.approvals import _is_headmaster


def _require_headmaster():
	if not _is_headmaster():
		frappe.throw(frappe._("You are not permitted to manage accounts."), frappe.PermissionError)


@contextmanager
def _elevated():
	"""Education's Student.on_update() auto-creates an ERPNext Customer
	record via its own internal .insert() call that does NOT inherit our
	ignore_permissions=True -- it checks the real session user's
	permissions, and a Headmaster has no Customer create permission (this
	app deliberately doesn't use ERPNext Customer/Sales Invoice, see
	DECISIONS.md 0008). Can't touch core Education code, so we briefly
	elevate to Administrator for the insert instead -- safe here because
	_require_headmaster() has already authorized the caller above."""
	original_user = frappe.session.user
	frappe.set_user("Administrator")
	try:
		yield
	finally:
		frappe.set_user(original_user)


def _generate_temp_password() -> str:
	"""Meets Frappe's default password policy (upper+lower+digit+special)
	without relying on characters that are awkward to read/type aloud."""
	return f"Edu{secrets.randbelow(9000) + 1000}!"


def _create_user(email: str, first_name: str, role: str) -> str:
	if frappe.db.exists("User", email):
		frappe.throw(frappe._("A user with email {0} already exists.").format(email))

	password = _generate_temp_password()
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"send_welcome_email": 0,
			"user_type": "Website User",
			"roles": [{"role": role}],
		}
	)
	user.insert(ignore_permissions=True)
	frappe.utils.password.update_password(email, password)
	return password


@frappe.whitelist()
def create_student(
	student_name: str,
	student_email: str,
	gender: str | None = None,
	date_of_birth: str | None = None,
	boarding_type: str | None = None,
	student_group: str | None = None,
	existing_guardian: str | None = None,
	guardian_name: str | None = None,
	guardian_email: str | None = None,
	guardian_mobile: str | None = None,
	guardian_relation: str | None = None,
) -> dict:
	"""Create the Student's User + Student doc, link a Guardian (existing
	or new), and optionally enroll into a class -- one atomic action."""
	_require_headmaster()

	if not student_name or not student_email:
		frappe.throw(frappe._("Student name and email are required."))

	parts = student_name.strip().split(" ", 1)
	first_name, last_name = parts[0], (parts[1] if len(parts) > 1 else "")

	student_password = _create_user(student_email, first_name, "Student")

	student = frappe.get_doc(
		{
			"doctype": "Student",
			"first_name": first_name,
			"last_name": last_name,
			"student_email_id": student_email,
			"user": student_email,
			"gender": gender,
			"date_of_birth": date_of_birth,
			"boarding_type": boarding_type or "Day Boarder",
			"enabled": 1,
		}
	)

	guardian_password = None
	guardian = None
	if existing_guardian:
		guardian = existing_guardian
	elif guardian_name and guardian_email:
		if frappe.db.exists("Guardian", {"email_address": guardian_email}):
			guardian = frappe.db.get_value("Guardian", {"email_address": guardian_email}, "name")
		else:
			guardian_password = _create_user(guardian_email, guardian_name.split(" ")[0], "Guardian")
			guardian_doc = frappe.get_doc(
				{
					"doctype": "Guardian",
					"guardian_name": guardian_name,
					"email_address": guardian_email,
					"mobile_number": guardian_mobile,
					"user": guardian_email,
				}
			)
			guardian_doc.insert(ignore_permissions=True)
			guardian = guardian_doc.name

	if guardian:
		student.append("guardians", {"guardian": guardian, "relation": guardian_relation or "Others"})

	with _elevated():
		student.insert(ignore_permissions=True)

		if student_group:
			frappe.get_doc(
				{
					"doctype": "Student Group Student",
					"parenttype": "Student Group",
					"parent": student_group,
					"parentfield": "students",
					"student": student.name,
					"student_name": student.student_name,
					"active": 1,
				}
			).insert(ignore_permissions=True)

	frappe.db.commit()
	return {
		"student": student.name,
		"student_email": student_email,
		"student_password": student_password,
		"guardian": guardian,
		"guardian_email": guardian_email if guardian_password else None,
		"guardian_password": guardian_password,
	}


@frappe.whitelist()
def create_instructor(instructor_name: str, email: str) -> dict:
	"""Create the Instructor's User + Instructor doc."""
	_require_headmaster()

	if not instructor_name or not email:
		frappe.throw(frappe._("Instructor name and email are required."))

	password = _create_user(email, instructor_name.split(" ")[0], "Instructor")

	instructor = frappe.get_doc(
		{
			"doctype": "Instructor",
			"instructor_name": instructor_name,
			"user": email,
			"status": "Active",
		}
	)
	with _elevated():
		instructor.insert(ignore_permissions=True)
	frappe.db.commit()

	return {"instructor": instructor.name, "email": email, "password": password}


@frappe.whitelist()
def enroll_student(student: str, student_group: str) -> dict:
	"""Add a Student Group Student row -- refuses a duplicate active
	enrollment in the same class rather than creating a second row."""
	_require_headmaster()

	already_active = frappe.db.exists(
		"Student Group Student", {"parent": student_group, "student": student, "active": 1}
	)
	if already_active:
		frappe.throw(frappe._("This student is already enrolled in that class."))

	student_name = frappe.db.get_value("Student", student, "student_name")
	frappe.get_doc(
		{
			"doctype": "Student Group Student",
			"parenttype": "Student Group",
			"parent": student_group,
			"parentfield": "students",
			"student": student,
			"student_name": student_name,
			"active": 1,
		}
	).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"student": student, "student_group": student_group}


@frappe.whitelist()
def get_provisioning_reference_data() -> dict:
	"""Dropdown data for the admin portal form."""
	_require_headmaster()
	return {
		"student_groups": frappe.get_all("Student Group", filters={"disabled": 0}, fields=["name"], order_by="name asc"),
		"guardians": frappe.get_all(
			"Guardian",
			filters={"email_address": ["not like", "%example.edupro.test"]},
			fields=["name", "guardian_name"],
			order_by="guardian_name asc",
		),
	}
