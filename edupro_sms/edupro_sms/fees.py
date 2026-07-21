"""Termly school fees -- a flat rate per term determined entirely by a
student's Boarding Type (Student.boarding_type), billed once per
Academic Term into a Student Fee record. Deliberately not built on
Education's Fee Structure/Fee Schedule/Fees chain: that pipeline
generates ERPNext Sales Invoices and needs a Company/Chart of
Accounts/Items configured for GL posting, which this school doesn't
use and didn't ask for -- Report Card was built the same way, as its
own doctype, for the same reason (DECISIONS.md 0008)."""

import frappe
from frappe.utils import flt, now_datetime, today

BOARDING_FEE = {
	"Day Boarder": 750,
	"Full Boarder": 1450,
}
DEFAULT_BOARDING_TYPE = "Day Boarder"


def get_fee_amount(boarding_type: str | None) -> float:
	return BOARDING_FEE.get(boarding_type or DEFAULT_BOARDING_TYPE, BOARDING_FEE[DEFAULT_BOARDING_TYPE])


def _is_bursar_or_above(user: str | None = None) -> bool:
	roles = set(frappe.get_roles(user))
	return bool(roles & {"System Manager", "Headmaster", "Bursar"})


def _log_ledger_entry(
	student: str,
	description: str,
	debit: float = 0,
	credit: float = 0,
	academic_term: str | None = None,
	reference_student_fee: str | None = None,
	posting_datetime=None,
) -> str:
	"""Every bill and every payment gets its own timestamped row here --
	the Fee Statement print format renders these as a running Debit/
	Credit/Balance ledger, like a bank statement, instead of just a
	per-term summary. Returns the new row's name -- record_payment()
	uses it as the receipt to print (Payment Receipt print format is
	bound to Student Ledger Entry, not Student Fee, since a fee can be
	paid in several installments and each one needs its own receipt)."""
	doc = frappe.get_doc(
		{
			"doctype": "Student Ledger Entry",
			"student": student,
			"posting_datetime": posting_datetime or now_datetime(),
			"academic_term": academic_term,
			"reference_student_fee": reference_student_fee,
			"description": description,
			"debit": debit,
			"credit": credit,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def generate_term_fees(academic_term: str, students: list[str] | None = None) -> dict:
	"""Bill every active (or given) student for a term, skipping anyone
	already billed for it -- safe to re-run."""
	if not _is_bursar_or_above():
		frappe.throw("You are not permitted to bill fees.", frappe.PermissionError)

	academic_year = frappe.db.get_value("Academic Term", academic_term, "academic_year")

	filters = {"enabled": 1}
	if students:
		filters["name"] = ["in", students]
	targets = frappe.get_all("Student", filters=filters, fields=["name", "boarding_type"])

	created, skipped = [], []
	for s in targets:
		name = f"SF-{s.name}-{academic_term}"
		if frappe.db.exists("Student Fee", name):
			skipped.append(s.name)
			continue
		boarding_type = s.boarding_type or DEFAULT_BOARDING_TYPE
		doc = frappe.get_doc(
			{
				"doctype": "Student Fee",
				"student": s.name,
				"academic_year": academic_year,
				"academic_term": academic_term,
				"boarding_type": boarding_type,
				"amount": get_fee_amount(boarding_type),
				"billed_on": today(),
			}
		)
		doc.insert(ignore_permissions=True)
		created.append(doc.name)
		_log_ledger_entry(
			s.name,
			f"{academic_term} Fees Billed ({boarding_type})",
			debit=get_fee_amount(boarding_type),
			academic_term=academic_term,
			reference_student_fee=doc.name,
		)

	frappe.db.commit()
	return {"created": len(created), "skipped": len(skipped)}


def get_student_fee_statement(student: str) -> dict:
	"""All terms of the student's current class's academic year, each
	shown as either a real billed Student Fee row or a projected "not
	yet billed" row (no placeholder record created for unbilled terms --
	computed here instead, using the student's current boarding rate).
	Academic year comes from the student's Student Group, not Program
	Enrollment -- most real students here don't have a Program
	Enrollment record, but every enrolled student has a Student Group."""
	boarding_type = frappe.db.get_value("Student", student, "boarding_type") or DEFAULT_BOARDING_TYPE

	student_group = frappe.db.get_value(
		"Student Group Student", {"student": student, "active": 1}, "parent", order_by="creation desc"
	)
	academic_year = frappe.db.get_value("Student Group", student_group, "academic_year") if student_group else None
	terms = []
	if academic_year:
		terms = frappe.get_all(
			"Academic Term",
			filters={"academic_year": academic_year},
			fields=["name", "term_start_date"],
			order_by="term_start_date asc",
		)

	billed = {
		f.academic_term: f
		for f in frappe.get_all(
			"Student Fee",
			filters={"student": student},
			fields=["academic_term", "amount", "amount_paid", "balance", "status", "boarding_type", "due_date"],
		)
	}

	rows = []
	total_balance = 0.0
	for term in terms:
		row = billed.get(term.name)
		if row:
			rows.append(
				{
					"academic_term": term.name,
					"billed": True,
					"boarding_type": row.boarding_type,
					"amount": row.amount,
					"amount_paid": row.amount_paid,
					"balance": row.balance,
					"status": row.status,
					"due_date": row.due_date,
				}
			)
			total_balance += flt(row.balance)
		else:
			rows.append(
				{
					"academic_term": term.name,
					"billed": False,
					"boarding_type": boarding_type,
					"amount": get_fee_amount(boarding_type),
					"amount_paid": 0,
					"balance": 0,
					"status": "Not Billed",
					"due_date": None,
				}
			)

	return {
		"academic_year": academic_year,
		"boarding_type": boarding_type,
		"total_balance": total_balance,
		"terms": rows,
	}


@frappe.whitelist()
def record_payment(student_fee: str, amount) -> dict:
	"""Bursar-facing: add a payment to a Student Fee's running amount_paid
	(not overwrite it -- a term is typically paid in more than one
	installment). Refuses to overpay past the billed amount rather than
	letting balance go negative."""
	if not _is_bursar_or_above():
		frappe.throw("You are not permitted to record payments.", frappe.PermissionError)

	amount = flt(amount)
	if amount <= 0:
		frappe.throw("Payment amount must be greater than zero.")

	doc = frappe.get_doc("Student Fee", student_fee)
	new_paid = flt(doc.amount_paid) + amount
	if new_paid > flt(doc.amount):
		frappe.throw(
			f"Payment of {amount} would exceed the outstanding balance of {flt(doc.amount) - flt(doc.amount_paid)}."
		)
	doc.amount_paid = new_paid
	doc.save(ignore_permissions=True)
	ledger_entry = _log_ledger_entry(
		doc.student,
		f"Payment Received - {doc.academic_term}",
		credit=amount,
		academic_term=doc.academic_term,
		reference_student_fee=doc.name,
	)
	frappe.db.commit()
	return {
		"name": doc.name,
		"amount_paid": doc.amount_paid,
		"balance": doc.balance,
		"status": doc.status,
		"ledger_entry": ledger_entry,
	}


@frappe.whitelist()
def set_boarding_type(student: str, boarding_type: str) -> dict:
	"""Bursar-facing: change a student's boarding type going forward.
	Deliberately does not touch any already-billed Student Fee record --
	those keep the boarding_type/amount that applied when they were
	billed, so changing this never rewrites history."""
	if not _is_bursar_or_above():
		frappe.throw("You are not permitted to change boarding type.", frappe.PermissionError)

	if boarding_type not in BOARDING_FEE:
		frappe.throw(f"Unknown boarding type: {boarding_type}")

	frappe.db.set_value("Student", student, "boarding_type", boarding_type)
	frappe.db.commit()
	return {"student": student, "boarding_type": boarding_type}


@frappe.whitelist()
def get_all_students_fee_summary() -> list[dict]:
	"""Bursar's overview: every enabled student with their class, current
	boarding type, and billed/paid/balance totals across whatever terms
	have been billed so far (real students only -- @example.edupro.test
	sample/demo students are excluded the same way the rest of this
	project treats them)."""
	if not _is_bursar_or_above():
		frappe.throw("You are not permitted to view fee records.", frappe.PermissionError)

	students = frappe.get_all(
		"Student",
		filters={"enabled": 1, "student_email_id": ["not like", "%example.edupro.test"]},
		fields=["name", "student_name", "boarding_type"],
		order_by="student_name asc",
	)

	totals = {}
	for row in frappe.get_all(
		"Student Fee", fields=["student", "amount", "amount_paid", "balance"]
	):
		t = totals.setdefault(row.student, {"billed": 0.0, "paid": 0.0, "balance": 0.0})
		t["billed"] += flt(row.amount)
		t["paid"] += flt(row.amount_paid)
		t["balance"] += flt(row.balance)

	groups = {
		row.student: row.parent
		for row in frappe.get_all(
			"Student Group Student", filters={"active": 1}, fields=["student", "parent"]
		)
	}

	rows = []
	for s in students:
		t = totals.get(s.name, {"billed": 0.0, "paid": 0.0, "balance": 0.0})
		rows.append(
			{
				"student": s.name,
				"student_name": s.student_name,
				"student_group": groups.get(s.name) or "Unassigned",
				"boarding_type": s.boarding_type or DEFAULT_BOARDING_TYPE,
				"total_billed": t["billed"],
				"total_paid": t["paid"],
				"total_balance": t["balance"],
			}
		)
	return rows


def get_school_fee_totals() -> dict:
	"""Whole-school billed/collected/outstanding totals across every
	Student Fee record billed so far -- powers the Headmaster dashboard's
	Revenue Collected / Outstanding Balance stat cards."""
	row = frappe.db.sql(
		"select sum(amount) as billed, sum(amount_paid) as paid, sum(balance) as balance from `tabStudent Fee`",
		as_dict=True,
	)[0]
	return {
		"total_billed": flt(row.billed),
		"total_collected": flt(row.paid),
		"total_outstanding": flt(row.balance),
	}


def get_class_fee_summary() -> list[dict]:
	"""Billed/collected/outstanding totals aggregated per class (Student
	Group) -- the class-by-class finance breakdown on the Headmaster
	dashboard, one level up from get_all_students_fee_summary()'s
	per-student rows."""
	totals = {}
	for row in frappe.get_all("Student Fee", fields=["student", "amount", "amount_paid", "balance"]):
		t = totals.setdefault(row.student, {"billed": 0.0, "paid": 0.0, "balance": 0.0})
		t["billed"] += flt(row.amount)
		t["paid"] += flt(row.amount_paid)
		t["balance"] += flt(row.balance)

	groups = {
		row.student: row.parent
		for row in frappe.get_all("Student Group Student", filters={"active": 1}, fields=["student", "parent"])
	}

	by_class = {}
	for student, t in totals.items():
		group = groups.get(student) or "Unassigned"
		c = by_class.setdefault(group, {"billed": 0.0, "paid": 0.0, "balance": 0.0, "student_count": 0})
		c["billed"] += t["billed"]
		c["paid"] += t["paid"]
		c["balance"] += t["balance"]
		c["student_count"] += 1

	rows = [{"student_group": group, **vals} for group, vals in by_class.items()]
	rows.sort(key=lambda r: r["student_group"])
	return rows


def get_student_ledger(student: str) -> dict:
	"""The full running ledger for a student -- every bill (Debit) and
	every payment (Credit), oldest first, with a running balance. This
	is what the Fee Statement print format renders as a bank-statement
	style table, as opposed to get_student_fee_statement()'s per-term
	summary (used on-screen in the Bursar/My Reports Fees tabs)."""
	entries = frappe.get_all(
		"Student Ledger Entry",
		filters={"student": student},
		fields=["posting_datetime", "description", "debit", "credit", "academic_term", "creation"],
	)

	term_start = {
		t.name: t.term_start_date
		for t in frappe.get_all("Academic Term", fields=["name", "term_start_date"])
	}
	entries.sort(
		key=lambda e: (
			e.posting_datetime,
			term_start.get(e.academic_term) or e.posting_datetime,
			e.creation,
		)
	)

	rows = []
	balance = 0.0
	for e in entries:
		balance += flt(e.debit) - flt(e.credit)
		rows.append(
			{
				"posting_datetime": e.posting_datetime,
				"description": e.description,
				"debit": e.debit,
				"credit": e.credit,
				"balance": balance,
			}
		)

	return {"entries": rows, "closing_balance": balance}


def get_receipt_context(ledger_entry: str) -> dict:
	"""Everything the Payment Receipt print format needs for one payment
	row -- the student's current class, and (when the payment is tied to
	a Student Fee) that term's real amount/paid/balance, read straight
	off the stored Student Fee record rather than recomputed here, since
	Student Ledger Entry rows don't carry their own persisted balance
	(get_student_ledger() computes a running balance only at display
	time, across the whole account, not per row)."""
	entry = frappe.get_doc("Student Ledger Entry", ledger_entry)

	student_group = frappe.db.get_value(
		"Student Group Student", {"student": entry.student, "active": 1}, "parent", order_by="creation desc"
	)

	fee = None
	if entry.reference_student_fee and frappe.db.exists("Student Fee", entry.reference_student_fee):
		fee = frappe.db.get_value(
			"Student Fee",
			entry.reference_student_fee,
			["academic_term", "amount", "amount_paid", "balance"],
			as_dict=True,
		)

	return {
		"entry": entry,
		"student_group": student_group or "Unassigned",
		"fee": fee,
	}
