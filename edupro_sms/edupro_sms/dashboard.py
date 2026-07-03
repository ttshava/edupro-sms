"""Land Headmaster/Instructor on our own website dashboard (/dashboard)
after login, with no Desk access at all -- wired via hooks.py
add_to_apps_screen + a User validate hook that keeps default_app and
user_type in sync with role. See .claude/DECISIONS.md 0013/0014 for why
this needs add_to_apps_screen rather than role_home_page (Frappe's
login flow only consults role_home_page for Website Users) and for the
history: Desk access was deliberately kept at first so marks entry/
report approval could keep working via Desk, then removed once
/marks-entry and the dashboard's approve/reject/publish actions were
built and verified as full Desk replacements, not before.
"""

import frappe

DASHBOARD_ROLES = {"Headmaster", "Instructor"}


def has_dashboard_access() -> bool:
	return bool(set(frappe.get_roles()) & DASHBOARD_ROLES)


def sync_dashboard_default_app(doc, method=None):
	role_names = {row.role for row in doc.roles}
	if role_names & DASHBOARD_ROLES:
		doc.default_app = "edupro_sms"
		doc.user_type = "Website User"
