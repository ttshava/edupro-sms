"""Removes everything the QA strain-test script may have created, in
dependency order, so a failed/partial run can be retried cleanly.
Safe to run even if nothing exists yet."""

import frappe


def run():
	deleted = {"assessment_results": 0, "assessment_plans": 0, "report_cards": 0, "student_fees": 0, "ledger_entries": 0}

	groups = frappe.get_all("Student Group", filters={"name": ["like", "QA Strain%"]}, pluck="name")

	for name in frappe.get_all("Report Card", filters={"student_group": ["in", groups or [""]]}, pluck="name"):
		doc = frappe.get_doc("Report Card", name)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Report Card", name, force=True, ignore_permissions=True)
		deleted["report_cards"] += 1

	for name in frappe.get_all("Assessment Result", filters={"student_group": ["in", groups or [""]]}, pluck="name"):
		doc = frappe.get_doc("Assessment Result", name)
		if doc.docstatus == 1:
			doc.flags.ignore_permissions = True
			doc.cancel()
		frappe.delete_doc("Assessment Result", name, force=True, ignore_permissions=True)
		deleted["assessment_results"] += 1

	for name in frappe.get_all("Assessment Plan", filters={"student_group": ["in", groups or [""]]}, pluck="name"):
		frappe.delete_doc("Assessment Plan", name, force=True, ignore_permissions=True)
		deleted["assessment_plans"] += 1

	students = frappe.get_all("Student", filters={"student_email_id": ["like", "qa.%@example.edupro.test"]}, pluck="name")
	for s in students:
		for sf in frappe.get_all("Student Fee", filters={"student": s}, pluck="name"):
			frappe.delete_doc("Student Fee", sf, force=True, ignore_permissions=True)
			deleted["student_fees"] += 1
		for le in frappe.get_all("Student Ledger Entry", filters={"student": s}, pluck="name"):
			frappe.delete_doc("Student Ledger Entry", le, force=True, ignore_permissions=True)
			deleted["ledger_entries"] += 1
		frappe.delete_doc("Student", s, force=True, ignore_permissions=True)

	guardians = frappe.get_all("Guardian", filters={"email_address": ["like", "qa.%@example.edupro.test"]}, pluck="name")
	for g in guardians:
		frappe.delete_doc("Guardian", g, force=True, ignore_permissions=True)

	users = frappe.get_all("User", filters={"name": ["like", "qa.%@example.edupro.test"]}, pluck="name")
	for u in users:
		frappe.delete_doc("User", u, force=True, ignore_permissions=True)

	for name in groups:
		frappe.delete_doc("Student Group", name, force=True, ignore_permissions=True)

	if frappe.db.exists("Program", "QA Strain Program"):
		frappe.delete_doc("Program", "QA Strain Program", force=True, ignore_permissions=True)

	# Education auto-creates a Customer per Student (named off the
	# student's full name) that isn't cleaned up when the Student is
	# deleted -- without removing these too, a retry with the same fixed
	# small-class names collides on the leftover Customer record.
	small_class_names = [
		"Grace O'Brian-Chikafu", "Method Zero Dube", "Nyasha Dube", "NoGuardian Studentson",
		"Partial Marks Moyo", "Longname Comment Testfield Mukamuri-Nyandoro the Third",
	]
	for name in small_class_names:
		if frappe.db.exists("Customer", name):
			frappe.delete_doc("Customer", name, force=True, ignore_permissions=True)
	deleted["customers"] = 0
	for name in frappe.get_all("Customer", filters={"customer_group": "Student"}, pluck="name"):
		if not frappe.db.exists("Student", {"student_name": name}):
			frappe.delete_doc("Customer", name, force=True, ignore_permissions=True)
			deleted["customers"] += 1

	for name in ["QA Teacher Alpha", "QA Teacher Beta", "QA Teacher Gamma", "QA Teacher Delta (unassigned)"]:
		if frappe.db.exists("Instructor", name):
			frappe.delete_doc("Instructor", name, force=True, ignore_permissions=True)
	for email in [
		"qa.teacher.alpha@example.edupro.test",
		"qa.teacher.beta@example.edupro.test",
		"qa.teacher.gamma@example.edupro.test",
		"qa.teacher.delta@example.edupro.test",
	]:
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)

	frappe.db.commit()
	print("deleted:", deleted)
	print("students:", len(students), "guardians:", len(guardians), "users:", len(users), "groups:", len(groups))
	print("DONE")
