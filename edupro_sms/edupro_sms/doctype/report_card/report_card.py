# Copyright (c) 2026, Edupro and contributors
# For license information, please see license.txt

import secrets

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from grading import DEFAULT_GRADING_SCALE, get_grade_description, get_grade_for_percentage


class ReportCard(Document):
	def on_update_after_submit(self):
		"""Fires on every field change while docstatus=1 — e.g. the
		Approved -> Published workflow transition (allow_on_submit lets
		workflow_state change post-submit). Only act the moment it
		actually becomes Published, not on every such update."""
		if self.workflow_state != "Published":
			return

		if not self.verification_code:
			# Random, unguessable token (not the predictable "RC-..." doc
			# name) -- this is what the print format's QR code encodes, so
			# scanning it can't be used to enumerate other students' reports.
			self.db_set("verification_code", secrets.token_hex(8), update_modified=False)

		from doctype.report_card.notify import EMAIL_DELIVERY_ENABLED

		if EMAIL_DELIVERY_ENABLED and not self.sent_to_parent_at:
			frappe.enqueue(
				"edupro_sms.edupro_sms.doctype.report_card.notify.send_report_card_emails",
				queue="short",
				report_card_name=self.name,
			)


def get_permission_query_conditions(user: str | None = None) -> str:
	"""Row-level scoping for the Report Card list view.

	- System Manager / Headmaster: unrestricted.
	- Class Teacher: only classes where they're Student Group.class_teacher.
	- Student: only their own report, and only once Published.
	- Guardian: only their linked children's reports, and only once Published.
	"""
	user = user or frappe.session.user
	if user == "Administrator":
		return ""

	roles = set(frappe.get_roles(user))
	if "System Manager" in roles or "Headmaster" in roles:
		return ""

	conditions = []

	if "Class Teacher" in roles:
		instructor = frappe.db.get_value("Instructor", {"user": user}, "name")
		if instructor:
			groups = frappe.get_all("Student Group", filters={"class_teacher": instructor}, pluck="name")
			if groups:
				group_list = ", ".join(frappe.db.escape(g) for g in groups)
				conditions.append(f"`tabReport Card`.student_group in ({group_list})")

	if "Student" in roles:
		student = frappe.db.get_value("Student", {"user": user}, "name")
		if student:
			conditions.append(
				f"(`tabReport Card`.student = {frappe.db.escape(student)} "
				f"and `tabReport Card`.workflow_state = 'Published')"
			)

	if "Guardian" in roles:
		guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
		if guardian:
			children = frappe.get_all(
				"Student Guardian", filters={"guardian": guardian, "parenttype": "Student"}, pluck="parent"
			)
			if children:
				child_list = ", ".join(frappe.db.escape(c) for c in children)
				conditions.append(
					f"(`tabReport Card`.student in ({child_list}) "
					f"and `tabReport Card`.workflow_state = 'Published')"
				)

	if not conditions:
		# Has a portal role but no matching Instructor/Student/Guardian
		# record (or a role with no scoping rule defined) -> see nothing,
		# not everything. Fail closed.
		return "1=0"

	return "(" + " or ".join(conditions) + ")"


def has_permission(doc, user: str | None = None, permission_type: str | None = None) -> bool:
	"""Single-document check (print view, direct /app/report-card/<name>
	access) — same rules as get_permission_query_conditions, evaluated
	against one document instead of a SQL fragment."""
	user = user or frappe.session.user
	if user == "Administrator":
		return True

	roles = set(frappe.get_roles(user))
	if "System Manager" in roles or "Headmaster" in roles:
		return True

	if "Class Teacher" in roles:
		instructor = frappe.db.get_value("Instructor", {"user": user}, "name")
		if instructor and frappe.db.get_value("Student Group", doc.student_group, "class_teacher") == instructor:
			return True

	if doc.workflow_state == "Published":
		if "Student" in roles:
			student = frappe.db.get_value("Student", {"user": user}, "name")
			if student and doc.student == student:
				return True

		if "Guardian" in roles:
			guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
			if guardian and frappe.db.exists(
				"Student Guardian", {"guardian": guardian, "parent": doc.student, "parenttype": "Student"}
			):
				return True

	return False


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

	created, updated, skipped = [], [], []

	for row in group.students:
		if not row.active:
			continue
		required_courses = _required_courses_for_student(row.student, group)
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


def maybe_generate_report_card(student: str, student_group: str, academic_term: str) -> dict | None:
	"""Auto-trigger for one student, called by marks_entry.save_marks()
	right after every submit -- the moment their last required subject is
	in, this generates/updates their Report Card and re-ranks the class,
	so a complete student flows straight into Class Teacher review with
	no separate "generate reports" step for anyone to remember to run.
	Silently no-ops (returns None) if they're still missing subjects --
	exactly the same completeness check generate_report_cards() itself
	uses, just scoped to one student instead of the whole class."""
	group = frappe.get_doc("Student Group", student_group)
	required_courses = _required_courses_for_student(student, group)
	if not required_courses:
		return None

	result = _generate_for_student(student, group, academic_term, required_courses)
	if result:
		_calculate_positions(student_group, academic_term)
	return result


def _required_courses_for(group) -> list[str]:
	"""Fallback only -- the Program's blanket required-course list, used
	when a student has no Program Enrollment (or it has no courses
	recorded yet). Prefer _required_courses_for_student(), which reflects
	each student's own subjects including their elective choice."""
	if not group.program:
		return []
	program = frappe.get_doc("Program", group.program)
	return [c.course for c in program.courses if c.required]


def _required_courses_for_student(student: str, group) -> list[str]:
	"""A student's real, personal subject list: their own Program
	Enrollment.courses (core subjects + whichever elective they picked),
	not the Program's one-size-fits-all required list -- two students in
	the same class can legitimately take different subjects (e.g. one
	chose Computer Science, another chose Textile Technology)."""
	if not group.program:
		return []

	enrollment_name = frappe.db.get_value(
		"Program Enrollment", {"student": student, "program": group.program}, "name"
	)
	if enrollment_name:
		courses = frappe.get_all(
			"Program Enrollment Course", filters={"parent": enrollment_name}, pluck="course"
		)
		if courses:
			return courses

	return _required_courses_for(group)


def _practical_courses_for_program(program: str | None) -> set[str]:
	"""Every course this Program offers under the "Practical" elective
	group (Fashion and Textiles / Design and Technology / Building
	Technology / Computer Science, depending on Form) -- whichever one a
	student picked, it reports as a single "Practical" line, never its
	real name. Empty for programs with no practical family (A-Level)."""
	if not program:
		return set()
	return set(frappe.get_all("Program Course", filters={"parent": program, "elective_group": "Practical"}, pluck="course"))


def _practical_none_row() -> dict:
	"""Synthetic Report Card row for a student with no practical subject
	in their Program Enrollment at all (real for some Form 3-4 students)
	-- shown as "Practical: NONE" rather than silently omitted, and
	deliberately not backed by any Assessment Result (there is nothing to
	link -- no marks were ever going to exist for a subject the student
	doesn't take), so it's excluded from the total/average calculation."""
	return {
		"assessment_result": None,
		"course": None,
		"reporting_subject": "Practical",
		"total_score": None,
		"maximum_score": None,
		"grade": "NONE",
		"term_mark": None,
		"term_grade": "NONE",
		"exam_mark": None,
		"exam_grade": "NONE",
		"comment": "No practical subject enrolled.",
	}


def _report_row_sort_key(row: dict):
	"""Alphabetical by displayed subject name, except Practical (real or
	NONE) always sorts last, per the school's requested layout."""
	is_practical = row.get("reporting_subject") == "Practical"
	label = row.get("reporting_subject") or row.get("course") or ""
	return (1 if is_practical else 0, label)


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
	grading_scale = results[0].grading_scale if results else DEFAULT_GRADING_SCALE
	overall_grade = get_grade_for_percentage(grading_scale, average_percentage)

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

	practical_courses = _practical_courses_for_program(group.program)
	subject_rows = [_subject_row(r, practical_courses) for r in results]
	if practical_courses and not (practical_courses & found_courses):
		subject_rows.append(_practical_none_row())
	subject_rows.sort(key=_report_row_sort_key)
	report_card.set("assessment_results", subject_rows)

	if is_new:
		report_card.insert()
	else:
		report_card.save()

	return {"name": report_card.name, "is_new": is_new}


def _subject_row(result, practical_courses: set[str] | None = None) -> dict:
	"""One Report Card Assessment Result row -- the overall subject
	score/grade (unchanged from before) plus the Term Mark/Exam Mark
	breakdown pulled from the underlying Assessment Result's own detail
	rows, and a comment auto-filled from the grade's Remark text unless
	a teacher already wrote a specific one in.

	`course` always stays the real taught subject (Teaching Subject) --
	`reporting_subject`, when set, is what's actually displayed (Reporting
	Subject). Only the four real practical courses get this override, to
	"Practical"; every other subject displays under its own name."""
	details = frappe.get_all(
		"Assessment Result Detail",
		filters={"parent": result.name},
		fields=["assessment_criteria", "score", "maximum_score", "grade"],
	)
	by_criteria = {d.assessment_criteria: d for d in details}
	term = by_criteria.get("Term Mark")
	exam = by_criteria.get("Exam Mark")

	comment = result.comment or get_grade_description(result.grading_scale, result.grade)

	return {
		"assessment_result": result.name,
		"course": result.course,
		"reporting_subject": "Practical" if practical_courses and result.course in practical_courses else None,
		"total_score": result.total_score,
		"maximum_score": result.maximum_score,
		"grade": result.grade,
		"term_mark": term.score if term else None,
		"term_grade": term.grade if term else None,
		"exam_mark": exam.score if exam else None,
		"exam_grade": exam.grade if exam else None,
		"comment": comment,
	}


def _calculate_positions(student_group: str, academic_term: str):
	"""Standard competition ranking: equal averages share a rank, and the
	next distinct rank skips accordingly (two students tied at 3 both show
	3, the next student shows 5, not 4).

	Also (re)generates both comment fields here rather than in
	_generate_for_student() -- position/number_of_students aren't known
	until this whole-class pass runs, and an insightful comment wants to
	reference them. Runs on every completion (not just full-batch
	generation), so as more classmates finish, everyone's comment stays
	current -- there's no manual override to preserve since Class
	Teacher/Headmaster no longer hand-type these (see .claude/DECISIONS.md
	on removing that input in favour of auto-generated remarks)."""
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
		doc = frappe.get_doc("Report Card", card.name)
		frappe.db.set_value(
			"Report Card",
			card.name,
			{
				"position": rank,
				"number_of_students": count,
				"class_teacher_comment": _generate_class_teacher_comment(doc, rank, count),
				"headmaster_comment": _generate_headmaster_comment(doc, rank, count),
			},
		)


_GRADE_TIERS = {
	"A*": "excellent", "A": "excellent", "A*/A": "excellent",
	"B": "good",
	"C": "solid",
	"D": "needs_improvement",
	"E": "at_risk", "F": "at_risk", "U": "at_risk", "Ungraded": "at_risk",
}


def _grade_tier(grade_code: str | None) -> str:
	return _GRADE_TIERS.get(grade_code, "solid")


def _ordinal(n: int) -> str:
	if 11 <= (n % 100) <= 13:
		suffix = "th"
	else:
		suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
	return f"{n}{suffix}"


def _best_and_worst_subjects(assessment_results) -> tuple[str | None, str | None]:
	"""Real strongest/weakest subject by percentage -- excludes the
	synthetic Practical/NONE row (no score to compare) and skips entirely
	if there's only one scored subject (nothing meaningful to contrast)."""
	scored = [
		(r.reporting_subject or r.course, flt(r.total_score) / flt(r.maximum_score))
		for r in assessment_results
		if r.course and r.maximum_score
	]
	if len(scored) < 2:
		return (scored[0][0], None) if scored else (None, None)
	scored.sort(key=lambda x: x[1])
	return scored[-1][0], scored[0][0]


def _generate_class_teacher_comment(report_card, position: int, count: int) -> str:
	"""Insightful, multi-sentence remark grounded entirely in this term's
	real results -- grade tier, class standing, and the student's actual
	strongest/weakest subject. Warmer and more pastoral in tone than the
	Headmaster's, since this is the teacher who sees the student daily."""
	name = (report_card.student_name or "This student").split(" ")[0]
	avg = flt(report_card.average_percentage)
	grade = report_card.overall_grade or "-"
	tier = _grade_tier(grade)
	best, worst = _best_and_worst_subjects(report_card.assessment_results)
	pos_clause = f", finishing {_ordinal(position)} out of {count} in the class," if position and count else ""

	if tier == "excellent":
		subject_line = f" {name} performed particularly strongly in {best}, and" if best else f" {name}"
		return (
			f"An outstanding term for {name}{pos_clause} with an average of {avg:.1f}% (Grade {grade})."
			f"{subject_line} showed real depth of understanding across the board. "
			f"Effort and focus have clearly paid off this term -- keep up this excellent standard."
		)
	if tier == "good":
		mid = f"{name}'s best results came in {best}" if best else f"{name} showed good results overall"
		tail = f", though more consistency in {worst} would help push things further" if worst else ""
		return (
			f"A solid, encouraging term for {name}{pos_clause} with an average of {avg:.1f}% (Grade {grade}). "
			f"{mid}{tail}. A promising foundation to build on next term."
		)
	if tier == "solid":
		detail = f" Results were strongest in {best}" + (f", but {worst} needs more focused attention" if worst else "") + "." if best else ""
		return (
			f"{name} achieved an average of {avg:.1f}% (Grade {grade}) this term{pos_clause.rstrip(',')}.{detail} "
			f"With more consistent effort and regular revision across all subjects, {name} is capable of a stronger result next term."
		)
	if tier == "needs_improvement":
		weak_line = f" {worst} in particular needs urgent attention" + (f", though {best} shows real capability" if best else "") + "." if worst else ""
		return (
			f"{name}'s average this term was {avg:.1f}% (Grade {grade}){pos_clause.rstrip(',')}, which falls below expectation.{weak_line} "
			f"I strongly encourage extra effort, better time management, and support at home to turn this around next term."
		)
	# at_risk
	weak_line = f", especially in {worst}," if worst else ""
	return (
		f"This has been a difficult term for {name}{pos_clause} with an average of {avg:.1f}% (Grade {grade}). "
		f"Performance across most subjects{weak_line} is well below what is needed. "
		f"I recommend a meeting with parents/guardians to put a focused support plan in place before next term."
	)


def _generate_headmaster_comment(report_card, position: int, count: int) -> str:
	"""Shorter, more formal endorsement-style remark for the Headmaster --
	same underlying data as the Class Teacher's comment, different
	register: evaluative and standing-focused rather than pastoral."""
	name = (report_card.student_name or "This student").split(" ")[0]
	avg = flt(report_card.average_percentage)
	grade = report_card.overall_grade or "-"
	tier = _grade_tier(grade)
	pos_clause = f", ranking {_ordinal(position)} out of {count} students in the class," if position and count else ""

	if tier == "excellent":
		return (
			f"An excellent set of results this term{pos_clause} with an average of {avg:.1f}% (Grade {grade}). "
			f"{name} is commended for this outstanding academic performance and is encouraged to maintain this standard."
		)
	if tier == "good":
		return (
			f"A good, consistent performance this term{pos_clause} averaging {avg:.1f}% (Grade {grade}). "
			f"{name} is encouraged to keep building on this progress with continued effort next term."
		)
	if tier == "solid":
		return (
			f"A satisfactory term overall{pos_clause} with an average of {avg:.1f}% (Grade {grade}). "
			f"{name} has the ability to achieve more with greater consistency and focus."
		)
	if tier == "needs_improvement":
		return (
			f"This term's results{pos_clause} averaging {avg:.1f}% (Grade {grade}), fall below the expected standard. "
			f"{name} is urged to work more closely with teachers and put in significantly more effort next term."
		)
	return (
		f"This term's performance{pos_clause} at {avg:.1f}% (Grade {grade}), is a serious concern. "
		f"I urge {name}, together with parents/guardians and teachers, to take immediate corrective action."
	)
