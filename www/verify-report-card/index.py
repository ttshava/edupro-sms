import frappe


def get_context(context):
	context.no_cache = 1
	context.title = "Verify Report Card"

	code = frappe.form_dict.get("code")
	context.code = code
	context.result = _lookup(code) if code else None


def _lookup(code):
	name = frappe.db.get_value(
		"Report Card", {"verification_code": code, "workflow_state": "Published"}, "name"
	)
	if not name:
		return None

	card = frappe.get_doc("Report Card", name)
	return {
		"student_name": card.student_name,
		"student_group": card.student_group,
		"academic_term": card.academic_term,
		"academic_year": card.academic_year,
		"overall_grade": card.overall_grade,
		"average_percentage": card.average_percentage,
		"school_name": frappe.db.get_single_value("School Settings", "school_name"),
	}
