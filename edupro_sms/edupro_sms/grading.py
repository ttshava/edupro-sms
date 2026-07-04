"""Shared Grade Boundaries data -- sourced from the real IGCSE Standard
Grading Scale (Education's own doctype) rather than hardcoded, so the
reference table shown to teachers always matches what actually decides
a grade. Also used to drive the live grade calculation in the browser
as marks are typed, and the grade-distribution chart."""

import frappe

# Cosmetic-only banding for the reference table; not used for the
# actual grade calculation (that stays entirely in Education's
# get_grade, driven by the intervals themselves).
_COLOR_BY_GRADE = {
	"A*": "green",
	"A": "green",
	"B": "blue",
	"C": "yellow",
	"D": "orange",
	"E": "red",
	"F": "red",
}


def get_grade_boundaries(grading_scale: str = "IGCSE Standard") -> list[dict]:
	if not frappe.db.exists("Grading Scale", grading_scale):
		return []

	doc = frappe.get_cached_doc("Grading Scale", grading_scale)
	intervals = sorted(doc.intervals, key=lambda i: flt(i.threshold), reverse=True)

	rows = []
	for idx, interval in enumerate(intervals):
		upper = 100 if idx == 0 else flt(intervals[idx - 1].threshold) - 1
		rows.append(
			{
				"grade_code": interval.grade_code,
				"low": interval.threshold,
				"high": upper,
				"description": interval.grade_description,
				"color": _COLOR_BY_GRADE.get(interval.grade_code, "grey"),
			}
		)
	return rows


def flt(v):
	return frappe.utils.flt(v)
