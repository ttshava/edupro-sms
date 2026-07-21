import frappe

from edupro_sms.edupro_sms.fees import BOARDING_FEE


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/bursar-reports"
		raise frappe.Redirect

	roles = set(frappe.get_roles())
	if not (roles & {"Bursar", "Headmaster", "System Manager"}):
		frappe.throw("You are not permitted to view this page.", frappe.PermissionError)

	context.no_cache = 1
	context.academic_terms = frappe.get_all("Academic Term", fields=["name"], order_by="term_start_date desc")
	context.boarding_types = list(BOARDING_FEE.keys())
	context.csrf_token = frappe.sessions.get_csrf_token()
	context.title = "Reports"
	context.active_nav = "reports"
