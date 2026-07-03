"""Land Headmaster/Instructor on our own website dashboard (/dashboard)
after login instead of Desk, while leaving them full Desk access for
actual work (marks entry, report card approval) -- wired via hooks.py
add_to_apps_screen + a User validate hook that keeps default_app in
sync with role. See .claude/DECISIONS.md for why this needs
add_to_apps_screen rather than role_home_page: Frappe's login flow only
consults role_home_page for Website Users: for System Users (which
Headmaster/Instructor stay, so Desk keeps working) it always redirects
to the user's default_app route instead.
"""

import frappe

DASHBOARD_ROLES = {"Headmaster", "Instructor"}


def has_dashboard_access() -> bool:
	return bool(set(frappe.get_roles()) & DASHBOARD_ROLES)


def sync_dashboard_default_app(doc, method=None):
	role_names = {row.role for row in doc.roles}
	if role_names & DASHBOARD_ROLES:
		doc.default_app = "edupro_sms"
