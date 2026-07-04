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


def get_pending_report_cards(student_group: str | None = None):
	if not _is_headmaster():
		return []
	filters = {"workflow_state": ["in", ["Reviewed", "Approved"]]}
	if student_group:
		filters["student_group"] = student_group
	return frappe.get_list(
		"Report Card",
		filters=filters,
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


# Which workflow_state a Report Card must already be in for each bulk
# class-level action to apply to it -- mirrors the Report Card Approval
# workflow's own transitions (Reviewed->Approve/Reject, Approved->Publish).
_FROM_STATE_FOR_ACTION = {"Approve": "Reviewed", "Reject": "Reviewed", "Publish": "Approved"}


@frappe.whitelist()
def apply_class_report_card_action(student_group, academic_term, action):
	"""Bulk version of apply_report_card_action for the headmaster's
	class-level review screens -- loops the same per-document
	apply_workflow call over every Report Card in that class+term
	that's currently in the right state for the action, rather than
	introducing any new workflow/state machine."""
	if not _is_headmaster():
		frappe.throw(_("You are not permitted to review report cards."), frappe.PermissionError)
	if action not in ALLOWED_ACTIONS:
		frappe.throw(_("Unknown action: {0}").format(action))

	from_state = _FROM_STATE_FOR_ACTION[action]
	names = frappe.get_all(
		"Report Card",
		filters={
			"student_group": student_group,
			"academic_term": academic_term,
			"workflow_state": from_state,
			"docstatus": ["!=", 2],
		},
		pluck="name",
	)

	succeeded, failed = 0, []
	for name in names:
		try:
			doc = frappe.get_doc("Report Card", name)
			apply_workflow(doc, action)
			succeeded += 1
		except Exception:
			failed.append(name)

	return {"succeeded": succeeded, "failed": failed, "total": len(names)}
