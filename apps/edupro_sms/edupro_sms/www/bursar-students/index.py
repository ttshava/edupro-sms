"""
Bursar Student Management Portal — Main Page

Shows list of students with search, filter, pagination.
Allows Bursar to:
- Search/filter students
- Enroll in program
- Link guardian
- Edit/deactivate

URL: /bursar-students/
"""

import frappe
from frappe import _


def get_context(context):
    """Get context for bursar-students main page"""

    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/bursar-students"
        raise frappe.Redirect

    roles = set(frappe.get_roles())
    if not (roles & {"Bursar", "Headmaster", "System Manager"}):
        frappe.throw(_("You are not permitted to view this page."), frappe.PermissionError)

    # Program/Student Group read access doesn't include Bursar by default;
    # our own role check above already gates the page.
    programs = frappe.db.get_list('Program', fields=['name'], order_by='name asc', ignore_permissions=True)
    student_groups = frappe.db.get_list('Student Group', fields=['name'], order_by='name asc', ignore_permissions=True)
    guardians = frappe.db.get_list(
        'Guardian', fields=['name', 'guardian_name'], order_by='guardian_name asc', ignore_permissions=True
    )

    context.no_cache = 1
    context.programs = programs
    context.student_groups = student_groups
    context.guardians = guardians
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.title = "Bursar: Students"
    context.active_nav = "students"

    return context
