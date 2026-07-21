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


def get_next_term_start(academic_term: str | None) -> str | None:
	"""The start date of whichever Academic Term begins right after the
	given one -- for the Report Card's "Next Term Begins" line. Purely a
	print-time convenience; no new data, just the next row by start date."""
	if not academic_term:
		return None
	this_start = frappe.db.get_value("Academic Term", academic_term, "term_start_date")
	if not this_start:
		return None
	next_start = frappe.db.get_value(
		"Academic Term", {"term_start_date": [">", this_start]}, "term_start_date", order_by="term_start_date asc"
	)
	return str(next_start) if next_start else None
