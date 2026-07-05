"""
Fee Dashboard API

Whitelisted methods for Headmaster to:
- Get fee financial overview (total billed, collected, outstanding)
- Calculate collection statistics and trends
- Get unpaid students list
- Get breakdown by program and boarding type

Usage:
    frappe.call({
        method: 'edupro_sms.fee_dashboard_api.get_fee_dashboard_data',
        args: { term: 'Term 1 2026', program: None }
    })
"""

import frappe
from frappe import _
from datetime import datetime, timedelta
from decimal import Decimal


@frappe.whitelist()
def get_fee_dashboard_data(term=None, program=None):
    """
    Get comprehensive fee dashboard data.

    Args:
        term: Academic Term name (if None, uses current active term)
        program: Program name (if None, includes all programs)

    Returns:
        {
            'summary': {
                'total_billed': 500000,
                'total_collected': 320000,
                'outstanding': 180000,
                'collection_percentage': 64.0,
                'number_of_students': 200
            },
            'by_program': [
                {
                    'program': 'IGCSE Science',
                    'billed': 250000,
                    'collected': 200000,
                    'percentage': 80.0
                },
                ...
            ],
            'by_status': {
                'Paid': 140,
                'Partial': 50,
                'Unpaid': 10
            },
            'collection_trend': [
                {'week': 'Week 1', 'percentage': 30},
                {'week': 'Week 2', 'percentage': 50},
                ...
            ],
            'unpaid_students': [
                {
                    'student_name': 'John Doe',
                    'admission_number': 'ADM-001',
                    'amount': 5000,
                    'days_overdue': 15
                },
                ...
            ]
        }
    """

    if not frappe.has_permission('Student Fee', 'read'):
        frappe.throw(_("You do not have permission to view dashboard"))

    # Get active term if not specified
    if not term:
        term_doc = frappe.db.get_value(
            'Academic Term',
            filters={'is_active': 1},
            fieldname='name'
        )
        if not term_doc:
            return {'error': 'No active academic term found'}
        term = term_doc

    # Build filters
    filters = {'academic_term': term}
    if program:
        filters['program'] = program

    try:
        # Get all fees for the term
        fees = frappe.db.get_list(
            'Student Fee',
            filters=filters,
            fields=['name', 'amount', 'status', 'program', 'student', 'due_date']
        )

        if not fees:
            return {
                'summary': {
                    'total_billed': 0,
                    'total_collected': 0,
                    'outstanding': 0,
                    'collection_percentage': 0,
                    'number_of_students': 0
                },
                'by_program': [],
                'by_status': {'Paid': 0, 'Partial': 0, 'Unpaid': 0},
                'collection_trend': [],
                'unpaid_students': []
            }

        # Calculate totals
        total_billed = sum(Decimal(str(f['amount'])) for f in fees)
        total_billed = float(total_billed)

        # Get collected amounts
        ledger_entries = frappe.db.get_list(
            'Student Ledger Entry',
            filters={'docstatus': 1},
            fields=['student_fee', 'SUM(debit) as total_paid'],
            group_by='student_fee'
        )

        collected_by_fee = {entry['student_fee']: float(entry['total_paid']) for entry in ledger_entries}
        total_collected = sum(collected_by_fee.values())

        outstanding = total_billed - total_collected
        collection_percentage = (total_collected / total_billed * 100) if total_billed > 0 else 0

        # Group by program
        by_program = {}
        for fee in fees:
            prog = fee['program']
            if prog not in by_program:
                by_program[prog] = {'billed': 0, 'collected': 0}

            by_program[prog]['billed'] += Decimal(str(fee['amount']))
            by_program[prog]['collected'] += Decimal(str(collected_by_fee.get(fee['name'], 0)))

        by_program_list = []
        for prog, data in sorted(by_program.items()):
            billed = float(data['billed'])
            collected = float(data['collected'])
            pct = (collected / billed * 100) if billed > 0 else 0

            by_program_list.append({
                'program': prog,
                'billed': billed,
                'collected': collected,
                'percentage': round(pct, 2)
            })

        # Count by status
        by_status = {'Paid': 0, 'Partial': 0, 'Unpaid': 0}
        for fee in fees:
            status = fee['status']
            if status in by_status:
                by_status[status] += 1

        # Collection trend (by week)
        collection_trend = calculate_collection_trend(term, fees, collected_by_fee)

        # Unpaid students (overdue or still owing)
        unpaid_students = get_unpaid_students(fees, collected_by_fee, term)

        return {
            'summary': {
                'total_billed': round(total_billed, 2),
                'total_collected': round(total_collected, 2),
                'outstanding': round(outstanding, 2),
                'collection_percentage': round(collection_percentage, 2),
                'number_of_students': len(fees)
            },
            'by_program': by_program_list,
            'by_status': by_status,
            'collection_trend': collection_trend,
            'unpaid_students': unpaid_students
        }

    except Exception as e:
        frappe.logger().error(f"Error getting dashboard data: {str(e)}")
        return {'error': str(e)}


def calculate_collection_trend(term, fees, collected_by_fee):
    """
    Calculate collection percentage trend by week.

    Returns list of {week, percentage} for each week of the term.
    """

    try:
        term_doc = frappe.db.get_value(
            'Academic Term',
            term,
            ['start_date', 'end_date']
        )

        if not term_doc:
            return []

        start_date = datetime.strptime(str(term_doc[0]), '%Y-%m-%d')
        end_date = datetime.strptime(str(term_doc[1]), '%Y-%m-%d')

        # Calculate weekly percentages
        trend = []
        current_date = start_date
        week_num = 1

        while current_date <= end_date:
            # Get ledger entries up to this date
            week_collected = frappe.db.get_value(
                'Student Ledger Entry',
                filters={
                    'docstatus': 1,
                    'reference_date': ['<=', current_date]
                },
                fieldname='SUM(debit) as total'
            ) or 0

            # Get initial total billed
            total_billed = sum(Decimal(str(f['amount'])) for f in fees)

            # Calculate percentage
            total_billed_float = float(total_billed)
            week_collected_float = float(week_collected)
            percentage = (week_collected_float / total_billed_float * 100) if total_billed_float > 0 else 0

            trend.append({
                'week': f'Week {week_num}',
                'percentage': round(percentage, 2),
                'date': current_date.strftime('%Y-%m-%d')
            })

            # Move to next week
            current_date += timedelta(days=7)
            week_num += 1

        return trend

    except Exception as e:
        frappe.logger().error(f"Error calculating trend: {str(e)}")
        return []


def get_unpaid_students(fees, collected_by_fee, term):
    """
    Get list of students with outstanding fees.

    Returns list of {student_name, admission_number, amount, days_overdue}
    """

    unpaid = []
    today = datetime.now().date()

    for fee in fees:
        balance = Decimal(str(fee['amount'])) - Decimal(str(collected_by_fee.get(fee['name'], 0)))

        if balance > 0:  # Still owing
            student_data = frappe.db.get_value(
                'Student',
                fee['student'],
                ['student_name', 'admission_number']
            )

            # Calculate days overdue
            due_date = fee.get('due_date')
            days_overdue = 0
            if due_date:
                try:
                    due_date_obj = datetime.strptime(str(due_date), '%Y-%m-%d').date()
                    days_overdue = (today - due_date_obj).days
                    if days_overdue < 0:
                        days_overdue = 0
                except:
                    pass

            unpaid.append({
                'student_name': student_data[0] if student_data else 'Unknown',
                'admission_number': student_data[1] if student_data else 'N/A',
                'amount': float(balance),
                'days_overdue': days_overdue,
                'fee_id': fee['name']
            })

    # Sort by days overdue (descending) and amount (descending)
    unpaid.sort(key=lambda x: (-x['days_overdue'], -x['amount']))

    return unpaid[:20]  # Return top 20 unpaid students


@frappe.whitelist()
def get_collection_metrics(term=None):
    """
    Get high-level collection metrics for quick overview.

    Returns:
        {
            'total_billed': 500000,
            'total_collected': 320000,
            'outstanding': 180000,
            'collection_rate': 64.0,
            'students_paid_in_full': 140,
            'students_partial': 50,
            'students_unpaid': 10
        }
    """

    if not frappe.has_permission('Student Fee', 'read'):
        frappe.throw(_("You do not have permission to view metrics"))

    data = get_fee_dashboard_data(term)

    if 'error' in data:
        return data

    return {
        'total_billed': data['summary']['total_billed'],
        'total_collected': data['summary']['total_collected'],
        'outstanding': data['summary']['outstanding'],
        'collection_rate': data['summary']['collection_percentage'],
        'students_paid_in_full': data['by_status'].get('Paid', 0),
        'students_partial': data['by_status'].get('Partial', 0),
        'students_unpaid': data['by_status'].get('Unpaid', 0)
    }
