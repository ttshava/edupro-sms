"""Row-level scoping for the Student doctype -- stock DocPerm already
grants Student/Guardian roles read+print on Student (needed so a parent
can open /printview for the Fee Statement print format), but with no
scoping at all a Student/Guardian could open *any* other student's
record via a direct URL, not just their own/their children's. System
Manager, Headmaster, Instructor, Academics User and Bursar are
intentionally left unrestricted here -- unchanged from before this
module existed."""

import frappe

_UNRESTRICTED_ROLES = {"System Manager", "Headmaster", "Instructor", "Academics User", "Bursar"}


def get_permission_query_conditions(user: str | None = None) -> str:
	user = user or frappe.session.user
	if user == "Administrator":
		return ""

	roles = set(frappe.get_roles(user))
	if roles & _UNRESTRICTED_ROLES:
		return ""

	conditions = []

	if "Student" in roles:
		student = frappe.db.get_value("Student", {"user": user}, "name")
		if student:
			conditions.append(f"`tabStudent`.name = {frappe.db.escape(student)}")

	if "Guardian" in roles:
		guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
		if guardian:
			children = frappe.get_all(
				"Student Guardian", filters={"guardian": guardian, "parenttype": "Student"}, pluck="parent"
			)
			if children:
				child_list = ", ".join(frappe.db.escape(c) for c in children)
				conditions.append(f"`tabStudent`.name in ({child_list})")

	if not conditions:
		return "1=0"

	return "(" + " or ".join(conditions) + ")"


def has_permission(doc, user: str | None = None, permission_type: str | None = None) -> bool:
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	roles = set(frappe.get_roles(user))
	if roles & _UNRESTRICTED_ROLES:
		return True

	if "Student" in roles:
		student = frappe.db.get_value("Student", {"user": user}, "name")
		if student and doc.name == student:
			return True

	if "Guardian" in roles:
		guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
		if guardian and frappe.db.exists(
			"Student Guardian", {"guardian": guardian, "parent": doc.name, "parenttype": "Student"}
		):
			return True

	return False
