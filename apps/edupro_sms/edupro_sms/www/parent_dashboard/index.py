"""
Parent/Guardian Portal Dashboard

URL: /my-parent-dashboard/
"""

import frappe
from frappe import _


def get_context(context):
    """Load context for parent dashboard."""

    user = frappe.session.user
    if user == 'Guest':
        raise frappe.PermissionError(_("Please log in to access parent dashboard"))

    guardian = frappe.db.get_value('Guardian', filters={'email': user}, pluck='name')
    if not guardian:
        raise frappe.PermissionError(_("You are not registered as a guardian"))

    context.guardian_id = guardian
    context.user_name = frappe.session.user

    return context
