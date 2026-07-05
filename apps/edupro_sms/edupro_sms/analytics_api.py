"""
Advanced Analytics API

Whitelisted methods for Headmaster to access academic analytics:
- get_academic_trends(academic_year): Class averages over time
- get_performance_alerts(program): At-risk/improving students
- get_subject_comparison(term, program): Subject performance analysis
- predict_final_grades(student_id): Grade projection
- get_at_risk_students(): Students with declining grades

Usage:
    frappe.call({
        method: 'edupro_sms.analytics_api.get_academic_trends',
        args: { academic_year: '2026' }
    })
"""

import frappe
from frappe import _
from datetime import datetime, timedelta
from decimal import Decimal


@frappe.whitelist()
def get_academic_trends(academic_year=None):
    """
    Get academic trends: class averages by term over time.

    Returns:
        {
            'trends': [
                {
                    'term': 'Term 1 2026',
                    'class_average': 72.5,
                    'highest_grade': 'A',
                    'lowest_grade': 'E',
                    'student_count': 200
                },
                ...
            ],
            'year': '2026'
        }
    """

    if not frappe.has_permission('Student', 'read'):
        frappe.throw(_("You do not have permission to view analytics"))

    if not academic_year:
        academic_year = frappe.db.get_value(
            'Academic Year',
            filters={'is_active': 1},
            pluck='name'
        )

    try:
        # Get all terms for this year
        terms = frappe.db.get_list(
            'Academic Term',
            filters={'academic_year': academic_year},
            fields=['name'],
            order_by='start_date asc'
        )

        trends = []

        for term in terms:
            # Get all marks for this term
            marks = frappe.db.get_list(
                'Mark',
                filters={'academic_term': term['name']},
                fields=['term_mark', 'exam_mark', 'grade']
            )

            if not marks:
                continue

            # Calculate statistics
            total_marks = sum((m['term_mark'] or 0) + (m['exam_mark'] or 0) for m in marks)
            class_avg = total_marks / (len(marks) * 2) if marks else 0

            grade_dist = {}
            for mark in marks:
                grade = mark['grade'] or 'N/A'
                grade_dist[grade] = grade_dist.get(grade, 0) + 1

            highest = max(grade_dist.keys()) if grade_dist else 'N/A'
            lowest = min(grade_dist.keys()) if grade_dist else 'N/A'

            trends.append({
                'term': term['name'],
                'class_average': round(class_avg, 2),
                'highest_grade': highest,
                'lowest_grade': lowest,
                'student_count': len(marks)
            })

        return {'trends': trends, 'year': academic_year}

    except Exception as e:
        frappe.logger().error(f"Error getting academic trends: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_performance_alerts(program=None, academic_term=None):
    """
    Get performance alerts: at-risk and improving students.

    Returns:
        {
            'at_risk': [
                {'student_name', 'trend', 'current_avg', 'previous_avg', 'grade'},
                ...
            ],
            'improving': [...],
            'declining': [...]
        }
    """

    if not frappe.has_permission('Student', 'read'):
        frappe.throw(_("You do not have permission to view analytics"))

    if not academic_term:
        academic_term = frappe.db.get_value(
            'Academic Term',
            filters={'is_active': 1},
            pluck='name'
        )

    try:
        # Get current marks
        filters = {'academic_term': academic_term}
        if program:
            filters['program'] = program

        current_marks = frappe.db.get_list(
            'Mark',
            filters=filters,
            fields=['student', 'term_mark', 'exam_mark'],
            order_by='student asc'
        )

        # Group by student
        student_marks = {}
        for mark in current_marks:
            student = mark['student']
            total = (mark['term_mark'] or 0) + (mark['exam_mark'] or 0)
            if student not in student_marks:
                student_marks[student] = []
            student_marks[student].append(total)

        # Calculate averages
        student_avgs = {}
        for student, marks in student_marks.items():
            avg = sum(marks) / len(marks) if marks else 0
            student_avgs[student] = avg

        # Get previous term average
        prev_term = frappe.db.get_value(
            'Academic Term',
            filters={'academic_year': academic_term},
            fieldname='name',
            order_by='start_date desc',
            limit_page_length=2
        )

        # Identify alerts
        at_risk = []
        improving = []
        declining = []

        for student, current_avg in student_avgs.items():
            # At-risk: below 50%
            if current_avg < 50:
                student_name = frappe.db.get_value('Student', student, 'student_name')
                at_risk.append({
                    'student_name': student_name,
                    'student_id': student,
                    'current_avg': round(current_avg, 2),
                    'trend': 'at_risk',
                    'grade': 'F'
                })

            # Improving: 20+ point increase
            if prev_term:
                prev_marks = frappe.db.get_list(
                    'Mark',
                    filters={'student': student, 'academic_term': prev_term},
                    fields=['term_mark', 'exam_mark']
                )
                if prev_marks:
                    prev_avg = sum((m['term_mark'] or 0) + (m['exam_mark'] or 0) for m in prev_marks) / (len(prev_marks) * 2)
                    if current_avg - prev_avg >= 20:
                        student_name = frappe.db.get_value('Student', student, 'student_name')
                        improving.append({
                            'student_name': student_name,
                            'current_avg': round(current_avg, 2),
                            'previous_avg': round(prev_avg, 2),
                            'trend': 'improving'
                        })
                    elif prev_avg - current_avg >= 20:
                        student_name = frappe.db.get_value('Student', student, 'student_name')
                        declining.append({
                            'student_name': student_name,
                            'current_avg': round(current_avg, 2),
                            'previous_avg': round(prev_avg, 2),
                            'trend': 'declining'
                        })

        return {
            'at_risk': at_risk[:20],  # Top 20
            'improving': improving[:10],
            'declining': declining[:10]
        }

    except Exception as e:
        frappe.logger().error(f"Error getting performance alerts: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_subject_comparison(academic_term=None, program=None):
    """
    Compare average performance across subjects.

    Returns:
        {
            'subjects': [
                {
                    'subject': 'Mathematics',
                    'average': 78.5,
                    'student_count': 200,
                    'grade_distribution': {'A': 50, 'B': 80, 'C': 60, ...}
                },
                ...
            ]
        }
    """

    if not frappe.has_permission('Student', 'read'):
        frappe.throw(_("You do not have permission to view analytics"))

    if not academic_term:
        academic_term = frappe.db.get_value(
            'Academic Term',
            filters={'is_active': 1},
            pluck='name'
        )

    try:
        filters = {'academic_term': academic_term}
        if program:
            filters['program'] = program

        marks = frappe.db.get_list(
            'Mark',
            filters=filters,
            fields=['subject', 'term_mark', 'exam_mark', 'grade']
        )

        # Group by subject
        subject_stats = {}
        for mark in marks:
            subject = mark['subject']
            if subject not in subject_stats:
                subject_stats[subject] = {
                    'marks': [],
                    'grades': {}
                }

            total = (mark['term_mark'] or 0) + (mark['exam_mark'] or 0)
            subject_stats[subject]['marks'].append(total)

            grade = mark['grade'] or 'N/A'
            subject_stats[subject]['grades'][grade] = subject_stats[subject]['grades'].get(grade, 0) + 1

        # Calculate averages
        subjects = []
        for subject, stats in sorted(subject_stats.items()):
            avg = sum(stats['marks']) / len(stats['marks']) if stats['marks'] else 0
            subjects.append({
                'subject': subject,
                'average': round(avg, 2),
                'student_count': len(stats['marks']),
                'grade_distribution': stats['grades']
            })

        return {'subjects': subjects}

    except Exception as e:
        frappe.logger().error(f"Error getting subject comparison: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def predict_final_grades(student_id, academic_term=None):
    """
    Predict final grades based on current performance.

    Returns:
        {
            'student_name': 'John Doe',
            'current_average': 78.5,
            'predicted_grade': 'B',
            'confidence': 0.85,
            'trend': 'stable'
        }
    """

    if not frappe.has_permission('Student', 'read'):
        frappe.throw(_("You do not have permission to view analytics"))

    if not academic_term:
        academic_term = frappe.db.get_value(
            'Academic Term',
            filters={'is_active': 1},
            pluck='name'
        )

    try:
        student_doc = frappe.get_doc('Student', student_id)

        # Get current marks
        marks = frappe.db.get_list(
            'Mark',
            filters={'student': student_id, 'academic_term': academic_term},
            fields=['term_mark', 'exam_mark']
        )

        if not marks:
            return {'error': 'No marks found for student'}

        current_avg = sum((m['term_mark'] or 0) + (m['exam_mark'] or 0) for m in marks) / (len(marks) * 2)

        # Simple prediction: assume same performance continues
        # For a final prediction, we'd use more complex ML models
        predicted = current_avg

        # Grade mapping
        if predicted >= 90:
            predicted_grade = 'A'
        elif predicted >= 80:
            predicted_grade = 'B'
        elif predicted >= 70:
            predicted_grade = 'C'
        elif predicted >= 60:
            predicted_grade = 'D'
        else:
            predicted_grade = 'E'

        # Confidence: higher if more consistent marks
        marks_list = [(m['term_mark'] or 0) + (m['exam_mark'] or 0) for m in marks]
        variance = sum((x - current_avg) ** 2 for x in marks_list) / len(marks_list) if marks_list else 0
        confidence = max(0.5, 1 - (variance / 1000))  # Normalize to 0.5-1.0

        return {
            'student_name': student_doc.student_name,
            'student_id': student_id,
            'current_average': round(current_avg, 2),
            'predicted_grade': predicted_grade,
            'confidence': round(confidence, 2),
            'trend': 'stable'
        }

    except Exception as e:
        frappe.logger().error(f"Error predicting grades: {str(e)}")
        return {'error': str(e)}


@frappe.whitelist()
def get_at_risk_students(academic_term=None, threshold=50):
    """
    Get students at risk (below threshold average).

    Returns:
        {
            'at_risk': [
                {'student_name', 'average', 'status', 'days_to_action'},
                ...
            ],
            'count': 25
        }
    """

    if not frappe.has_permission('Student', 'read'):
        frappe.throw(_("You do not have permission to view analytics"))

    if not academic_term:
        academic_term = frappe.db.get_value(
            'Academic Term',
            filters={'is_active': 1},
            pluck='name'
        )

    try:
        marks = frappe.db.get_list(
            'Mark',
            filters={'academic_term': academic_term},
            fields=['student', 'term_mark', 'exam_mark'],
            order_by='student asc'
        )

        # Group by student
        student_avgs = {}
        for mark in marks:
            student = mark['student']
            total = (mark['term_mark'] or 0) + (mark['exam_mark'] or 0)
            if student not in student_avgs:
                student_avgs[student] = []
            student_avgs[student].append(total)

        # Find at-risk
        at_risk = []
        for student, mark_list in student_avgs.items():
            avg = sum(mark_list) / len(mark_list) if mark_list else 0
            if avg < threshold:
                student_name = frappe.db.get_value('Student', student, 'student_name')
                at_risk.append({
                    'student_name': student_name,
                    'student_id': student,
                    'average': round(avg, 2),
                    'status': 'Critical' if avg < 40 else 'At Risk',
                    'days_to_action': 7
                })

        return {
            'at_risk': sorted(at_risk, key=lambda x: x['average'])[:50],
            'count': len(at_risk)
        }

    except Exception as e:
        frappe.logger().error(f"Error getting at-risk students: {str(e)}")
        return {'error': str(e)}
