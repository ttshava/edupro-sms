"""Keep the public-facing branding (login page, portal footer) in sync
with School Settings. Each site is one school, so Website Settings has
no other configured use for app_name/app_logo/copyright -- wired via
hooks.py doc_events on School Settings.
"""

import frappe


def sync_website_branding(doc, method=None):
	logo_url = doc.logo
	if logo_url:
		logo_file = frappe.db.get_value("File", {"file_url": logo_url}, ["name", "is_private"], as_dict=True)
		if logo_file and logo_file.is_private:
			file_doc = frappe.get_doc("File", logo_file.name)
			file_doc.is_private = 0
			file_doc.save(ignore_permissions=True)
			logo_url = file_doc.file_url

	ws = frappe.get_single("Website Settings")
	ws.app_name = doc.school_name
	ws.app_logo = logo_url
	ws.copyright = doc.motto
	ws.show_footer_on_login = 1
	ws.save(ignore_permissions=True)
