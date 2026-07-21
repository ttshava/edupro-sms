# Copyright (c) 2026, Edupro and Contributors
# See license.txt

"""Automated coverage for docs/07_Testing.md TC-01 through TC-12.

Creates its own Academic Year/Term/Program/Course/Student Group/Students
rather than depending on the Sprint 3-7 demo data — FrappeTestCase rolls
back each test's DB changes, so this is safe to run repeatedly and won't
collide with real data on a live site.
"""

import time

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days

from doctype.report_card.notify import send_report_card_emails
from doctype.report_card.report_card import (
	generate_report_cards,
	has_permission,
)

TEST_TAG = "TC-Suite"


class TestReportCard(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.academic_year = cls._ensure("Academic Year", f"{TEST_TAG} 2099", {
			"academic_year_name": f"{TEST_TAG} 2099",
			"year_start_date": "2099-01-01",
			"year_end_date": "2099-12-15",
		})
		cls.academic_term = cls._ensure(
			"Academic Term",
			f"{cls.academic_year} ({TEST_TAG} Term 1)",
			{
				"academic_year": cls.academic_year,
				"term_name": f"{TEST_TAG} Term 1",
				"term_start_date": "2099-01-01",
				"term_end_date": "2099-04-15",
			},
		)
		cls.term_2 = cls._ensure(
			"Academic Term",
			f"{cls.academic_year} ({TEST_TAG} Term 2)",
			{
				"academic_year": cls.academic_year,
				"term_name": f"{TEST_TAG} Term 2",
				"term_start_date": "2099-05-01",
				"term_end_date": "2099-08-15",
			},
		)
		cls.course_a = cls._ensure("Course", f"{TEST_TAG} Course A", {
			"course_name": f"{TEST_TAG} Course A",
			"default_grading_scale": "Cambridge O Level",
			"assessment_criteria": [
				{"assessment_criteria": cls._ensure_criteria("Test"), "weightage": 40},
				{"assessment_criteria": cls._ensure_criteria("Exam"), "weightage": 60},
			],
		})
		cls.course_b = cls._ensure("Course", f"{TEST_TAG} Course B", {
			"course_name": f"{TEST_TAG} Course B",
			"default_grading_scale": "Cambridge O Level",
		})
		cls.program = cls._ensure("Program", f"{TEST_TAG} Program", {
			"program_name": f"{TEST_TAG} Program",
			"courses": [
				{"course": cls.course_a, "required": 1},
				{"course": cls.course_b, "required": 1},
			],
		})
		cls.student_group = cls._ensure("Student Group", f"{TEST_TAG} Group", {
			"student_group_name": f"{TEST_TAG} Group",
			"group_based_on": "Batch",
			"academic_year": cls.academic_year,
			"academic_term": cls.academic_term,
			"program": cls.program,
			"max_strength": 40,
		})
		# Assessment Plan.academic_term is fetch_from student_group.academic_term
		# (docs/03_DocTypes.md / DECISIONS.md 0008) -- a Student Group is
		# locked to ONE term. TC-12 (historical term view) needs a second
		# group to represent the same class in a later term.
		cls.student_group_term2 = cls._ensure("Student Group", f"{TEST_TAG} Group Term2", {
			"student_group_name": f"{TEST_TAG} Group Term2",
			"group_based_on": "Batch",
			"academic_year": cls.academic_year,
			"academic_term": cls.term_2,
			"program": cls.program,
			"max_strength": 40,
		})

	def setUp(self):
		super().setUp()
		# Naming-series counters don't always reset cleanly with FrappeTestCase's
		# per-test rollback, which can leave a stale Report Card with the same
		# RC-{student}-{term} name from a previous test's aborted insert.
		frappe.db.delete("Report Card", {"name": ["like", f"RC-EDU-STU-%-{TEST_TAG}%"]})

	@classmethod
	def _ensure(cls, doctype, name, values):
		if frappe.db.exists(doctype, name):
			return name
		doc = frappe.get_doc({"doctype": doctype, **values})
		doc.insert(ignore_permissions=True)
		return doc.name

	@classmethod
	def _ensure_criteria(cls, name):
		if not frappe.db.exists("Assessment Criteria", name):
			frappe.get_doc({"doctype": "Assessment Criteria", "assessment_criteria": name}).insert(
				ignore_permissions=True
			)
		return name

	def _make_student(self, suffix, guardian_name=None, student_group=None):
		email = f"{TEST_TAG.lower()}.{suffix}@example.edupro.test"
		guardians = []
		if guardian_name:
			guardian = frappe.db.get_value("Guardian", {"guardian_name": guardian_name}, "name")
			if not guardian:
				guardian = frappe.get_doc(
					{"doctype": "Guardian", "guardian_name": guardian_name}
				).insert(ignore_permissions=True).name
			guardians = [{"guardian": guardian}]
		student = frappe.get_doc(
			{
				"doctype": "Student",
				"first_name": f"{TEST_TAG}-{suffix}",
				"student_email_id": email,
				"enabled": 1,
				"guardians": guardians,
			}
		)
		student.insert(ignore_permissions=True)
		self._make_student_in_group(student.name, student_group or self.student_group)
		return student.name

	def _make_student_in_group(self, student_name, student_group):
		group = frappe.get_doc("Student Group", student_group)
		group.append(
			"students",
			{
				"student": student_name,
				"student_name": frappe.db.get_value("Student", student_name, "student_name"),
				"active": 1,
			},
		)
		group.save(ignore_permissions=True)

	def _make_plan(self, course, academic_term, day_offset, student_group=None):
		return frappe.get_doc(
			{
				"doctype": "Assessment Plan",
				"student_group": student_group or self.student_group,
				"program": self.program,
				"course": course,
				"assessment_group": "All Assessment Groups",
				"grading_scale": "Cambridge O Level",
				"academic_year": self.academic_year,
				"academic_term": academic_term,
				"schedule_date": add_days("2099-04-01", day_offset),
				"from_time": "08:00:00",
				"to_time": "10:00:00",
				"maximum_assessment_score": 100,
				"assessment_criteria": [
					{"assessment_criteria": "Test", "maximum_score": 40},
					{"assessment_criteria": "Exam", "maximum_score": 60},
				],
			}
		).insert(ignore_permissions=True)

	def _submit_result(self, plan, student, test_score, exam_score, student_group=None):
		doc = frappe.get_doc(
			{
				"doctype": "Assessment Result",
				"assessment_plan": plan.name,
				"student": student,
				"student_group": student_group or self.student_group,
				"details": [
					{"assessment_criteria": "Test", "score": test_score},
					{"assessment_criteria": "Exam", "score": exam_score},
				],
			}
		)
		doc.insert(ignore_permissions=True)
		doc.submit()
		return doc

	# ------------------------------------------------------------------
	# TC-01 — Teacher enters marks for many students, no data loss
	# ------------------------------------------------------------------
	def test_tc01_bulk_marks_entry_no_data_loss(self):
		plan_a = self._make_plan(self.course_a, self.academic_term, 0)
		plan_b = self._make_plan(self.course_b, self.academic_term, 1)

		students = [self._make_student(f"tc01-{i}") for i in range(5)]
		for i, student in enumerate(students):
			self._submit_result(plan_a, student, 30 + i, 45 + i)
			self._submit_result(plan_b, student, 25 + i, 40 + i)

		for student in students:
			count = frappe.db.count(
				"Assessment Result", {"student": student, "academic_term": self.academic_term, "docstatus": 1}
			)
			self.assertEqual(count, 2, f"expected 2 submitted results for {student}, found {count}")

	# ------------------------------------------------------------------
	# TC-02 — Missing marks block report generation, not silently partial
	# ------------------------------------------------------------------
	def test_tc02_incomplete_marks_blocked_from_report(self):
		plan_a = self._make_plan(self.course_a, self.academic_term, 2)
		self._make_plan(self.course_b, self.academic_term, 3)  # course_b left unsubmitted

		student = self._make_student("tc02")
		self._submit_result(plan_a, student, 30, 45)  # only course_a submitted

		summary = generate_report_cards(self.student_group, self.academic_term)
		student_name = frappe.db.get_value("Student", student, "student_name")
		self.assertIn(student_name, summary["skipped"])
		self.assertFalse(frappe.db.exists("Report Card", {"student": student, "academic_term": self.academic_term}))

	# ------------------------------------------------------------------
	# TC-03 — Headmaster approves: workflow advances, record locks
	# ------------------------------------------------------------------
	def test_tc03_headmaster_approve_locks_and_updates_status(self):
		from frappe.model.workflow import apply_workflow

		plan_a = self._make_plan(self.course_a, self.academic_term, 4)
		plan_b = self._make_plan(self.course_b, self.academic_term, 5)
		student = self._make_student("tc03")
		self._submit_result(plan_a, student, 30, 45)
		self._submit_result(plan_b, student, 25, 40)

		generate_report_cards(self.student_group, self.academic_term)
		name = frappe.db.get_value("Report Card", {"student": student, "academic_term": self.academic_term})
		doc = frappe.get_doc("Report Card", name)
		self.assertEqual(doc.workflow_state, "Pending Approval")

		doc = apply_workflow(doc, "Review")
		self.assertEqual(doc.workflow_state, "Reviewed")

		doc = apply_workflow(doc, "Approve")
		self.assertEqual(doc.workflow_state, "Approved")
		self.assertEqual(doc.docstatus, 1)

		doc.reload()
		doc.total_score = 999
		with self.assertRaises(frappe.exceptions.UpdateAfterSubmitError):
			doc.save()

	# ------------------------------------------------------------------
	# TC-04 — Headmaster rejects: goes back to Pending Approval
	# ------------------------------------------------------------------
	def test_tc04_headmaster_reject_returns_to_pending(self):
		from frappe.model.workflow import apply_workflow

		plan_a = self._make_plan(self.course_a, self.academic_term, 6)
		plan_b = self._make_plan(self.course_b, self.academic_term, 7)
		student = self._make_student("tc04")
		self._submit_result(plan_a, student, 30, 45)
		self._submit_result(plan_b, student, 25, 40)

		generate_report_cards(self.student_group, self.academic_term)
		name = frappe.db.get_value("Report Card", {"student": student, "academic_term": self.academic_term})
		doc = frappe.get_doc("Report Card", name)
		doc = apply_workflow(doc, "Review")
		doc = apply_workflow(doc, "Reject")
		self.assertEqual(doc.workflow_state, "Rejected")
		self.assertEqual(doc.docstatus, 0, "Rejected must stay unlocked so it can be fixed")

		doc = apply_workflow(doc, "Resubmit")
		self.assertEqual(doc.workflow_state, "Pending Approval")

	# ------------------------------------------------------------------
	# TC-05 — Guardian with multiple children sees all of them
	# ------------------------------------------------------------------
	def test_tc05_guardian_with_multiple_children_sees_all(self):
		from frappe.model.workflow import apply_workflow

		guardian_name = f"{TEST_TAG} Guardian TC05"
		children = [self._make_student(f"tc05-{i}", guardian_name=guardian_name) for i in range(3)]

		plan_a = self._make_plan(self.course_a, self.academic_term, 8)
		plan_b = self._make_plan(self.course_b, self.academic_term, 9)
		for student in children:
			self._submit_result(plan_a, student, 30, 45)
			self._submit_result(plan_b, student, 25, 40)

		generate_report_cards(self.student_group, self.academic_term)
		for student in children:
			name = frappe.db.get_value("Report Card", {"student": student, "academic_term": self.academic_term})
			doc = frappe.get_doc("Report Card", name)
			doc = apply_workflow(doc, "Review")
			doc = apply_workflow(doc, "Approve")
			apply_workflow(doc, "Publish")

		guardian_user = self._ensure_portal_user(guardian_name, "Guardian")
		try:
			frappe.set_user(guardian_user)
			visible = frappe.get_list(
				"Report Card", filters={"academic_term": self.academic_term}, fields=["student"]
			)
		finally:
			frappe.set_user("Administrator")
		visible_students = {row.student for row in visible}
		self.assertEqual(visible_students, set(children), "Guardian must see all 3 linked children")

	def _ensure_portal_user(self, identity_name, role):
		doctype = "Guardian" if role == "Guardian" else "Student"
		field = "guardian_name" if role == "Guardian" else "student_name"
		record_name = frappe.db.get_value(doctype, {field: identity_name}, "name")
		email = f"{record_name}@example.edupro.test".replace(" ", "").lower()
		user_name = frappe.db.get_value(doctype, record_name, "user")
		if not user_name:
			if frappe.db.exists("User", email):
				user_name = email
			else:
				user = frappe.get_doc(
					{"doctype": "User", "email": email, "first_name": identity_name, "user_type": "Website User"}
				)
				user.append("roles", {"role": role})
				user.insert(ignore_permissions=True)
				user_name = user.name
			frappe.db.set_value(doctype, record_name, "user", user_name)
		return user_name

	# ------------------------------------------------------------------
	# TC-06 — Student portal: only sees own report
	# ------------------------------------------------------------------
	def test_tc06_student_portal_only_sees_own_report(self):
		from frappe.model.workflow import apply_workflow

		plan_a = self._make_plan(self.course_a, self.academic_term, 10)
		plan_b = self._make_plan(self.course_b, self.academic_term, 11)

		student_1 = self._make_student("tc06-a")
		student_2 = self._make_student("tc06-b")
		for student in (student_1, student_2):
			self._submit_result(plan_a, student, 30, 45)
			self._submit_result(plan_b, student, 25, 40)

		generate_report_cards(self.student_group, self.academic_term)
		for student in (student_1, student_2):
			name = frappe.db.get_value("Report Card", {"student": student, "academic_term": self.academic_term})
			doc = frappe.get_doc("Report Card", name)
			doc = apply_workflow(doc, "Review")
			doc = apply_workflow(doc, "Approve")
			apply_workflow(doc, "Publish")

		user_1 = self._ensure_portal_user(frappe.db.get_value("Student", student_1, "student_name"), "Student")
		own_card = frappe.get_doc("Report Card", frappe.db.get_value("Report Card", {"student": student_1}))
		other_card = frappe.get_doc("Report Card", frappe.db.get_value("Report Card", {"student": student_2}))

		self.assertTrue(has_permission(own_card, user_1, "read"))
		self.assertFalse(has_permission(other_card, user_1, "read"))

	# ------------------------------------------------------------------
	# TC-07 — PDF generation timing (scaled down; extrapolated)
	# ------------------------------------------------------------------
	def test_tc07_pdf_generation_timing(self):
		from frappe.utils.pdf import get_pdf

		plan_a = self._make_plan(self.course_a, self.academic_term, 12)
		plan_b = self._make_plan(self.course_b, self.academic_term, 13)
		students = [self._make_student(f"tc07-{i}") for i in range(3)]
		for student in students:
			self._submit_result(plan_a, student, 30, 45)
			self._submit_result(plan_b, student, 25, 40)
		generate_report_cards(self.student_group, self.academic_term)

		start = time.time()
		for student in students:
			name = frappe.db.get_value("Report Card", {"student": student, "academic_term": self.academic_term})
			html = frappe.get_print("Report Card", name, "IGCSE Report Card")
			get_pdf(html)
		elapsed = time.time() - start

		per_student = elapsed / len(students)
		self.assertLess(
			per_student, 5, f"PDF generation averaged {per_student:.2f}s/student, target is <5s (docs/08)"
		)

	# ------------------------------------------------------------------
	# TC-08 — Email delivery to multiple parents
	# ------------------------------------------------------------------
	def test_tc08_email_multiple_parents(self):
		from frappe.model.workflow import apply_workflow

		if not frappe.db.exists("Email Account", {"default_outgoing": 1}):
			self.skipTest("No outgoing Email Account configured (expected on a fresh site, see docs/06 §6.6)")

		plan_a = self._make_plan(self.course_a, self.academic_term, 14)
		plan_b = self._make_plan(self.course_b, self.academic_term, 15)
		student = self._make_student("tc08", guardian_name=f"{TEST_TAG} Guardian TC08")
		self._submit_result(plan_a, student, 30, 45)
		self._submit_result(plan_b, student, 25, 40)
		generate_report_cards(self.student_group, self.academic_term)

		name = frappe.db.get_value("Report Card", {"student": student, "academic_term": self.academic_term})
		doc = frappe.get_doc("Report Card", name)
		doc = apply_workflow(doc, "Review")
		doc = apply_workflow(doc, "Approve")
		apply_workflow(doc, "Publish")

		before = frappe.db.count("Email Queue", {"reference_name": name})
		send_report_card_emails(name)
		after = frappe.db.count("Email Queue", {"reference_name": name})
		self.assertGreater(after, before, "expected at least one Email Queue record for the guardian")
		self.assertIsNotNone(frappe.db.get_value("Report Card", name, "sent_to_parent_at"))

	# ------------------------------------------------------------------
	# TC-09 — Duplicate prevention
	# ------------------------------------------------------------------
	def test_tc09_duplicate_prevention(self):
		plan_a = self._make_plan(self.course_a, self.academic_term, 16)
		student = self._make_student("tc09")
		self._submit_result(plan_a, student, 30, 45)

		with self.assertRaises(frappe.exceptions.ValidationError):
			frappe.get_doc(
				{
					"doctype": "Assessment Result",
					"assessment_plan": plan_a.name,
					"student": student,
					"student_group": self.student_group,
					"details": [
						{"assessment_criteria": "Test", "score": 20},
						{"assessment_criteria": "Exam", "score": 30},
					],
				}
			).insert(ignore_permissions=True)

	# ------------------------------------------------------------------
	# TC-10 — Grade calculation matches Cambridge O Level boundaries exactly
	# ------------------------------------------------------------------
	def test_tc10_grade_calculation_boundaries(self):
		from edupro_sms.grading import get_grade_for_percentage

		cases = [
			(100, "A*/A"), (90, "A*/A"), (80, "A*/A"),
			(79.99, "B"), (70, "B"),
			(69.99, "C"), (60, "C"),
			(59.99, "D"), (50, "D"),
			(49.99, "E"), (40, "E"),
			(39.99, "Ungraded"), (0, "Ungraded"),
		]
		for percentage, expected_grade in cases:
			self.assertEqual(
				get_grade_for_percentage("Cambridge O Level", percentage),
				expected_grade,
				f"{percentage}% should be grade {expected_grade}",
			)

	# ------------------------------------------------------------------
	# TC-11 — Class position with ties
	# ------------------------------------------------------------------
	def test_tc11_position_calculation_with_ties(self):
		# Position is ranked across every Report Card sharing this exact
		# student_group + academic_term. FrappeTestCase does not appear to
		# roll back data between test *methods* within this run (only
		# setUp's explicit cleanup keeps Report Card names from colliding),
		# so ranking-sensitive assertions need their own isolated group --
		# otherwise other tests' students in the shared self.student_group
		# would shift the expected ranks.
		isolated_group = self._ensure("Student Group", f"{TEST_TAG} Group TC11", {
			"student_group_name": f"{TEST_TAG} Group TC11",
			"group_based_on": "Batch",
			"academic_year": self.academic_year,
			"academic_term": self.academic_term,
			"program": self.program,
			"max_strength": 40,
		})

		plan_a = self._make_plan(self.course_a, self.academic_term, 17, student_group=isolated_group)
		plan_b = self._make_plan(self.course_b, self.academic_term, 18, student_group=isolated_group)

		# 4 students: two tied for 1st (90%), one 3rd (70%), one 4th (50%)
		scores = [("tc11-a", 36, 54), ("tc11-b", 36, 54), ("tc11-c", 28, 42), ("tc11-d", 20, 30)]
		students = {}
		for suffix, test, exam in scores:
			student = self._make_student(suffix, student_group=isolated_group)
			students[suffix] = student
			self._submit_result(plan_a, student, test, exam, student_group=isolated_group)
			self._submit_result(plan_b, student, test, exam, student_group=isolated_group)

		generate_report_cards(isolated_group, self.academic_term)

		positions = {}
		for suffix, student in students.items():
			name = frappe.db.get_value("Report Card", {"student": student, "academic_term": self.academic_term})
			positions[suffix] = frappe.db.get_value("Report Card", name, "position")

		self.assertEqual(positions["tc11-a"], 1)
		self.assertEqual(positions["tc11-b"], 1, "tied students must share rank 1")
		self.assertEqual(positions["tc11-c"], 3, "next distinct rank must skip to 3, not 2")
		self.assertEqual(positions["tc11-d"], 4)

	# ------------------------------------------------------------------
	# TC-12 — Historical term view
	# ------------------------------------------------------------------
	def test_tc12_historical_term_view(self):
		# Student Group.academic_term locks every Assessment Plan under it
		# to that one term (fetch_from, see DECISIONS.md 0008/0009) -- so
		# "the same class in a later term" needs its own Student Group.
		# The point of this test is that a student's Term 1 results stay
		# fully intact and queryable once Term 2 data exists alongside it.
		plan_term1 = self._make_plan(self.course_a, self.academic_term, 19)
		plan_term2 = self._make_plan(self.course_a, self.term_2, 20, student_group=self.student_group_term2)

		student = self._make_student("tc12")
		self._make_student_in_group(student, self.student_group_term2)

		frappe.get_doc(
			{
				"doctype": "Assessment Result",
				"assessment_plan": plan_term1.name,
				"student": student,
				"student_group": self.student_group,
				"details": [{"assessment_criteria": "Test", "score": 30}, {"assessment_criteria": "Exam", "score": 45}],
			}
		).insert(ignore_permissions=True).submit()

		frappe.get_doc(
			{
				"doctype": "Assessment Result",
				"assessment_plan": plan_term2.name,
				"student": student,
				"student_group": self.student_group_term2,
				"details": [{"assessment_criteria": "Test", "score": 32}, {"assessment_criteria": "Exam", "score": 48}],
			}
		).insert(ignore_permissions=True).submit()

		term1_results = frappe.get_all(
			"Assessment Result", filters={"student": student, "academic_term": self.academic_term}
		)
		term2_results = frappe.get_all(
			"Assessment Result", filters={"student": student, "academic_term": self.term_2}
		)
		self.assertEqual(len(term1_results), 1, "Term 1 result must remain accessible after Term 2 data exists")
		self.assertEqual(len(term2_results), 1)
