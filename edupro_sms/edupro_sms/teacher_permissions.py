"""Scope Instructor (teacher) access to Assessment Plan/Result down to
their own assigned classes AND subjects -- Education's stock permissions
grant this only to the broader "Academics User" role, with no per-class
scoping. Wired via hooks.py permission_query_conditions/has_permission.

Access is granted strictly per (class, subject) pair, sourced only from
Class Subject Assignment -- the precise, per-subject grant. Being a
class's Class Teacher, or teaching one subject in it, does NOT by itself
grant access to every OTHER subject in that class (e.g. Mrs Oyombo
teaching French in Form 1 Green must not be able to see or enter marks
for that class's Mathematics). The Class Teacher's whole-class report
review already has its own separate, correct access path -- a direct
Student Group.class_teacher check in report_card.py/class_review.py --
so it doesn't depend on this module at all."""

import frappe


def _instructor_for_user(user: str) -> str | None:
	return frappe.db.get_value("Instructor", {"user": user}, "name")


def _assigned_class_courses(instructor: str) -> list[tuple[str, str]]:
	rows = frappe.get_all(
		"Class Subject Assignment", filters={"instructor": instructor}, fields=["student_group", "course"]
	)
	return [(r.student_group, r.course) for r in rows]


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

		pairs = _assigned_class_courses(instructor)
		if not pairs:
			return "1=0"

		clauses = " or ".join(
			f"(`tab{doctype}`.student_group = {frappe.db.escape(group)}"
			f" and `tab{doctype}`.course = {frappe.db.escape(course)})"
			for group, course in pairs
		)
		return f"({clauses})"

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

	return (doc.student_group, doc.course) in _assigned_class_courses(instructor)


def assessment_plan_query_conditions(user: str | None = None) -> str:
	return get_permission_query_conditions_for_assessment("Assessment Plan")(user)


def assessment_plan_has_permission(doc, user: str | None = None, permission_type: str | None = None) -> bool:
	return has_permission_for_assessment(doc, user, permission_type)


def assessment_result_query_conditions(user: str | None = None) -> str:
	return get_permission_query_conditions_for_assessment("Assessment Result")(user)


def assessment_result_has_permission(doc, user: str | None = None, permission_type: str | None = None) -> bool:
	return has_permission_for_assessment(doc, user, permission_type)
