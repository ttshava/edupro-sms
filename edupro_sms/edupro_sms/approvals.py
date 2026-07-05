"""Website approve/reject/publish for Headmasters, and review for Class
Teachers -- drives the existing Report Card Approval workflow (see
fixtures/workflow.json) via frappe.model.workflow.apply_workflow, the
same call Desk's workflow buttons make, instead of reimplementing the
state machine.

Review (Pending Approval -> Reviewed) is the Class Teacher's own step
in that workflow, distinct from the Headmaster's Approve/Reject/Publish
-- both need a website entry point since Desk access was removed for
both roles (see DECISIONS.md 0014).
"""

import frappe
from frappe import _
from frappe.model.workflow import apply_workflow

ALLOWED_ACTIONS = {"Review", "Approve", "Reject", "Publish"}


def _is_headmaster(user=None) -> bool:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	return bool(roles & {"Headmaster", "System Manager"})


def _is_class_teacher_of(student_group, user=None) -> bool:
	user = user or frappe.session.user
	roles = set(frappe.get_roles(user))
	if "Class Teacher" not in roles:
		return False
	instructor = frappe.db.get_value("Instructor", {"user": user}, "name")
	if not instructor:
		return False
	return frappe.db.get_value("Student Group", student_group, "class_teacher") == instructor


def _can_perform(action, student_group, user=None) -> bool:
	if _is_headmaster(user):
		return True
	if action == "Review":
		return _is_class_teacher_of(student_group, user)
	return False


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


_COMMENT_FIELD_RULES = {
	# field -> (who may edit it, which workflow_state(s) it's editable in)
	"class_teacher_comment": {"Pending Approval", "Reviewed"},
	"headmaster_comment": {"Reviewed", "Approved"},
}


@frappe.whitelist()
def save_report_card_comment(report_card_name: str, field: str, value: str) -> dict:
	"""Class Teacher writes class_teacher_comment during their Review
	step; Headmaster writes headmaster_comment during Approve/Publish --
	both fields already print on the Report Card PDF but previously had
	no portal input anywhere, only Desk (which these roles don't have)."""
	if field not in _COMMENT_FIELD_RULES:
		frappe.throw(_("Invalid field."))

	doc = frappe.get_doc("Report Card", report_card_name)

	if field == "class_teacher_comment":
		allowed = _is_headmaster() or _is_class_teacher_of(doc.student_group)
	else:
		allowed = _is_headmaster()

	if not allowed:
		frappe.throw(_("You are not permitted to edit this comment."), frappe.PermissionError)

	if doc.workflow_state not in _COMMENT_FIELD_RULES[field]:
		frappe.throw(_("This report card is not currently in a state where that comment can be edited."))

	frappe.db.set_value("Report Card", report_card_name, field, value)
	frappe.db.commit()
	return {"report_card": report_card_name, "field": field, "value": value}


@frappe.whitelist()
def apply_report_card_action(name, action):
	if action not in ALLOWED_ACTIONS:
		frappe.throw(_("Unknown action: {0}").format(action))

	doc = frappe.get_doc("Report Card", name)
	if not _can_perform(action, doc.student_group):
		frappe.throw(_("You are not permitted to {0} this report card.").format(action.lower()), frappe.PermissionError)
	apply_workflow(doc, action)
	return {"workflow_state": doc.workflow_state}


# Which workflow_state a Report Card must already be in for each bulk
# class-level action to apply to it -- mirrors the Report Card Approval
# workflow's own transitions (Pending Approval->Review, Reviewed->
# Approve/Reject, Approved->Publish).
_FROM_STATE_FOR_ACTION = {
	"Review": "Pending Approval",
	"Approve": "Reviewed",
	"Reject": "Reviewed",
	"Publish": "Approved",
}


@frappe.whitelist()
def apply_class_report_card_action(student_group, academic_term, action):
	"""Bulk version of apply_report_card_action for the headmaster's and
	class teacher's class-level review screens -- loops the same
	per-document apply_workflow call over every Report Card in that
	class+term that's currently in the right state for the action,
	rather than introducing any new workflow/state machine."""
	if action not in ALLOWED_ACTIONS:
		frappe.throw(_("Unknown action: {0}").format(action))
	if not _can_perform(action, student_group):
		frappe.throw(_("You are not permitted to {0} report cards for this class.").format(action.lower()), frappe.PermissionError)

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
