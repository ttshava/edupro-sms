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

from edupro_sms.teacher_permissions import has_permission_for_assessment


def _can_access_plan(plan, user=None) -> bool:
	return has_permission_for_assessment(plan, user)


def _class_students(student_group, course=None):
	"""Every active student in the class -- unless a course is given, in
	which case only students actually enrolled in that specific subject
	(required subjects still cover the whole class, since every student's
	Program Enrollment gets those added automatically; an elective like
	Computer Science only lists the students who picked it, not the
	classmates who picked a different elective instead)."""
	students = frappe.get_all(
		"Student Group Student",
		filters={"parent": student_group, "active": 1},
		fields=["student", "student_name"],
		order_by="student_name asc",
	)
	if not course or not students:
		return students

	program = frappe.db.get_value("Student Group", student_group, "program")
	if not program:
		return students

	enrollments = frappe.get_all(
		"Program Enrollment",
		filters={"student": ["in", [s.student for s in students]], "program": program},
		fields=["name", "student"],
	)
	if not enrollments:
		return students

	enrollment_student = {e.name: e.student for e in enrollments}
	enrolled_in_course = frappe.get_all(
		"Program Enrollment Course",
		filters={"parent": ["in", list(enrollment_student)], "course": course},
		pluck="parent",
	)
	students_with_course = {enrollment_student[e] for e in enrolled_in_course}
	# A student with no enrollment row at all can't be confirmed either
	# way -- default to including them rather than silently hiding them
	# from marks entry over a data gap.
	no_enrollment = {s.student for s in students} - set(enrollment_student.values())

	return [s for s in students if s.student in students_with_course or s.student in no_enrollment]


@frappe.whitelist()
def get_entry_data(assessment_plan):
	from edupro_sms.grading import get_grade_boundaries

	plan = frappe.get_doc("Assessment Plan", assessment_plan)
	if not _can_access_plan(plan):
		frappe.throw(_("You are not permitted to enter marks for this class."), frappe.PermissionError)

	criteria = get_assessment_details(assessment_plan)
	students = _class_students(plan.student_group, plan.course)

	existing = frappe.get_all(
		"Assessment Result",
		filters={"assessment_plan": assessment_plan, "docstatus": ["!=", 2]},
		fields=["name", "student", "docstatus", "comment"],
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
				"comment": (result.comment if result else "") or "",
			}
		)

	return {
		"plan": {
			"name": plan.name,
			"course": plan.course,
			"student_group": plan.student_group,
			"academic_term": plan.academic_term,
			"schedule_date": str(plan.schedule_date) if plan.schedule_date else None,
			"grading_scale": plan.grading_scale,
			"entered_count": entered_count,
			"total_count": len(rows),
			"status": "Complete" if rows and entered_count >= len(rows) else "In Progress",
		},
		"criteria": criteria,
		"rows": rows,
		"grade_boundaries": get_grade_boundaries(plan.grading_scale),
	}


@frappe.whitelist()
def save_marks(assessment_plan, entries):
	if isinstance(entries, str):
		entries = json.loads(entries)

	plan = frappe.get_doc("Assessment Plan", assessment_plan)
	if not _can_access_plan(plan):
		frappe.throw(_("You are not permitted to enter marks for this class."), frappe.PermissionError)

	valid_criteria = {c.assessment_criteria for c in get_assessment_details(assessment_plan)}
	valid_students = {s.student for s in _class_students(plan.student_group, plan.course)}

	saved = 0
	for entry in entries:
		student = entry.get("student")
		if student not in valid_students:
			frappe.throw(_("Student {0} is not in this class.").format(student))

		scores = entry.get("scores") or {}
		new_comment = (entry.get("comment") or "").strip()
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
			existing_doc = frappe.get_doc("Assessment Result", existing_name)
			existing_comment = existing_doc.comment or ""
			if existing_scores == new_scores and existing_comment == new_comment:
				continue

			if existing_scores == new_scores:
				# Comment-only edit: skip the cancel/amend dance entirely.
				# Once a Report Card has been generated, cancelling this
				# Assessment Result to amend it fails with LinkExistsError
				# (Frappe won't cancel a submitted doc that's linked from
				# another submitted doc) -- but comment isn't a submittable
				# grading field, so writing it directly is safe and doesn't
				# need to touch docstatus at all.
				frappe.db.set_value("Assessment Result", existing_name, "comment", new_comment)
				saved += 1
				continue

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

		doc.comment = new_comment
		doc.flags.ignore_permissions = True
		doc.save()
		if not new_comment:
			# Teacher left the remark blank -- fall back to the grade
			# band's own description (e.g. "Very good" for a B) instead
			# of leaving it empty. Still just a starting point: they can
			# overwrite it any time via the comment-only edit path above.
			from edupro_sms.grading import get_grade_description

			auto_comment = get_grade_description(doc.grading_scale, doc.grade)
			if auto_comment:
				doc.comment = auto_comment
		doc.submit()
		saved += 1

		# The moment this student's last required subject is submitted,
		# their Report Card should exist for Class Teacher review with no
		# separate "generate reports" step -- there's no such button
		# anywhere in the product (see docs/04_Workflows.md 4.2), so this
		# is the only trigger point. Runs as Administrator since it's a
		# system side effect, not something the teacher is themselves
		# permitted/expected to do; never allowed to break the teacher's
		# actual mark submission above, which has already succeeded.
		try:
			from edupro_sms.doctype.report_card.report_card import maybe_generate_report_card

			acting_user = frappe.session.user
			frappe.set_user("Administrator")
			try:
				maybe_generate_report_card(student, plan.student_group, plan.academic_term)
			finally:
				frappe.set_user(acting_user)
		except Exception:
			frappe.log_error(title="Auto report card generation failed")

	frappe.db.commit()
	return {"saved": saved}
