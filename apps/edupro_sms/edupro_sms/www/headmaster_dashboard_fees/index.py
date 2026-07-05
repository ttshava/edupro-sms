"""
Headmaster Fee Dashboard

Displays financial overview:
- Total billed, collected, outstanding, collection %
- Charts: by program, by status, collection trend
- Unpaid students list

URL: /headmaster-dashboard/fees/
"""

import frappe
from frappe import _


def get_context(context):
    """Load context for fee dashboard."""

    if frappe.session.user == 'Guest':
        raise frappe.PermissionError(_("Please log in"))

    # Get active academic terms
    academic_terms = frappe.db.get_list(
        'Academic Term',
        filters={'is_active': 1},
        fields=['name'],
        order_by='start_date desc'
    )

    # Get all programs
    programs = frappe.db.get_list(
        'Program',
        fields=['name'],
        order_by='name asc'
    )

    context.academic_terms = academic_terms
    context.programs = programs

    return context
