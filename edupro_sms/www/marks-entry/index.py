import frappe
from frappe import _

from marks_entry import get_entry_data


def get_context(context):
	if frappe.session.user == "Guest":
		redirect_to = frappe.utils.quote(frappe.local.request.full_path)
		frappe.local.flags.redirect_location = f"/login?redirect-to={redirect_to}"
		raise frappe.Redirect

	plan_name = frappe.form_dict.get("plan")
	if not plan_name:
		frappe.throw(_("Missing assessment plan."), frappe.DoesNotExistError)

	context.no_cache = 1
	context.data = get_entry_data(plan_name)
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = "Enter Marks"
