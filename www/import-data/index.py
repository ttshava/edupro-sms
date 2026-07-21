"""
Import Data Page Context Handler

Bulk CSV/Excel import for Students, Instructors, Guardians, Assessment Plans.

URL: /import-data/
"""

import frappe
from frappe import _


def get_context(context):
    """Get context for the import-data page"""

    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/import-data"
        raise frappe.Redirect

    roles = set(frappe.get_roles())
    if not (roles & {"Bursar", "Headmaster", "System Manager"}):
        frappe.throw(_("You are not permitted to view this page."), frappe.PermissionError)

    context.no_cache = 1
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.title = "Bulk Data Import"
    context.active_nav = "students"

    return context
