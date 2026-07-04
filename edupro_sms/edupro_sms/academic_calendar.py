"""Shared "what term is it right now" helper -- used by both the
teacher dashboard summary bar and the parent/student dashboard, so
"Current Term" always means the same thing everywhere."""

import frappe


def get_current_term() -> str | None:
	today = frappe.utils.today()
	term = frappe.db.get_value(
		"Academic Term", {"term_start_date": ["<=", today], "term_end_date": [">=", today]}, "name"
	)
	if not term:
		# Between terms (holidays) -- fall back to the most recently started one.
		term = frappe.db.get_value(
			"Academic Term", {"term_start_date": ["<=", today]}, "name", order_by="term_start_date desc"
		)
	return term
