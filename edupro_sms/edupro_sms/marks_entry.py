"""Website marks entry for Instructors -- lets a teacher record or
correct marks for their own class/subject without needing Desk.
Reuses Assessment Result's own Document.validate() (max score check,
grade calculation, duplicate check) instead of reimplementing it; only
adds the amend dance a submitted doc requires for "editing" a mark
already on record.
"""

import json

import frappe
from education.education.api import get_assessment_details
from frappe import _
from frappe.utils import flt

from edupro_sms.edupro_sms.teacher_permissions import _assigned_student_groups, _instructor_for_user


def _can_access_plan(plan, user=None) -> bool:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if "System Manager" in roles or "Headmaster" in roles or "Academics User" in roles:
		return True
	if "Instructor" not in roles:
		return False
	instructor = _instructor_for_user(user)
	if not instructor:
		return False
	return plan.student_group in _assigned_student_groups(instructor)


def _class_students(student_group):
	return frappe.get_all(
		"Student Group Student",
		filters={"parent": student_group, "active": 1},
		fields=["student", "student_name"],
		order_by="student_name asc",
	)


@frappe.whitelist()
def get_entry_data(assessment_plan):
	from edupro_sms.edupro_sms.grading import get_grade_boundaries

	plan = frappe.get_doc("Assessment Plan", assessment_plan)
	if not _can_access_plan(plan):
		frappe.throw(_("You are not permitted to enter marks for this class."), frappe.PermissionError)

	criteria = get_assessment_details(assessment_plan)
	students = _class_students(plan.student_group)

	existing = frappe.get_all(
		"Assessment Result",
		filters={"assessment_plan": assessment_plan, "docstatus": ["!=", 2]},
		fields=["name", "student", "docstatus"],
	)
	existing_by_student = {e.student: e for e in existing}

	rows = []
	entered_count = 0
	for s in students:
		result = existing_by_student.get(s.student)
		scores = {}
		if result:
			details = frappe.get_all(
				"Assessment Result Detail",
				filters={"parent": result.name},
				fields=["assessment_criteria", "score"],
			)
			scores = {d.assessment_criteria: d.score for d in details}
		if result and result.docstatus == 1:
			entered_count += 1
		rows.append(
			{
				"student": s.student,
				"student_name": s.student_name,
				"existing_docstatus": result.docstatus if result else None,
				"scores": scores,
			}
		)

	return {
		"plan": {
			"name": plan.name,
			"course": plan.course,
			"student_group": plan.student_group,
			"academic_term": plan.academic_term,
			"schedule_date": str(plan.schedule_date) if plan.schedule_date else None,
			"entered_count": entered_count,
			"total_count": len(rows),
			"status": "Complete" if rows and entered_count >= len(rows) else "In Progress",
		},
		"criteria": criteria,
		"rows": rows,
		"grade_boundaries": get_grade_boundaries(),
	}


@frappe.whitelist()
def save_marks(assessment_plan, entries):
	if isinstance(entries, str):
		entries = json.loads(entries)

	plan = frappe.get_doc("Assessment Plan", assessment_plan)
	if not _can_access_plan(plan):
		frappe.throw(_("You are not permitted to enter marks for this class."), frappe.PermissionError)

	valid_criteria = {c.assessment_criteria for c in get_assessment_details(assessment_plan)}
	valid_students = {s.student for s in _class_students(plan.student_group)}

	saved = 0
	for entry in entries:
		student = entry.get("student")
		if student not in valid_students:
			frappe.throw(_("Student {0} is not in this class.").format(student))

		scores = entry.get("scores") or {}
		details = [
			{"assessment_criteria": crit, "score": flt(scores.get(crit))}
			for crit in valid_criteria
			if str(scores.get(crit) or "").strip() != ""
		]
		if not details:
			continue

		existing_name = frappe.db.get_value(
			"Assessment Result",
			{"assessment_plan": assessment_plan, "student": student, "docstatus": ["!=", 2]},
			"name",
		)

		if existing_name:
			existing_scores = {
				d.assessment_criteria: flt(d.score)
				for d in frappe.get_all(
					"Assessment Result Detail",
					filters={"parent": existing_name},
					fields=["assessment_criteria", "score"],
				)
			}
			new_scores = {d["assessment_criteria"]: flt(d["score"]) for d in details}
			if existing_scores == new_scores:
				continue

			existing_doc = frappe.get_doc("Assessment Result", existing_name)
			if existing_doc.docstatus == 1:
				existing_doc.flags.ignore_permissions = True
				existing_doc.cancel()
				doc = frappe.copy_doc(existing_doc)
				doc.amended_from = existing_doc.name
			else:
				doc = existing_doc
			doc.set("details", [])
			for d in details:
				doc.append("details", d)
		else:
			doc = frappe.new_doc("Assessment Result")
			doc.assessment_plan = assessment_plan
			doc.student = student
			for d in details:
				doc.append("details", d)

		doc.flags.ignore_permissions = True
		doc.save()
		doc.submit()
		saved += 1

	frappe.db.commit()
	return {"saved": saved}
