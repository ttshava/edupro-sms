"""Website approve/reject/publish for Headmasters -- drives the
existing Report Card Approval workflow (see fixtures/workflow.json)
via frappe.model.workflow.apply_workflow, the same call Desk's
workflow buttons make, instead of reimplementing the state machine.
"""

import frappe
from frappe import _
from frappe.model.workflow import apply_workflow

ALLOWED_ACTIONS = {"Approve", "Reject", "Publish"}


def _is_headmaster(user=None) -> bool:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	return bool(roles & {"Headmaster", "System Manager"})


def get_pending_report_cards():
	if not _is_headmaster():
		return []
	return frappe.get_list(
		"Report Card",
		filters={"workflow_state": ["in", ["Reviewed", "Approved"]]},
		fields=["name", "student_name", "student_group", "academic_term", "workflow_state"],
		order_by="modified desc",
	)


@frappe.whitelist()
def apply_report_card_action(name, action):
	if not _is_headmaster():
		frappe.throw(_("You are not permitted to review report cards."), frappe.PermissionError)
	if action not in ALLOWED_ACTIONS:
		frappe.throw(_("Unknown action: {0}").format(action))

	doc = frappe.get_doc("Report Card", name)
	apply_workflow(doc, action)
	return {"workflow_state": doc.workflow_state}
