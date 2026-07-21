"""Headmaster-facing class/subject rollups -- everything here is scoped
to the current Academic Term and computed from real Report Card /
Assessment Result data, no fabricated trend figures."""

import frappe
from frappe.utils import flt

from edupro_sms.academic_calendar import get_current_term
from edupro_sms.grading import get_grade_for_percentage, get_grading_scale_for_program


def get_class_summary_rows(academic_term: str | None = None) -> list[dict]:
	"""One row per Student Group for the headmaster's Class Performance
	Overview table -- teacher, student count, average %, grade, and a
	Complete/In Progress/Pending status."""
	academic_term = academic_term or get_current_term()
	groups = frappe.get_all("Student Group", fields=["name", "program", "class_teacher"], order_by="name asc")

	rows = []
	for group in groups:
		student_count = frappe.db.count("Student Group Student", {"parent": group.name, "active": 1})
		cards = frappe.get_all(
			"Report Card",
			filters={"student_group": group.name, "academic_term": academic_term, "docstatus": ["!=", 2]},
			fields=["average_percentage", "workflow_state"],
		)
		class_teacher_name = (
			frappe.db.get_value("Instructor", group.class_teacher, "instructor_name") if group.class_teacher else None
		)

		average = (sum(flt(c.average_percentage) for c in cards) / len(cards)) if cards else None
		grade = get_grade_for_percentage(get_grading_scale_for_program(group.program), average)

		if not cards:
			status = "Pending"
		elif all(c.workflow_state == "Published" for c in cards) and len(cards) >= student_count and student_count:
			status = "Complete"
		else:
			status = "In Progress"

		published_count = sum(1 for c in cards if c.workflow_state == "Published")
		reviewed_count = sum(1 for c in cards if c.workflow_state == "Reviewed")
		approved_count = sum(1 for c in cards if c.workflow_state == "Approved")

		rows.append(
			{
				"student_group": group.name,
				"program": group.program,
				"class_teacher": class_teacher_name or "Not assigned",
				"student_count": student_count,
				"average_percentage": average,
				"grade": grade,
				"status": status,
				"reports_count": len(cards),
				"published_count": published_count,
				"reviewed_count": reviewed_count,
				"approved_count": approved_count,
			}
		)
	return rows


def get_class_review(student_group: str, academic_term: str | None = None) -> dict:
	"""Full drill-down for one class: stats, grade distribution, and a
	ranked student list -- everything the headmaster needs to review
	before approving that class's reports."""
	academic_term = academic_term or get_current_term()

	group = frappe.get_doc("Student Group", student_group)
	class_teacher_name = (
		frappe.db.get_value("Instructor", group.class_teacher, "instructor_name") if group.class_teacher else None
	)

	cards = frappe.get_all(
		"Report Card",
		filters={"student_group": student_group, "academic_term": academic_term, "docstatus": ["!=", 2]},
		fields=[
			"name",
			"student",
			"student_name",
			"average_percentage",
			"overall_grade",
			"workflow_state",
			"class_teacher_comment",
			"headmaster_comment",
		],
	)
	cards.sort(key=lambda c: flt(c.average_percentage), reverse=True)

	students = []
	rank = 0
	last_avg = None
	for idx, card in enumerate(cards, start=1):
		if card.average_percentage != last_avg:
			rank = idx
			last_avg = card.average_percentage
		subject_count = frappe.db.count("Report Card Assessment Result", {"parent": card.name})
		students.append(
			{
				"position": rank,
				"student": card.student,
				"student_name": card.student_name,
				"subject_count": subject_count,
				"average_percentage": card.average_percentage,
				"grade": card.overall_grade,
				"workflow_state": card.workflow_state,
				"report_card": card.name,
				"class_teacher_comment": card.class_teacher_comment or "",
				"headmaster_comment": card.headmaster_comment or "",
			}
		)

	average = (sum(flt(c.average_percentage) for c in cards) / len(cards)) if cards else None
	grade_distribution = {}
	for card in cards:
		grade_distribution[card.overall_grade] = grade_distribution.get(card.overall_grade, 0) + 1

	pass_count = sum(1 for c in cards if flt(c.average_percentage) >= 50)
	pass_rate = round((pass_count / len(cards)) * 100) if cards else None

	position_among_classes, total_classes = _class_position(student_group, academic_term)

	teacher_comments = [c.class_teacher_comment for c in cards if c.class_teacher_comment]

	return {
		"student_group": student_group,
		"program": group.program,
		"class_teacher": class_teacher_name or "Not assigned",
		"academic_term": academic_term,
		"student_count": frappe.db.count("Student Group Student", {"parent": student_group, "active": 1}),
		"average_percentage": average,
		"overall_grade": get_grade_for_percentage(get_grading_scale_for_program(group.program), average),
		"pass_rate": pass_rate,
		"grade_distribution": grade_distribution,
		"position_among_classes": position_among_classes,
		"total_classes": total_classes,
		"students": students,
		"teacher_comments": teacher_comments,
		"reviewed_count": sum(1 for c in cards if c.workflow_state == "Reviewed"),
		"approved_count": sum(1 for c in cards if c.workflow_state == "Approved"),
		"published_count": sum(1 for c in cards if c.workflow_state == "Published"),
	}


def _class_position(student_group: str, academic_term: str) -> tuple[int | None, int]:
	rows = get_class_summary_rows(academic_term)
	ranked = sorted(
		[r for r in rows if r["average_percentage"] is not None], key=lambda r: r["average_percentage"], reverse=True
	)
	for idx, r in enumerate(ranked, start=1):
		if r["student_group"] == student_group:
			return idx, len(rows)
	return None, len(rows)


def get_subject_analysis(academic_term: str | None = None, top_n: int = 3) -> dict:
	"""Strong/weak subjects school-wide this term -- real per-Course
	averages across every submitted Assessment Result, not per-topic
	(no per-topic/strand data exists to support that finer claim)."""
	academic_term = academic_term or get_current_term()

	rows = frappe.db.sql(
		"""
		select ar.course as course, avg(ar.total_score / ar.maximum_score * 100) as avg_pct, count(*) as cnt
		from `tabAssessment Result` ar
		where ar.academic_term = %s and ar.docstatus = 1 and ar.maximum_score > 0
		group by ar.course
		order by avg_pct desc
		""",
		(academic_term,),
		as_dict=True,
	)
	for r in rows:
		r["avg_pct"] = flt(r["avg_pct"])

	return {
		"strong": rows[:top_n],
		"weak": list(reversed(rows[-top_n:])) if len(rows) > top_n else [],
	}


def get_recent_activity(limit: int = 8) -> list[dict]:
	"""Real recent events -- built entirely from fields that actually
	exist and are populated: each Report Card's own `modified` timestamp
	and current `workflow_state` (Report Card doesn't have change
	tracking enabled, so there's no way to know exactly when a
	transition happened or reconstruct a true event history -- this
	shows "last touched at TIME, currently in STATE", not a fabricated
	play-by-play), plus classes whose assessment date has passed with
	zero marks entered."""
	activity = []

	recent_cards = frappe.get_all(
		"Report Card",
		filters={"docstatus": ["!=", 2]},
		fields=["student_name", "student_group", "workflow_state", "modified"],
		order_by="modified desc",
		limit=limit,
	)
	for card in recent_cards:
		activity.append(
			{
				"when": card.modified,
				"when_display": frappe.utils.format_datetime(card.modified, "yyyy-MM-dd HH:mm"),
				"text": f"{card.student_group}: {card.student_name}'s report is now {card.workflow_state}",
				"kind": "approval",
			}
		)

	today = frappe.utils.today()
	overdue_plans = frappe.get_all(
		"Assessment Plan",
		filters={"schedule_date": ["<", today]},
		fields=["name", "student_group", "course", "schedule_date"],
		order_by="schedule_date desc",
		limit=50,
	)
	for plan in overdue_plans:
		if len(activity) >= limit * 2:
			break
		entered = frappe.db.count("Assessment Result", {"assessment_plan": plan.name, "docstatus": 1})
		if entered == 0:
			activity.append(
				{
					"when": plan.schedule_date,
					"when_display": str(plan.schedule_date),
					"text": f"{plan.student_group}: no marks entered yet for {plan.course} (due {plan.schedule_date})",
					"kind": "alert",
				}
			)

	activity.sort(key=lambda a: str(a["when"]), reverse=True)
	return activity[:limit]
