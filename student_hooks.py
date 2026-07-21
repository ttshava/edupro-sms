import frappe


def ensure_student_role(doc, method=None):
	"""Education's own Student.validate_user() calls User.add_roles("Student")
	on a brand-new, not-yet-inserted User document, then saves it -- the role
	never actually persists (add_roles() expects an existing saved doc). Core
	Education code, can't edit it directly, so this after_insert hook re-checks
	and assigns the role once the linked User definitely exists."""
	if not doc.student_email_id or not frappe.db.exists("User", doc.student_email_id):
		return

	user = frappe.get_doc("User", doc.student_email_id)
	if not any(r.role == "Student" for r in user.roles):
		user.append("roles", {"role": "Student"})
		user.save(ignore_permissions=True)
