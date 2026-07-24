"""Shared Grade Boundaries data -- sourced from the real curriculum
Grading Scales (Education's own doctype) rather than hardcoded, so the
reference table shown to teachers always matches what actually decides
a grade. Also used to drive the live grade calculation in the browser
as marks are typed, the grade-distribution chart, and the Report Card's
auto-loaded per-subject comment (grading.get_grade_description)."""

import frappe

# Cosmetic-only banding for the reference table; not used for the
# actual grade calculation (that stays entirely in Education's
# get_grade, driven by the intervals themselves).
_COLOR_BY_GRADE = {
	"A*": "green",
	"A*/A": "green",
	"A": "green",
	"B": "blue",
	"C": "yellow",
	"D": "orange",
	"E": "red",
	"F": "red",
	"U": "red",
	"Ungraded": "red",
}

# (School Settings.curriculum_board, Program.curriculum "band") -> Grading Scale name.
_GRADING_SCALE_BY_BOARD_AND_BAND = {
	("Cambridge", "Form 1-2"): "Cambridge Form 1-2",
	("Cambridge", "O Level"): "Cambridge O Level",
	("Cambridge", "A Level"): "Cambridge A Level",
	("ZIMSEC", "Form 1-2"): "ZIMSEC Form 1-2",
	("ZIMSEC", "O Level"): "ZIMSEC O Level",
	("ZIMSEC", "A Level"): "ZIMSEC A Level",
}

DEFAULT_GRADING_SCALE = "Cambridge O Level"


def get_grading_scale_for_program(program: str | None) -> str:
	"""Which of the 6 curriculum Grading Scales applies to a Program --
	the school-wide curriculum board (Cambridge/ZIMSEC, School Settings)
	combined with that Program's own grading band (Form 1-2/O Level/A
	Level, via the repurposed Curriculum doctype -- Form level decides
	the band regardless of which board the school is currently running)."""
	board = frappe.db.get_single_value("School Settings", "curriculum_board") or "Cambridge"
	band = frappe.db.get_value("Program", program, "curriculum") if program else None
	return _GRADING_SCALE_BY_BOARD_AND_BAND.get((board, band), DEFAULT_GRADING_SCALE)


def get_grade_description(grading_scale: str, grade_code: str | None) -> str | None:
	"""The Remark text for a grade already computed against a scale (e.g.
	"Very good" for a Cambridge O Level "B") -- used to auto-fill a
	Report Card subject's comment instead of leaving it blank."""
	if not grade_code or not frappe.db.exists("Grading Scale", grading_scale):
		return None
	doc = frappe.get_cached_doc("Grading Scale", grading_scale)
	for interval in doc.intervals:
		if interval.grade_code == grade_code:
			return interval.grade_description
	return None


# Canned per-subject remark for a Report Card row, shown when a teacher
# leaves the comment blank -- keyed off the Exam Mark criterion's own
# grade (not the combined Term+Exam grade) and banded by Form level.
# Grading scale names ending "A Level" are Form 5-6 (Lower/Upper Sixth);
# the "Form 1-2"/"O Level" scales are all Form 1-4.
_SUBJECT_COMMENT_BY_BAND_AND_GRADE = {
	"Form 1-4": {
		"A*": "Outstanding performance. Keep up the excellent work.",
		"A": "Excellent achievement. Continue striving for excellence.",
		"B": "Very good performance. Aim for greater consistency to reach the top grade.",
		"C": "Good work. With more effort and revision, you can improve further.",
		"D": "Fair performance. More commitment and regular practice are needed.",
		"E": "Basic understanding shown, but significant improvement is required.",
		"F": "Below expectations. Work harder and seek help regularly.",
		"G": "Limited achievement. Greater effort and consistent study are essential.",
		"U": "Unsatisfactory performance. Immediate improvement in effort and commitment is needed.",
	},
	"Form 5-6": {
		"A*": "Exceptional performance. Demonstrates outstanding understanding and independent thinking.",
		"A": "Excellent work. Continue maintaining this high standard.",
		"B": "Very good performance. Greater consistency and deeper analysis will lead to higher achievement.",
		"C": "Satisfactory performance. More critical engagement and regular revision are needed.",
		"D": "A basic understanding is evident, but more focused effort is required.",
		"E": "Minimum standard achieved. Greater commitment and independent study are essential.",
		"U": "Performance is below the required standard. Significant improvement in effort, attendance, and study habits is urgently needed.",
	},
}


def get_subject_comment(grading_scale: str | None, exam_grade: str | None) -> str | None:
	"""Canned Report Card remark for the given Exam Mark grade, banded by
	Form level. Returns None if there's no Exam Mark grade to key off, or
	the grade isn't one of the band's known codes."""
	if not exam_grade:
		return None
	band = "Form 5-6" if grading_scale and grading_scale.endswith("A Level") else "Form 1-4"
	return _SUBJECT_COMMENT_BY_BAND_AND_GRADE[band].get(exam_grade)


def get_grade_for_percentage(grading_scale: str, percentage: float | None) -> str | None:
	"""Letter grade for a percentage against a named scale. Deliberately
	doesn't call Education's own get_grade(): that function caches
	`frappe.local.grading_scale` keyed only by *whether it's set*, not by
	which scale was requested, so a second call in the same request with
	a different scale silently reuses the first scale's (possibly empty)
	intervals -- an empty interval list then leaves its `grade` local
	unassigned and raises UnboundLocalError. get_grade_boundaries() below
	is cached per-scale via frappe.get_cached_doc, so it doesn't have
	that cross-contamination bug."""
	if percentage is None:
		return None
	boundaries = get_grade_boundaries(grading_scale)
	for row in boundaries:
		if flt(percentage) >= flt(row["low"]):
			return row["grade_code"]
	return boundaries[-1]["grade_code"] if boundaries else None


def get_grade_boundaries(grading_scale: str = DEFAULT_GRADING_SCALE) -> list[dict]:
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
