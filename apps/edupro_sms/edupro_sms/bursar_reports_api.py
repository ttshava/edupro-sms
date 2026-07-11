"""Bursar-facing finance reports -- read-only aggregations over the same
Student Fee / Student Ledger Entry data fees.py already maintains, no
new doctypes. Three reports: fee collection (billed vs collected, by
class), outstanding balances (who owes what, for chasing payment), and
payment history (every payment recorded, an audit trail)."""

import frappe
from frappe import _
from frappe.utils import flt


def _is_bursar_or_above(user: str | None = None) -> bool:
	roles = set(frappe.get_roles(user))
	return bool(roles & {"System Manager", "Headmaster", "Bursar"})


def _require_bursar():
	if not _is_bursar_or_above():
		frappe.throw(_("You are not permitted to view fee reports."), frappe.PermissionError)


@frappe.whitelist()
def get_fee_collection_summary(academic_term: str | None = None) -> dict:
	"""Billed / collected / outstanding, whole-school and broken down by
	class -- the "how much have we collected" report. Scoped to one term
	when given, otherwise every Student Fee ever billed."""
	_require_bursar()

	filters = {}
	if academic_term:
		filters["academic_term"] = academic_term

	rows = frappe.get_all(
		"Student Fee",
		filters=filters,
		fields=["student", "academic_term", "amount", "amount_paid", "balance"],
	)

	groups = {
		row.student: row.parent
		for row in frappe.get_all("Student Group Student", filters={"active": 1}, fields=["student", "parent"])
	}

	by_class = {}
	total_billed = total_paid = total_balance = 0.0
	for r in rows:
		total_billed += flt(r.amount)
		total_paid += flt(r.amount_paid)
		total_balance += flt(r.balance)

		group = groups.get(r.student) or "Unassigned"
		c = by_class.setdefault(group, {"billed": 0.0, "paid": 0.0, "balance": 0.0, "student_count": 0})
		c["billed"] += flt(r.amount)
		c["paid"] += flt(r.amount_paid)
		c["balance"] += flt(r.balance)
		c["student_count"] += 1

	class_rows = [{"student_group": g, **v} for g, v in by_class.items()]
	class_rows.sort(key=lambda r: r["student_group"])

	collection_rate = round((total_paid / total_billed) * 100, 1) if total_billed else 0

	return {
		"academic_term": academic_term,
		"total_billed": total_billed,
		"total_paid": total_paid,
		"total_balance": total_balance,
		"collection_rate": collection_rate,
		"by_class": class_rows,
	}


@frappe.whitelist()
def get_outstanding_balances(min_balance: float = 0.01) -> dict:
	"""Every student with money owing, worst offenders first -- the
	debtors list for chasing payment. One row per (student, term) with
	an outstanding balance, not collapsed per-student, since a parent
	may owe on one term but be clear on another."""
	_require_bursar()

	rows = frappe.get_all(
		"Student Fee",
		filters={"balance": [">", min_balance]},
		fields=["student", "student_name", "academic_term", "amount", "amount_paid", "balance", "due_date", "boarding_type"],
		order_by="balance desc",
	)

	groups = {
		row.student: row.parent
		for row in frappe.get_all("Student Group Student", filters={"active": 1}, fields=["student", "parent"])
	}

	guardian_contacts = {}
	guardian_links = frappe.get_all(
		"Student Guardian",
		filters={"parent": ["in", [r.student for r in rows]], "parenttype": "Student"},
		fields=["parent", "guardian"],
	) if rows else []
	guardian_ids = {g.guardian for g in guardian_links}
	guardian_info = {
		g.name: g
		for g in frappe.get_all("Guardian", filters={"name": ["in", list(guardian_ids)]}, fields=["name", "guardian_name", "email_address", "mobile_number"])
	} if guardian_ids else {}
	for g in guardian_links:
		if g.parent not in guardian_contacts:
			info = guardian_info.get(g.guardian)
			if info:
				guardian_contacts[g.parent] = {
					"guardian_name": info.guardian_name,
					"email": info.email_address,
					"phone": info.mobile_number,
				}

	out = []
	total_outstanding = 0.0
	for r in rows:
		total_outstanding += flt(r.balance)
		contact = guardian_contacts.get(r.student, {})
		out.append(
			{
				"student": r.student,
				"student_name": r.student_name,
				"student_group": groups.get(r.student) or "Unassigned",
				"boarding_type": r.boarding_type,
				"academic_term": r.academic_term,
				"amount": r.amount,
				"amount_paid": r.amount_paid,
				"balance": r.balance,
				"due_date": r.due_date,
				"guardian_name": contact.get("guardian_name"),
				"guardian_email": contact.get("email"),
				"guardian_phone": contact.get("phone"),
			}
		)

	return {"rows": out, "total_outstanding": total_outstanding, "count": len(out)}


@frappe.whitelist()
def get_payment_history(date_from: str | None = None, date_to: str | None = None, student: str | None = None) -> dict:
	"""Every payment (credit) recorded in the given window -- a
	transaction log / audit trail, newest first. Debits (billing) are
	deliberately excluded here; that's what the collection summary is
	for, this report is specifically "money that came in and when"."""
	_require_bursar()

	filters = {"credit": [">", 0]}
	if date_from:
		filters["posting_datetime"] = [">=", date_from]
	if date_to:
		existing = filters.get("posting_datetime")
		if existing:
			filters["posting_datetime"] = ["between", [date_from, date_to + " 23:59:59"]]
		else:
			filters["posting_datetime"] = ["<=", date_to + " 23:59:59"]
	if student:
		filters["student"] = student

	rows = frappe.get_all(
		"Student Ledger Entry",
		filters=filters,
		fields=["name", "student", "student_name", "posting_datetime", "description", "credit", "academic_term", "reference_student_fee"],
		order_by="posting_datetime desc",
	)

	groups = {
		row.student: row.parent
		for row in frappe.get_all("Student Group Student", filters={"active": 1}, fields=["student", "parent"])
	}

	total = 0.0
	for r in rows:
		r["student_group"] = groups.get(r.student) or "Unassigned"
		total += flt(r.credit)

	return {"rows": rows, "total_collected": total, "count": len(rows)}
