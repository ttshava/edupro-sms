# Copyright (c) 2026, Edupro and contributors
# For license information, please see license.txt

"""Teacher dashboard: every Class + Subject + Term the logged-in
Instructor is assigned to teach, with marks-entry progress.

Relies entirely on Assessment Plan's own permission scoping
(edupro_sms.teacher_permissions) -- frappe.get_list respects
that automatically, so an Instructor only ever sees their own classes
without any extra filtering logic here. Headmaster/System Manager see
every class (their permission scoping returns unrestricted access).
"""

import frappe


def execute(filters=None):
	columns = _columns()
	data = _rows()
	return columns, data


def _columns():
	return [
		{"fieldname": "student_group", "label": "Class", "fieldtype": "Link", "options": "Student Group", "width": 140},
		{"fieldname": "course", "label": "Subject", "fieldtype": "Link", "options": "Course", "width": 220},
		{"fieldname": "academic_term", "label": "Term", "fieldtype": "Link", "options": "Academic Term", "width": 140},
		{"fieldname": "schedule_date", "label": "Assessment Date", "fieldtype": "Date", "width": 120},
		{"fieldname": "total_students", "label": "Students", "fieldtype": "Int", "width": 90},
		{"fieldname": "marks_entered", "label": "Marks Entered", "fieldtype": "Int", "width": 110},
		{"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 130},
	]


def _rows():
	plans = frappe.get_list(
		"Assessment Plan",
		fields=["name", "student_group", "course", "academic_term", "schedule_date", "grading_scale"],
		order_by="student_group asc, course asc",
	)

	rows = []
	for plan in plans:
		total_students = frappe.db.count("Student Group Student", {"parent": plan.student_group, "active": 1})
		marks_entered = frappe.db.count(
			"Assessment Result", {"assessment_plan": plan.name, "docstatus": 1}
		)
		status = "Complete" if total_students and marks_entered >= total_students else "In Progress"
		rows.append(
			{
				"name": plan.name,
				"student_group": plan.student_group,
				"course": plan.course,
				"academic_term": plan.academic_term,
				"schedule_date": plan.schedule_date,
				"grading_scale": plan.grading_scale,
				"total_students": total_students,
				"marks_entered": marks_entered,
				"status": status,
			}
		)
	return rows
