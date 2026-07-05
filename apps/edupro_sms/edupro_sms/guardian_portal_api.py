"""
Guardian/Parent Portal API

Whitelisted methods for parents to access linked children's data:
- get_guardian_dashboard(): List of linked children
- get_child_grades(student_id, academic_term=None): Child's grades
- get_child_reports(student_id): Child's report cards
- get_child_fees(student_id): Child's fee status
- get_child_dashboard(student_id): Child's overall summary

Usage:
    frappe.call({
        method: 'edupro_sms.guardian_portal_api.get_guardian_dashboard',
        callback: function(r) { console.log(r.message); }
    })
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_guardian_dashboard():
    """
    Get list of children linked to this guardian.

    Returns:
        {
            'children': [
                {
                    'student_id': 'STU-001',
                    'student_name': 'John Doe',
                    'admission_number': 'ADM-001',
                    'class': 'Form 1A',
                    'program': 'IGCSE Science',
                    'gpa': 3.8,
                    'class_position': 5,
                    'last_report_date': '2026-05-15'
                },
                ...
            ],
            'count': 2
        }
    """

    # Get current user's guardian record
    user = frappe.session.user
    guardian_id = frappe.db.get_value(
        'Student Guardian Link',
        filters={'parent': user, 'parenttype': 'User'},
        pluck='parent'
    )

    # Alternative: check if user is a Guardian DocType
    if not guardian_id:
        guardian_doc = frappe.db.get_value('Guardian', filters={'email': user}, pluck='name')
        if not guardian_doc:
            frappe.throw(_("You are not registered as a guardian"))
        guardian_id = guardian_doc

    try:
        # Get all linked students
        linked_students = frappe.db.get_list(
            'Student Guardian Link',
            filters={'guardian': guardian_id},
            fields=['student']
        )

        if not linked_students:
            return {'children': [], 'count': 0}

        children = []

        for link in linked_students:
            student_id = link['student']
            student_doc = frappe.get_doc('Student', student_id)

            # Get current enrollment
            enrollment = frappe.db.get_value(
                'Program Enrollment',
                filters={'student': student_id, 'docstatus': 1},
                fields=['program', 'student_group'],
                order_by='modified desc'
            )

            student_group = enrollment[1] if enrollment else 'Not Enrolled'
            program = enrollment[0] if enrollment else 'Not Assigned'

            # Calculate GPA
            marks = frappe.db.get_list(
                'Mark',
                filters={'student': student_id},
                fields=['SUM(term_mark + exam_mark) / COUNT(*) as avg_mark']
            )

            avg_mark = float(marks[0]['avg_mark']) if marks and marks[0]['avg_mark'] else 0
            gpa = (avg_mark / 100) * 4.0

            # Get class position
            position = frappe.db.get_value(
                'Report Card',
                filters={'student': student_id},
                fields=['class_position'],
                order_by='academic_term desc'
            )

            class_position = position if position else 'N/A'

            # Get last report date
            last_report = frappe.db.get_value(
                'Report Card',
                filters={'student': student_id},
                fields=['creation'],
                order_by='modified desc'
            )

            last_report_date = str(last_report).split()[0] if last_report else 'No reports'

            children.append({
                'student_id': student_id,
                'student_name': student_doc.student_name,
                'admission_number': student_doc.admission_number,
                'class': student_group,
                'program': program,
                'gpa': round(gpa, 2),
                'class_position': class_position,
                'last_report_date': last_report_date
            })

        return {'children': children, 'count': len(children)}

    except Exception as e:
        frappe.logger().error(f"Error getting guardian dashboard: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_child_grades(student_id, academic_term=None):
    """
    Get linked child's grades.

    Args:
        student_id: Student ID (must be linked to current guardian)
        academic_term: Academic Term name (if None, gets all terms)

    Returns:
        {
            'grades': [{subject, term_mark, exam_mark, grade, comment}, ...],
            'term': 'Term 1 2026',
            'term_average': 82.5,
            'student_name': 'John Doe'
        }
    """

    # Permission check: verify student is linked to current guardian
    user = frappe.session.user
    guardian = frappe.db.get_value('Guardian', filters={'email': user}, pluck='name')

    if not guardian:
        frappe.throw(_("You are not registered as a guardian"))

    # Verify student is linked
    is_linked = frappe.db.get_value(
        'Student Guardian Link',
        filters={'guardian': guardian, 'student': student_id},
        pluck='name'
    )

    if not is_linked:
        frappe.throw(_("You do not have permission to view this student's data"))

    try:
        student_doc = frappe.get_doc('Student', student_id)

        # Get marks
        filters = {'student': student_id}
        if academic_term:
            filters['academic_term'] = academic_term

        marks = frappe.db.get_list(
            'Mark',
            filters=filters,
            fields=['subject', 'term_mark', 'exam_mark', 'grade', 'comments', 'academic_term'],
            order_by='subject asc'
        )

        if not marks:
            return {
                'grades': [],
                'term': academic_term or 'All Terms',
                'term_average': 0,
                'student_name': student_doc.student_name,
                'message': 'No marks found'
            }

        grades = []
        total_marks = 0
        mark_count = 0

        for mark in marks:
            total_mark = (mark['term_mark'] or 0) + (mark['exam_mark'] or 0)
            grades.append({
                'subject': mark['subject'],
                'term_mark': mark['term_mark'] or 0,
                'exam_mark': mark['exam_mark'] or 0,
                'total_mark': total_mark,
                'grade': mark['grade'] or 'N/A',
                'teacher_comment': mark['comments'] or ''
            })
            total_marks += total_mark
            mark_count += 1

        term_average = (total_marks / (mark_count * 2)) if mark_count > 0 else 0

        return {
            'grades': grades,
            'term': academic_term or 'All Terms',
            'term_average': round(term_average, 2),
            'student_name': student_doc.student_name,
            'subject_count': len(grades)
        }

    except Exception as e:
        frappe.logger().error(f"Error getting child grades: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_child_reports(student_id):
    """
    Get linked child's report cards.

    Args:
        student_id: Student ID (must be linked to current guardian)

    Returns:
        {
            'reports': [{name, academic_term, created, ...}, ...],
            'count': 3,
            'student_name': 'John Doe'
        }
    """

    # Permission check
    user = frappe.session.user
    guardian = frappe.db.get_value('Guardian', filters={'email': user}, pluck='name')

    if not guardian:
        frappe.throw(_("You are not registered as a guardian"))

    is_linked = frappe.db.get_value(
        'Student Guardian Link',
        filters={'guardian': guardian, 'student': student_id},
        pluck='name'
    )

    if not is_linked:
        frappe.throw(_("You do not have permission to view this student's data"))

    try:
        student_doc = frappe.get_doc('Student', student_id)

        # Get published reports
        reports = frappe.db.get_list(
            'Report Card',
            filters={'student': student_id, 'docstatus': 1},
            fields=['name', 'academic_term', 'creation'],
            order_by='academic_term desc'
        )

        report_list = []
        for report in reports:
            report_list.append({
                'name': report['name'],
                'academic_term': report['academic_term'],
                'created': str(report['creation']).split()[0],
                'download_url': f'/api/resource/Report Card/{report["name"]}',
                'print_url': f'/api/method/frappe.client.get_print?doctype=Report Card&name={report["name"]}'
            })

        return {
            'reports': report_list,
            'count': len(report_list),
            'student_name': student_doc.student_name
        }

    except Exception as e:
        frappe.logger().error(f"Error getting child reports: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_child_fees(student_id):
    """
    Get linked child's fee status.

    Args:
        student_id: Student ID (must be linked to current guardian)

    Returns:
        {
            'fees': [{academic_term, amount, paid, balance, status, ...}, ...],
            'total_amount': 15000,
            'total_paid': 8000,
            'outstanding': 7000,
            'collection_percentage': 53.3,
            'student_name': 'John Doe'
        }
    """

    # Permission check
    user = frappe.session.user
    guardian = frappe.db.get_value('Guardian', filters={'email': user}, pluck='name')

    if not guardian:
        frappe.throw(_("You are not registered as a guardian"))

    is_linked = frappe.db.get_value(
        'Student Guardian Link',
        filters={'guardian': guardian, 'student': student_id},
        pluck='name'
    )

    if not is_linked:
        frappe.throw(_("You do not have permission to view this student's data"))

    try:
        student_doc = frappe.get_doc('Student', student_id)

        # Get fees
        fees = frappe.db.get_list(
            'Student Fee',
            filters={'student': student_id},
            fields=['name', 'academic_term', 'program', 'amount', 'status', 'due_date'],
            order_by='academic_term desc'
        )

        fee_list = []
        total_amount = 0
        total_paid = 0

        for fee in fees:
            # Get payment history
            paid = frappe.db.get_value(
                'Student Ledger Entry',
                filters={'student_fee': fee['name'], 'docstatus': 1},
                fieldname='SUM(debit) as total_paid'
            ) or 0

            paid = float(paid)
            balance = fee['amount'] - paid

            fee_list.append({
                'academic_term': fee['academic_term'],
                'program': fee['program'],
                'amount': fee['amount'],
                'paid': paid,
                'balance': max(0, balance),
                'status': fee['status'],
                'due_date': str(fee['due_date']) if fee['due_date'] else 'N/A'
            })

            total_amount += fee['amount']
            total_paid += paid

        outstanding = total_amount - total_paid
        collection_pct = (total_paid / total_amount * 100) if total_amount > 0 else 0

        return {
            'fees': fee_list,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'outstanding': max(0, outstanding),
            'collection_percentage': round(collection_pct, 2),
            'student_name': student_doc.student_name,
            'fee_count': len(fee_list)
        }

    except Exception as e:
        frappe.logger().error(f"Error getting child fees: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_child_dashboard(student_id):
    """
    Get linked child's dashboard summary (all info in one call).

    Args:
        student_id: Student ID (must be linked to current guardian)

    Returns:
        {
            'student': {name, class, program, gpa, position, ...},
            'grades': [{subject, grade, ...}, ...],
            'reports': [{academic_term, created, ...}, ...],
            'fees': [{academic_term, amount, balance, ...}, ...],
            'alerts': [{type, message}, ...] (if any issues)
        }
    """

    # Permission check
    user = frappe.session.user
    guardian = frappe.db.get_value('Guardian', filters={'email': user}, pluck='name')

    if not guardian:
        frappe.throw(_("You are not registered as a guardian"))

    is_linked = frappe.db.get_value(
        'Student Guardian Link',
        filters={'guardian': guardian, 'student': student_id},
        pluck='name'
    )

    if not is_linked:
        frappe.throw(_("You do not have permission to view this student's data"))

    try:
        # Get all data
        grades_data = get_child_grades(student_id)
        reports_data = get_child_reports(student_id)
        fees_data = get_child_fees(student_id)

        student_doc = frappe.get_doc('Student', student_id)
        enrollment = frappe.db.get_value(
            'Program Enrollment',
            filters={'student': student_id, 'docstatus': 1},
            fields=['program', 'student_group'],
            order_by='modified desc'
        )

        alerts = []

        # Generate alerts
        if grades_data.get('term_average', 0) < 50:
            alerts.append({'type': 'warning', 'message': 'Grade average below 50%'})

        if fees_data.get('outstanding', 0) > 0:
            alerts.append({'type': 'info', 'message': f"Outstanding fees: ${fees_data['outstanding']:,.2f}"})

        return {
            'student': {
                'student_id': student_id,
                'name': student_doc.student_name,
                'class': enrollment[1] if enrollment else 'Not Enrolled',
                'program': enrollment[0] if enrollment else 'Not Assigned',
                'gpa': grades_data.get('term_average', 0) / 25 if grades_data.get('term_average') else 0  # Convert to 4.0 scale
            },
            'latest_grades': grades_data.get('grades', [])[:5],  # Last 5 subjects
            'latest_reports': reports_data.get('reports', [])[:3],  # Last 3 reports
            'current_fees': fees_data.get('fees', []),
            'fee_status': {
                'outstanding': fees_data.get('outstanding', 0),
                'collection_percentage': fees_data.get('collection_percentage', 0)
            },
            'alerts': alerts
        }

    except Exception as e:
        frappe.logger().error(f"Error getting child dashboard: {str(e)}")
        return {'error': str(e)}
