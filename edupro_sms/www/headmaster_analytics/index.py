"""
Headmaster Analytics Dashboard

URL: /headmaster-analytics/
"""

import frappe
from frappe import _


def get_context(context):
    """Load context for analytics dashboard."""

    if frappe.session.user == 'Guest':
        raise frappe.PermissionError(_("Please log in"))

    # Get academic years
    academic_years = frappe.db.get_list(
        'Academic Year',
        fields=['name'],
        order_by='name desc'
    )

    # Get programs
    programs = frappe.db.get_list(
        'Program',
        fields=['name'],
        order_by='name asc'
    )

    context.academic_years = academic_years
    context.programs = programs

    return context
