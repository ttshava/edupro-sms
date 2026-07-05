"""
Student Portal API

Whitelisted methods for students to access their own data:
- get_student_dashboard(): Summary of student info and current performance
- get_student_grades(academic_term=None): Grades by subject for term(s)
- get_student_reports(): List of report cards for download
- get_student_fees(): Fee status and payment history

Usage:
    frappe.call({
        method: 'edupro_sms.student_portal_api.get_student_dashboard',
        callback: function(r) { console.log(r.message); }
    })
"""

import frappe
from frappe import _
from decimal import Decimal


@frappe.whitelist()
def get_student_dashboard():
    """
    Get student's dashboard summary.

    Returns:
        {
            'student_id': 'STU-001',
            'student_name': 'John Doe',
            'admission_number': 'ADM-001',
            'class': 'Form 1A',
            'program': 'IGCSE Science',
            'current_term': 'Term 1 2026',
            'gpa': 3.8,
            'class_position': 5,
            'total_students_in_class': 45,
            'last_report_date': '2026-05-15',
            'enrolled': True
        }
    """

    # Get current user's student record
    user = frappe.session.user
    student_id = frappe.db.get_value('Student', filters={'user_id': user}, pluck='name')

    if not student_id:
        frappe.throw(_("You are not registered as a student"))

    try:
        student_doc = frappe.get_doc('Student', student_id)

        # Get current enrollment (most recent)
        enrollment = frappe.db.get_value(
            'Program Enrollment',
            filters={'student': student_id, 'docstatus': 1},
            fields=['program', 'student_group', 'academic_term'],
            order_by='modified desc'
        )

        student_group = enrollment[1] if enrollment else 'Not Enrolled'
        program = enrollment[0] if enrollment else 'Not Assigned'
        current_term = enrollment[2] if enrollment else None

        # Get current term if not found
        if not current_term:
            current_term = frappe.db.get_value(
                'Academic Term',
                filters={'is_active': 1},
                pluck='name'
            )

        # Calculate GPA (weighted average of all marks)
        marks = frappe.db.get_list(
            'Mark',
            filters={'student': student_id},
            fields=['SUM(term_mark + exam_mark) / COUNT(*) as avg_mark']
        )

        avg_mark = float(marks[0]['avg_mark']) if marks and marks[0]['avg_mark'] else 0
        # Convert to GPA scale (0-4.0)
        gpa = (avg_mark / 100) * 4.0

        # Get class position (based on latest report card)
        position = frappe.db.get_value(
            'Report Card',
            filters={'student': student_id},
            fields=['class_position'],
            order_by='academic_term desc'
        )

        class_position = position if position else 'N/A'

        # Count total students in class
        total_in_class = frappe.db.count(
            'Program Enrollment',
            filters={'student_group': student_group, 'docstatus': 1}
        ) if student_group != 'Not Enrolled' else 0

        # Get last report date
        last_report = frappe.db.get_value(
            'Report Card',
            filters={'student': student_id},
            fields=['creation'],
            order_by='modified desc'
        )

        last_report_date = str(last_report).split()[0] if last_report else 'No reports yet'

        return {
            'student_id': student_id,
            'student_name': student_doc.student_name,
            'admission_number': student_doc.admission_number,
            'email': student_doc.email,
            'class': student_group,
            'program': program,
            'current_term': current_term,
            'gpa': round(gpa, 2),
            'class_position': class_position,
            'total_students_in_class': total_in_class,
            'last_report_date': last_report_date,
            'enrolled': enrollment is not None
        }

    except Exception as e:
        frappe.logger().error(f"Error getting student dashboard: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_student_grades(academic_term=None):
    """
    Get student's grades for a term or all terms.

    Args:
        academic_term: Academic Term name (if None, gets all terms)

    Returns:
        {
            'grades': [
                {
                    'subject': 'Mathematics',
                    'term_mark': 85,
                    'exam_mark': 78,
                    'total_mark': 163,
                    'grade': 'A',
                    'teacher_comment': 'Good progress...'
                },
                ...
            ],
            'term': 'Term 1 2026',
            'term_average': 82.5
        }
    """

    # Get current user's student record
    user = frappe.session.user
    student_id = frappe.db.get_value('Student', filters={'user_id': user}, pluck='name')

    if not student_id:
        frappe.throw(_("You are not registered as a student"))

    try:
        # Build filters
        filters = {'student': student_id}

        if academic_term:
            filters['academic_term'] = academic_term

        # Get marks for student
        marks = frappe.db.get_list(
            'Mark',
            filters=filters,
            fields=[
                'subject', 'term_mark', 'exam_mark', 'academic_term',
                'grade', 'comments'
            ],
            order_by='subject asc'
        )

        if not marks:
            return {
                'grades': [],
                'term': academic_term or 'All Terms',
                'term_average': 0,
                'message': 'No marks found'
            }

        # Process marks
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
            'subject_count': len(grades)
        }

    except Exception as e:
        frappe.logger().error(f"Error getting student grades: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_student_reports():
    """
    Get list of report cards for student (for download/preview).

    Returns:
        {
            'reports': [
                {
                    'name': 'RC-001',
                    'academic_term': 'Term 1 2026',
                    'status': 'Published',
                    'created': '2026-05-15',
                    'file_url': '/api/resource/Report Card/RC-001'
                },
                ...
            ],
            'count': 3
        }
    """

    # Get current user's student record
    user = frappe.session.user
    student_id = frappe.db.get_value('Student', filters={'user_id': user}, pluck='name')

    if not student_id:
        frappe.throw(_("You are not registered as a student"))

    try:
        # Get published report cards only
        reports = frappe.db.get_list(
            'Report Card',
            filters={'student': student_id, 'docstatus': 1},
            fields=['name', 'academic_term', 'creation', 'student_name'],
            order_by='academic_term desc'
        )

        report_list = []
        for report in reports:
            report_list.append({
                'name': report['name'],
                'academic_term': report['academic_term'],
                'created': str(report['creation']).split()[0],
                'student_name': report['student_name'],
                'download_url': f'/api/resource/Report Card/{report["name"]}',
                'print_url': f'/api/method/frappe.client.get_print?doctype=Report Card&name={report["name"]}'
            })

        return {
            'reports': report_list,
            'count': len(report_list)
        }

    except Exception as e:
        frappe.logger().error(f"Error getting student reports: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_student_fees():
    """
    Get student's fee status and payment history.

    Returns:
        {
            'current_fees': [
                {
                    'academic_term': 'Term 1 2026',
                    'program': 'IGCSE Science',
                    'amount': 5000,
                    'paid': 2000,
                    'balance': 3000,
                    'status': 'Partial',
                    'due_date': '2026-03-31'
                },
                ...
            ],
            'total_amount': 15000,
            'total_paid': 8000,
            'outstanding': 7000,
            'collection_percentage': 53.3
        }
    """

    # Get current user's student record
    user = frappe.session.user
    student_id = frappe.db.get_value('Student', filters={'user_id': user}, pluck='name')

    if not student_id:
        frappe.throw(_("You are not registered as a student"))

    try:
        # Get all fees for student
        fees = frappe.db.get_list(
            'Student Fee',
            filters={'student': student_id},
            fields=['name', 'academic_term', 'program', 'amount', 'status', 'due_date'],
            order_by='academic_term desc'
        )

        current_fees = []
        total_amount = 0
        total_paid = 0

        for fee in fees:
            # Get payment history for this fee
            paid = frappe.db.get_value(
                'Student Ledger Entry',
                filters={'student_fee': fee['name'], 'docstatus': 1},
                fieldname='SUM(debit) as total_paid'
            ) or 0

            paid = float(paid)
            balance = fee['amount'] - paid

            current_fees.append({
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
            'current_fees': current_fees,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'outstanding': max(0, outstanding),
            'collection_percentage': round(collection_pct, 2),
            'fee_count': len(current_fees)
        }

    except Exception as e:
        frappe.logger().error(f"Error getting student fees: {str(e)}")
        return {'error': str(e)}
