"""Force "setup complete" for every session, regardless of what
Frappe/ERPNext's own setup-wizard gating computes.

Edupro SMS deliberately doesn't use ERPNext's Company/fiscal-year setup
(see docs/02_Database.md §2.2, .claude/DECISIONS.md 0004/0011) — we
config the school via our own School Settings doctype instead. ERPNext's
own gate (Installed Application.is_setup_complete, recomputed against
whether a Company exists) turned out to still redirect to the wizard in
some flows even after both the flag and a real Company record were in
place — rather than keep chasing the exact trigger, this hook has the
last word on every boot: it always tells the client setup is done.
"""

import frappe


def boot_session(bootinfo):
	bootinfo.sysdefaults["setup_complete"] = 1

	all_apps = frappe.get_installed_apps()
	bootinfo.setup_wizard_completed_apps = list(all_apps)
