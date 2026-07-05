"""
Student Portal Dashboard

URL: /my-student-dashboard/
"""

import frappe
from frappe import _


def get_context(context):
    """Load context for student dashboard."""

    # Permission check - must be logged in as a student
    user = frappe.session.user
    if user == 'Guest':
        raise frappe.PermissionError(_("Please log in to access student dashboard"))

    student_id = frappe.db.get_value('Student', filters={'user_id': user}, pluck='name')
    if not student_id:
        raise frappe.PermissionError(_("You are not registered as a student"))

    context.student_id = student_id
    context.user_name = frappe.session.user

    return context
