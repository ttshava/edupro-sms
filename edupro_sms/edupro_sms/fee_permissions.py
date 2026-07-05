"""Scope Student Fee and Student Ledger Entry visibility to the owning
Student and their linked Guardians -- same shape as Report Card's own
permission scoping (edupro_sms/doctype/report_card/report_card.py),
since neither Education's stock Fees doctype nor ERPNext's Sales
Invoice ship with any Student/Guardian row-level scoping of their own
(see the fees research: Sales Invoice grants the Student role blanket
read+write across every invoice in the system out of the box).

Both fee doctypes share the exact same "student" field and the exact
same set of roles that should see everything (System Manager,
Headmaster, Bursar) vs. only their own (Student, Guardian), so one
factory drives both hooks.py entries instead of duplicating the logic
per doctype."""

import frappe

_UNRESTRICTED_ROLES = {"System Manager", "Headmaster", "Bursar"}


def _make_query_conditions(doctype: str):
	def _conditions(user: str | None = None) -> str:
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
				conditions.append(f"`tab{doctype}`.student = {frappe.db.escape(student)}")

		if "Guardian" in roles:
			guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
			if guardian:
				children = frappe.get_all(
					"Student Guardian", filters={"guardian": guardian, "parenttype": "Student"}, pluck="parent"
				)
				if children:
					child_list = ", ".join(frappe.db.escape(c) for c in children)
					conditions.append(f"`tab{doctype}`.student in ({child_list})")

		if not conditions:
			return "1=0"

		return "(" + " or ".join(conditions) + ")"

	return _conditions


def _make_has_permission():
	def _has_permission(doc, user: str | None = None, permission_type: str | None = None) -> bool:
		user = user or frappe.session.user
		if user == "Administrator":
			return True

		roles = set(frappe.get_roles(user))
		if roles & _UNRESTRICTED_ROLES:
			return True

		if "Student" in roles:
			student = frappe.db.get_value("Student", {"user": user}, "name")
			if student and doc.student == student:
				return True

		if "Guardian" in roles:
			guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
			if guardian and frappe.db.exists(
				"Student Guardian", {"guardian": guardian, "parent": doc.student, "parenttype": "Student"}
			):
				return True

		return False

	return _has_permission


get_permission_query_conditions = _make_query_conditions("Student Fee")
has_permission = _make_has_permission()

get_ledger_permission_query_conditions = _make_query_conditions("Student Ledger Entry")
has_ledger_permission = _make_has_permission()
