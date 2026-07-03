# Copyright (c) 2026, Edupro and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from education.education.api import get_grade


class ReportCard(Document):
	pass


@frappe.whitelist()
def generate_report_cards(student_group: str, academic_term: str) -> dict:
	"""Aggregate each active student's submitted Assessment Results for a
	term into a Report Card (Draft/Pending Approval), then rank the class.

	Only considers Assessment Results with docstatus=1 (submitted) — marks
	still in draft on the subject level aren't ready to roll up yet. A
	student missing any of their Program's required courses is skipped and
	reported back, not silently included with a partial total.
	"""
	group = frappe.get_doc("Student Group", student_group)
	required_courses = _required_courses_for(group)

	created, updated, skipped = [], [], []

	for row in group.students:
		if not row.active:
			continue
		result = _generate_for_student(row.student, group, academic_term, required_courses)
		if result is None:
			skipped.append(row.student_name or row.student)
		elif result["is_new"]:
			created.append(result["name"])
		else:
			updated.append(result["name"])

	_calculate_positions(student_group, academic_term)

	return {
		"created": created,
		"updated": updated,
		"skipped": skipped,
	}


def _required_courses_for(group) -> list[str]:
	if not group.program:
		return []
	program = frappe.get_doc("Program", group.program)
	return [c.course for c in program.courses if c.required]


def _generate_for_student(student: str, group, academic_term: str, required_courses: list[str]):
	results = frappe.get_all(
		"Assessment Result",
		filters={"student": student, "student_group": group.name, "academic_term": academic_term, "docstatus": 1},
		fields=["name", "course", "total_score", "maximum_score", "grade", "comment", "grading_scale"],
	)

	found_courses = {r.course for r in results}
	missing = set(required_courses) - found_courses
	if missing:
		frappe.msgprint(
			_("Skipping {0}: missing submitted results for {1}").format(student, ", ".join(missing)),
			indicator="orange",
		)
		return None

	total_score = sum(flt(r.total_score) for r in results)
	maximum_score = sum(flt(r.maximum_score) for r in results)
	average_percentage = (total_score / maximum_score * 100) if maximum_score else 0
	grading_scale = results[0].grading_scale if results else "IGCSE Standard"
	overall_grade = get_grade(grading_scale, average_percentage)

	existing_name = frappe.db.get_value(
		"Report Card", {"student": student, "academic_term": academic_term, "docstatus": 0}
	)
	is_new = not existing_name
	report_card = frappe.get_doc("Report Card", existing_name) if existing_name else frappe.new_doc("Report Card")

	report_card.student = student
	report_card.student_group = group.name
	report_card.academic_term = academic_term
	report_card.total_score = total_score
	report_card.maximum_score = maximum_score
	report_card.average_percentage = average_percentage
	report_card.overall_grade = overall_grade
	report_card.set(
		"assessment_results",
		[
			{
				"assessment_result": r.name,
				"course": r.course,
				"total_score": r.total_score,
				"maximum_score": r.maximum_score,
				"grade": r.grade,
				"comment": r.comment,
			}
			for r in results
		],
	)

	if is_new:
		report_card.insert()
	else:
		report_card.save()

	return {"name": report_card.name, "is_new": is_new}


def _calculate_positions(student_group: str, academic_term: str):
	"""Standard competition ranking: equal averages share a rank, and the
	next distinct rank skips accordingly (two students tied at 3 both show
	3, the next student shows 5, not 4)."""
	cards = frappe.get_all(
		"Report Card",
		filters={"student_group": student_group, "academic_term": academic_term, "docstatus": ["!=", 2]},
		fields=["name", "average_percentage"],
		order_by="average_percentage desc",
	)
	count = len(cards)
	rank = 0
	last_percentage = None
	for idx, card in enumerate(cards, start=1):
		if card.average_percentage != last_percentage:
			rank = idx
			last_percentage = card.average_percentage
		frappe.db.set_value("Report Card", card.name, {"position": rank, "number_of_students": count})
