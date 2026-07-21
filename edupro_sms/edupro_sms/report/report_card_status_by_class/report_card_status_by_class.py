# Copyright (c) 2026, Edupro and contributors
# For license information, please see license.txt

"""Headmaster dashboard: one row per Class + Term, with a count of Report
Cards in each workflow state plus how many students in the class still
have no Report Card at all (not yet generated / missing required marks).
"""

import frappe


def execute(filters=None):
	filters = filters or {}
	columns = _columns()
	data = _rows(filters)
	return columns, data


def _columns():
	return [
		{"fieldname": "student_group", "label": "Class", "fieldtype": "Link", "options": "Student Group", "width": 160},
		{"fieldname": "academic_term", "label": "Term", "fieldtype": "Link", "options": "Academic Term", "width": 160},
		{"fieldname": "total_students", "label": "Students", "fieldtype": "Int", "width": 90},
		{"fieldname": "not_generated", "label": "Not Generated", "fieldtype": "Int", "width": 110},
		{"fieldname": "pending_approval", "label": "Pending Approval", "fieldtype": "Int", "width": 130},
		{"fieldname": "reviewed", "label": "Reviewed", "fieldtype": "Int", "width": 100},
		{"fieldname": "approved", "label": "Approved", "fieldtype": "Int", "width": 100},
		{"fieldname": "rejected", "label": "Rejected", "fieldtype": "Int", "width": 100},
		{"fieldname": "published", "label": "Published", "fieldtype": "Int", "width": 100},
	]


def _rows(filters):
	group_filters = {}
	if filters.get("student_group"):
		group_filters["name"] = filters["student_group"]

	groups = frappe.get_all("Student Group", filters=group_filters, fields=["name", "academic_term"])
	rows = []
	for group in groups:
		if not group.academic_term:
			continue
		if filters.get("academic_term") and group.academic_term != filters["academic_term"]:
			continue

		total_students = frappe.db.count(
			"Student Group Student", {"parent": group.name, "active": 1}
		)

		state_counts = {
			state: frappe.db.count(
				"Report Card",
				{"student_group": group.name, "academic_term": group.academic_term, "workflow_state": state},
			)
			for state in ("Pending Approval", "Reviewed", "Approved", "Rejected", "Published")
		}
		generated = sum(state_counts.values())

		rows.append(
			{
				"student_group": group.name,
				"academic_term": group.academic_term,
				"total_students": total_students,
				"not_generated": max(total_students - generated, 0),
				"pending_approval": state_counts["Pending Approval"],
				"reviewed": state_counts["Reviewed"],
				"approved": state_counts["Approved"],
				"rejected": state_counts["Rejected"],
				"published": state_counts["Published"],
			}
		)
	return rows
