"""
Headmaster Batch Print Page

Allows Headmaster to:
1. Select criteria (class/group, term, status)
2. Preview how many reports will be printed
3. Generate merged PDF
4. Download PDF

URL: /headmaster-batch-print/
"""

import frappe
from frappe import _


def get_context(context):
    """Load context for batch print page."""

    if frappe.session.user == 'Guest':
        raise frappe.PermissionError(_("Please log in"))

    # Get student groups
    student_groups = frappe.db.get_list(
        'Student Group',
        fields=['name'],
        order_by='name asc'
    )

    # Get academic terms
    academic_terms = frappe.db.get_list(
        'Academic Term',
        filters={'is_active': 1},
        fields=['name'],
        order_by='start_date desc'
    )

    context.student_groups = student_groups
    context.academic_terms = academic_terms

    return context
