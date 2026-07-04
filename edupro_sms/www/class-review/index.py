import frappe
from frappe import _


def get_context(context):
	if frappe.session.user == "Guest":
		redirect_to = frappe.utils.quote(frappe.local.request.full_path)
		frappe.local.flags.redirect_location = f"/login?redirect-to={redirect_to}"
		raise frappe.Redirect

	roles = set(frappe.get_roles())
	if not (roles & {"Headmaster", "System Manager"}):
		frappe.throw(_("You are not permitted to review classes."), frappe.PermissionError)

	student_group = frappe.form_dict.get("group")
	if not student_group:
		frappe.throw(_("Missing class."), frappe.DoesNotExistError)

	from edupro_sms.edupro_sms.approvals import get_pending_report_cards
	from edupro_sms.edupro_sms.class_review import get_class_review

	context.no_cache = 1
	context.review = get_class_review(student_group)
	context.pending_report_cards = get_pending_report_cards(student_group)
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = f"Class Review - {student_group}"
