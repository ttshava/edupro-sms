"""
Bursar Fee Entry Portal

Allows Bursar to:
1. View all student fees
2. Search/filter by student, boarding type, status, term
3. Edit fee amounts
4. Record payments
5. View fee statements

URL: /bursar_fees/
"""

import frappe
from frappe import _

from fees import BOARDING_FEE


def get_context(context):
    """Load context for fee entry portal."""

    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/bursar_fees"
        raise frappe.Redirect

    roles = set(frappe.get_roles())
    if not (roles & {"Bursar", "Headmaster", "System Manager"}):
        frappe.throw(_("You are not permitted to view this page."), frappe.PermissionError)

    # Academic Term read access is restricted to a handful of roles
    # (Academics User, Instructor, Student, Guardian) that don't include
    # Bursar/Headmaster -- this is a harmless reference-data dropdown and
    # our own role check above already gates the page, so bypass here.
    academic_terms = frappe.db.get_list(
        'Academic Term',
        fields=['name'],
        order_by='term_start_date desc',
        ignore_permissions=True
    )

    context.no_cache = 1
    context.boarding_types = list(BOARDING_FEE.keys())
    context.academic_terms = academic_terms
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.title = "Bursar: Fees"
    context.active_nav = "fees"

    return context
