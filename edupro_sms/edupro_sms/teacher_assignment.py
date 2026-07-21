"""Headmaster-facing teacher assignment -- who is the Class Teacher of a
class, and who teaches which subject to which class. The latter didn't
have a real single source of truth before: it was implicit in whichever
Instructor happened to be set as `examiner` on each term's Assessment
Plan, which meant nothing enforced it and a new term's plans had no
default until someone remembered to set it by hand. Class Subject
Assignment is that source of truth now; Assessment Plan.examiner
defaults from it (see doc_events hook in hooks.py) and teacher
permission-scoping in teacher_permissions.py additionally grants access
based on it.

This is deliberately additive, not a replacement: a teacher already
listed in a class's general Instructor list (Student Group Instructor)
keeps the access they already have. Class Subject Assignment is the
precise, per-subject grant going forward.
"""

import frappe

from edupro_sms.edupro_sms.approvals import _is_headmaster


def _require_headmaster():
	if not _is_headmaster():
		frappe.throw(frappe._("You are not permitted to manage teacher assignments."), frappe.PermissionError)


@frappe.whitelist()
def assign_class_teacher(student_group: str, instructor: str) -> dict:
	_require_headmaster()
	frappe.db.set_value("Student Group", student_group, "class_teacher", instructor)

	# approvals._is_class_teacher_of() requires the "Class Teacher" role on
	# top of this Link match -- without it, the class-review page, report
	# card comments, and batch report generation all refuse the very
	# person this call just designated as class teacher.
	user = frappe.db.get_value("Instructor", instructor, "user")
	if user and not frappe.db.exists("Has Role", {"parent": user, "role": "Class Teacher"}):
		user_doc = frappe.get_doc("User", user)
		user_doc.append("roles", {"role": "Class Teacher"})
		user_doc.save(ignore_permissions=True)

	frappe.db.commit()
	return {"student_group": student_group, "class_teacher": instructor}


@frappe.whitelist()
def assign_subject_teacher(student_group: str, course: str, instructor: str, academic_year: str) -> dict:
	"""Upsert -- a class only ever has one teacher per subject per year,
	so re-assigning updates the existing row instead of creating a
	second, conflicting one."""
	_require_headmaster()

	existing = frappe.db.get_value(
		"Class Subject Assignment",
		{"student_group": student_group, "course": course, "academic_year": academic_year},
		"name",
	)
	if existing:
		existing_doc = frappe.get_doc("Class Subject Assignment", existing)
		existing_doc.instructor = instructor
		existing_doc.save(ignore_permissions=True)
		name = existing
	else:
		doc = frappe.get_doc(
			{
				"doctype": "Class Subject Assignment",
				"student_group": student_group,
				"course": course,
				"academic_year": academic_year,
				"instructor": instructor,
			}
		)
		doc.insert(ignore_permissions=True)
		name = doc.name

	frappe.db.commit()
	return {"name": name, "student_group": student_group, "course": course, "instructor": instructor}


@frappe.whitelist()
def get_teacher_assignment_reference_data() -> dict:
	_require_headmaster()
	return {
		"student_groups": frappe.get_all(
			"Student Group", filters={"disabled": 0}, fields=["name", "class_teacher"], order_by="name asc"
		),
		"courses": frappe.get_all("Course", fields=["name"], order_by="name asc"),
		"instructors": frappe.get_all(
			"Instructor",
			fields=["name", "instructor_name"],
			order_by="instructor_name asc",
		),
		"academic_years": frappe.get_all("Academic Year", fields=["name"], order_by="name desc"),
	}


@frappe.whitelist()
def get_class_subject_assignments(student_group: str) -> list[dict]:
	_require_headmaster()
	return frappe.get_all(
		"Class Subject Assignment",
		filters={"student_group": student_group},
		fields=["name", "course", "instructor", "instructor_name", "academic_year"],
		order_by="course asc",
	)


def default_examiner_from_assignment(doc, method=None):
	"""Assessment Plan doc_event (before_insert) -- see hooks.py. Never
	overrides an examiner someone already picked; only fills the gap."""
	if doc.examiner or not (doc.student_group and doc.course and doc.academic_year):
		return

	instructor = frappe.db.get_value(
		"Class Subject Assignment",
		{"student_group": doc.student_group, "course": doc.course, "academic_year": doc.academic_year},
		"instructor",
	)
	if instructor:
		doc.examiner = instructor
