import frappe
from frappe import _


def get_context(context):
	if frappe.session.user == "Guest":
		redirect_to = frappe.utils.quote(frappe.local.request.full_path)
		frappe.local.flags.redirect_location = f"/login?redirect-to={redirect_to}"
		raise frappe.Redirect

	student_group = frappe.form_dict.get("group")
	if not student_group:
		frappe.throw(_("Missing class."), frappe.DoesNotExistError)

	from edupro_sms.approvals import _is_class_teacher_of, _is_headmaster, get_pending_report_cards
	from edupro_sms.class_review import get_class_review

	is_headmaster = _is_headmaster()
	is_class_teacher = _is_class_teacher_of(student_group)
	if not (is_headmaster or is_class_teacher):
		frappe.throw(_("You are not permitted to review this class."), frappe.PermissionError)

	context.no_cache = 1
	context.review = get_class_review(student_group)
	context.pending_report_cards = get_pending_report_cards(student_group) if is_headmaster else []
	context.is_headmaster = is_headmaster
	context.is_class_teacher = is_class_teacher
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = f"Class Review - {student_group}"
