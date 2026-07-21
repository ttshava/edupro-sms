"""
Batch Billing API

Thin wrapper over edupro_sms.edupro_sms.fees.generate_term_fees, the
proven billing engine already used by the Bursar dashboard: a flat rate
per Student.boarding_type (see fees.BOARDING_FEE), billed once per
Academic Term, skipping students already billed.

This deliberately does NOT use a per-Program rate table or Program
Enrollment records. fees.py's own docstring explains why: "most real
students here don't have a Program Enrollment record, but every
enrolled student has a Student Group." An earlier version of this file
built on Program Enrollment + a "Billing Configuration" doctype whose
database table was never even migrated -- it could not have billed a
single student.
"""

import frappe
from frappe import _

from edupro_sms.edupro_sms.fees import BOARDING_FEE, get_fee_amount, generate_term_fees


def _is_bursar_or_above() -> bool:
    roles = set(frappe.get_roles())
    return bool(roles & {"System Manager", "Headmaster", "Bursar"})


@frappe.whitelist()
def get_boarding_rates():
    """Flat per-term rate by boarding type, for display before billing."""
    return BOARDING_FEE


@frappe.whitelist()
def preview_batch_billing(academic_term, boarding_filter=None):
    """
    Preview how many students would be billed for a term, without
    creating anything.

    Returns:
        {
            'count': 30,
            'already_billed': 3,
            'total_amount': 22500,
            'by_boarding': {'Day Boarder': 25, 'Full Boarder': 5},
            'students': [{...}, ...]  # first 5, for preview
        }
    """
    if not _is_bursar_or_above():
        frappe.throw(_("You do not have permission to preview billing"), frappe.PermissionError)

    students = frappe.get_all(
        "Student",
        filters={"enabled": 1, "student_email_id": ["not like", "%example.edupro.test"]},
        fields=["name", "student_name", "boarding_type"],
    )

    if boarding_filter and boarding_filter != "ALL":
        students = [s for s in students if (s.boarding_type or "Day Boarder") == boarding_filter]

    already_billed = set()
    if students:
        already_billed = set(
            frappe.get_all(
                "Student Fee",
                filters={"academic_term": academic_term, "student": ["in", [s.name for s in students]]},
                pluck="student",
            )
        )

    to_bill = [s for s in students if s.name not in already_billed]

    by_boarding = {}
    for s in to_bill:
        bt = s.boarding_type or "Day Boarder"
        by_boarding[bt] = by_boarding.get(bt, 0) + 1

    return {
        "count": len(to_bill),
        "already_billed": len(already_billed),
        "total_amount": sum(get_fee_amount(s.boarding_type) for s in to_bill),
        "by_boarding": by_boarding,
        "students": [
            {
                "student_id": s.name,
                "student_name": s.student_name,
                "boarding_type": s.boarding_type or "Day Boarder",
                "amount": get_fee_amount(s.boarding_type),
            }
            for s in to_bill[:5]
        ],
    }


@frappe.whitelist()
def create_batch_fees(academic_term, boarding_filter=None):
    """
    Bill every active student for a term (optionally restricted to one
    boarding type). Delegates entirely to fees.generate_term_fees, which
    already handles duplicate-skipping and transaction safety.
    """
    all_students = frappe.get_all(
        "Student",
        filters={"enabled": 1, "student_email_id": ["not like", "%example.edupro.test"]},
        fields=["name", "boarding_type"],
    )
    if boarding_filter and boarding_filter != "ALL":
        all_students = [s for s in all_students if (s.boarding_type or "Day Boarder") == boarding_filter]

    result = generate_term_fees(academic_term, students=[s.name for s in all_students])
    return {
        "success": True,
        "created": result["created"],
        "skipped": result["skipped"],
        "message": f"Batch billing complete: {result['created']} created, {result['skipped']} skipped.",
    }
