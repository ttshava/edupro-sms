"""Scope Instructor (teacher) access to Assessment Plan/Result down to
their own assigned classes+subjects — Education's stock permissions
grant this only to the broader "Academics User" role, with no per-class
scoping. Wired via hooks.py permission_query_conditions/has_permission.
"""

import frappe


def _instructor_for_user(user: str) -> str | None:
	return frappe.db.get_value("Instructor", {"user": user}, "name")


def _assigned_student_groups(instructor: str) -> list[str]:
	return frappe.get_all(
		"Student Group Instructor", filters={"instructor": instructor}, pluck="parent"
	)


def get_permission_query_conditions_for_assessment(doctype: str):
	def _conditions(user: str | None = None) -> str:
		user = user or frappe.session.user
		if user == "Administrator":
			return ""

		roles = set(frappe.get_roles(user))
		if "System Manager" in roles or "Headmaster" in roles or "Academics User" in roles:
			return ""

		if "Instructor" not in roles:
			return "1=0"

		instructor = _instructor_for_user(user)
		if not instructor:
			return "1=0"

		groups = _assigned_student_groups(instructor)
		if not groups:
			return "1=0"

		group_list = ", ".join(frappe.db.escape(g) for g in groups)
		return f"`tab{doctype}`.student_group in ({group_list})"

	return _conditions


def has_permission_for_assessment(doc, user: str | None = None, permission_type: str | None = None) -> bool:
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	roles = set(frappe.get_roles(user))
	if "System Manager" in roles or "Headmaster" in roles or "Academics User" in roles:
		return True

	if "Instructor" not in roles:
		return False

	instructor = _instructor_for_user(user)
	if not instructor:
		return False

	return doc.student_group in _assigned_student_groups(instructor)


def assessment_plan_query_conditions(user: str | None = None) -> str:
	return get_permission_query_conditions_for_assessment("Assessment Plan")(user)


def assessment_plan_has_permission(doc, user: str | None = None, permission_type: str | None = None) -> bool:
	return has_permission_for_assessment(doc, user, permission_type)


def assessment_result_query_conditions(user: str | None = None) -> str:
	return get_permission_query_conditions_for_assessment("Assessment Result")(user)


def assessment_result_has_permission(doc, user: str | None = None, permission_type: str | None = None) -> bool:
	return has_permission_for_assessment(doc, user, permission_type)
