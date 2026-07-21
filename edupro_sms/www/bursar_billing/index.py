"""
Bursar Batch Billing Page

Allows Bursar to:
1. Select Academic Term
2. Optionally filter by Boarding Type
3. Preview how many students will be billed
4. Confirm and execute batch billing

URL: /bursar_billing/
"""

import frappe
from frappe import _

from edupro_sms.fees import BOARDING_FEE


def get_context(context):
    """Load context for batch billing page."""

    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/bursar_billing"
        raise frappe.Redirect

    roles = set(frappe.get_roles())
    if not (roles & {"Bursar", "Headmaster", "System Manager"}):
        frappe.throw(_("You are not permitted to view this page."), frappe.PermissionError)

    academic_terms = frappe.db.get_list(
        'Academic Term',
        fields=['name'],
        order_by='term_start_date desc',
        ignore_permissions=True
    )

    context.no_cache = 1
    context.academic_terms = academic_terms
    context.boarding_types = list(BOARDING_FEE.keys())
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.title = "Bursar: Billing"
    context.active_nav = "billing"

    return context
