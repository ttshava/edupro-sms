"""
Fee Entry API

Whitelisted methods for Bursar to:
- List and filter student fees
- Edit fee amounts
- Record payment transactions

Student Fee stores amount/amount_paid/balance/status directly (see
edupro_sms.edupro_sms.doctype.student_fee.student_fee.StudentFee.validate,
which recomputes balance and status from amount/amount_paid on every save --
status is always one of "Billed", "Partially Paid", "Paid" and can never be
set directly, since validate() overwrites it unconditionally). Payment
recording delegates to edupro_sms.edupro_sms.fees.record_payment, the one
proven, tested implementation, instead of re-deriving balance from Student
Ledger Entry (which is an audit trail, not the source of truth for balance).

Usage:
    frappe.call({
        method: 'edupro_sms.fee_entry_api.get_student_fees',
        args: { boarding_type: 'Full Boarder', status: 'Billed' }
    })
"""

import frappe
from frappe import _

from edupro_sms.edupro_sms.fees import record_payment as _record_payment


@frappe.whitelist()
def get_student_fees(boarding_type=None, status=None, academic_term=None, limit=100, offset=0, search=None):
    """
    Get list of student fees with optional filters.

    Args:
        boarding_type: "Day Boarder" / "Full Boarder", or None for all
        status: "Billed" / "Partially Paid" / "Paid", or None for all
        academic_term: Academic Term name, or None for all
        limit: Number of results per page (default 100)
        offset: Pagination offset (default 0)
        search: Search by student name

    Returns:
        {
            'fees': [{
                'name': 'SF-STU-001-Term 1 2026',
                'student': 'STU-001',
                'student_name': 'John Doe',
                'email': 'john@school.com',
                'boarding_type': 'Day Boarder',
                'academic_term': 'Term 1 2026',
                'amount': 750,
                'amount_paid': 250,
                'balance': 500,
                'status': 'Partially Paid',
                'due_date': '2026-03-31'
            }, ...],
            'total': 33
        }
    """

    if not frappe.has_permission('Student Fee', 'read'):
        frappe.throw(_("You do not have permission to view fees"))

    filters = {}

    if boarding_type and boarding_type != 'ALL':
        filters['boarding_type'] = boarding_type

    if status and status != 'ALL':
        filters['status'] = status

    if academic_term and academic_term != 'ALL':
        filters['academic_term'] = academic_term

    if search:
        filters['student_name'] = ['like', f'%{search}%']

    try:
        total = frappe.db.count('Student Fee', filters=filters)

        fees = frappe.db.get_list(
            'Student Fee',
            filters=filters,
            fields=[
                'name', 'student', 'student_name', 'boarding_type',
                'academic_term', 'amount', 'amount_paid', 'balance',
                'status', 'due_date'
            ],
            order_by='due_date asc, student_name asc',
            limit_page_length=limit,
            limit_start=offset
        )

        for fee in fees:
            fee['email'] = frappe.db.get_value('Student', fee['student'], 'student_email_id')

        return {
            'fees': fees,
            'total': total
        }

    except Exception as e:
        frappe.logger().error(f"Error fetching student fees: {str(e)}")
        return {'fees': [], 'total': 0, 'error': str(e)}


@frappe.whitelist()
def update_student_fee(fee_id, amount=None):
    """
    Update a student fee's billed amount. Status is never set here -- it's
    auto-computed from amount/amount_paid by Student Fee.validate().

    Args:
        fee_id: Student Fee name
        amount: New billed amount

    Returns:
        {
            'success': True,
            'message': 'Fee updated successfully',
            'updated_fee': {...}
        }
    """

    if not frappe.has_permission('Student Fee', 'write'):
        frappe.throw(_("You do not have permission to update fees"))

    if amount is None:
        return {'success': False, 'error': 'Enter a new amount.'}

    try:
        fee_doc = frappe.get_doc('Student Fee', fee_id)
        old_amount = fee_doc.amount
        fee_doc.amount = float(amount)
        fee_doc.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.logger().info(
            f"Fee {fee_id} amount updated: {old_amount} -> {fee_doc.amount} by {frappe.session.user}"
        )

        return {
            'success': True,
            'message': 'Fee updated successfully',
            'updated_fee': {
                'name': fee_doc.name,
                'amount': fee_doc.amount,
                'balance': fee_doc.balance,
                'status': fee_doc.status
            }
        }

    except Exception as e:
        frappe.logger().error(f"Error updating fee {fee_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def record_payment(fee_id, amount, payment_date=None, payment_method=None, notes=None):
    """
    Record a payment against a student fee. Delegates to the proven
    edupro_sms.edupro_sms.fees.record_payment -- payment_date/payment_method/
    notes are accepted for API-compatibility with the caller but unsupported
    by the schema, so they're ignored rather than silently pretended to work.

    Returns:
        {
            'success': True,
            'message': 'Payment recorded successfully. Outstanding balance: $500.00',
            'new_balance': 500,
            'fee_status': 'Partially Paid',
            'receipt_id': 'a1b2c3d4e5'
        }
    """

    try:
        result = _record_payment(fee_id, amount)
        return {
            'success': True,
            'message': f"Payment recorded successfully. Outstanding balance: ${result['balance']:,.2f}",
            'new_balance': result['balance'],
            'fee_status': result['status'],
            'receipt_id': result['ledger_entry']
        }
    except frappe.PermissionError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        frappe.logger().error(f"Error recording payment for {fee_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@frappe.whitelist()
def get_fee_balance(fee_id):
    """
    Get current balance for a student fee, read directly off the doc
    (amount/amount_paid/balance/status are real stored fields, kept in
    sync by Student Fee.validate() on every save).

    Returns:
        {
            'amount': 750,
            'paid': 250,
            'balance': 500,
            'status': 'Partially Paid'
        }
    """

    try:
        fee_doc = frappe.get_doc('Student Fee', fee_id)
        return {
            'amount': fee_doc.amount,
            'paid': fee_doc.amount_paid,
            'balance': fee_doc.balance,
            'status': fee_doc.status
        }

    except Exception as e:
        frappe.logger().error(f"Error getting fee balance: {str(e)}")
        return {'error': str(e)}
