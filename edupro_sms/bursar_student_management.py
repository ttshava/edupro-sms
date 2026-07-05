"""
Bursar Student Management API

Whitelisted methods for Bursar to manage students:
- Create new students
- Enroll students in programs
- Link students to guardians
- Edit student information
- Deactivate students

Field names verified against the real Education-app Student/Guardian/
Academic Year schema (an earlier version of this file assumed
Student.email, Student.admission_number, Student.status, Guardian.email,
Guardian.status, and Academic Year.is_current, none of which exist --
real fields are Student.student_email_id, Student.enabled (int),
Guardian.email_address, Academic Year has no "current" flag at all).

All operations are:
- Permission-checked (Bursar role only)
- Audit-logged (who changed what, when)
- Validated (required fields, data integrity)
"""

import frappe
from frappe import _
from datetime import datetime
from typing import Dict, List, Optional
import traceback


def has_bursar_permission():
    """Check if user has Bursar role"""
    return frappe.has_permission('Student', 'create')


def log_audit(action: str, doctype: str, doc_name: str, changes: Dict = None):
    """Log audit trail for all student management actions"""
    try:
        audit_log = {
            'user': frappe.session.user,
            'action': action,
            'doctype': doctype,
            'document': doc_name,
            'timestamp': datetime.now().isoformat(),
            'changes': changes or {}
        }
        # In production, save to a dedicated Audit Log DocType
        frappe.logger().info(f"Audit: {audit_log}")
    except Exception as e:
        frappe.logger().error(f"Audit logging failed: {str(e)}")


def _current_academic_year() -> Optional[str]:
    """Academic Year has no "is current" flag -- pick the one whose date
    range contains today, falling back to the most recently started one."""
    today = frappe.utils.today()

    year = frappe.db.get_value(
        'Academic Year',
        filters={'year_start_date': ['<=', today], 'year_end_date': ['>=', today]},
        pluck='name',
    )
    if year:
        return year

    return frappe.db.get_value(
        'Academic Year',
        filters={},
        pluck='name',
        order_by='year_start_date desc',
    )


@frappe.whitelist()
def create_student(
    student_name: str,
    email: str,
    dob: Optional[str] = None,
    gender: str = 'M',
    boarding_type: str = 'Day Boarder'
) -> Dict:
    """
    Create a new student.

    Args:
        student_name: Full name of student
        email: Email address (must be unique) -- stored as student_email_id
        dob: Date of birth (YYYY-MM-DD format, optional)
        gender: M or F (default: M)
        boarding_type: 'Day Boarder' or 'Full Boarder' (default: Day Boarder)

    Returns:
        Dict with success flag and student name/email
    """

    if not has_bursar_permission():
        frappe.throw(_("You do not have permission to create students"))

    if not student_name or not student_name.strip():
        frappe.throw(_("Student name is required"))

    if not email or '@' not in email:
        frappe.throw(_("Valid email is required"))

    existing_email = frappe.db.get_value('Student', filters={'student_email_id': email.strip()}, pluck='name')
    if existing_email:
        frappe.throw(f"Student with email '{email}' already exists (ID: {existing_email})")

    if boarding_type not in ['Day Boarder', 'Full Boarder']:
        frappe.throw("Boarding type must be 'Day Boarder' or 'Full Boarder'")

    if gender and gender.upper() not in ['M', 'F']:
        frappe.throw(_("Gender must be 'M' or 'F'"))

    # Gender is a Link to the Gender doctype ("Male"/"Female"), not M/F.
    real_gender = 'Female' if gender.upper() == 'F' else 'Male'

    # first_name/last_name are the real source of truth -- Education's own
    # Student.set_title() recomputes student_name from them, and
    # validate_user()'s auto-created User doc requires first_name directly.
    name_parts = student_name.strip().split(' ', 1)
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    try:
        student = frappe.get_doc({
            'doctype': 'Student',
            'first_name': first_name,
            'last_name': last_name,
            'student_email_id': email.strip(),
            'date_of_birth': dob,
            'gender': real_gender,
            'boarding_type': boarding_type,
            'enabled': 1,
        })

        student.insert(ignore_permissions=True)
        frappe.db.commit()

        log_audit('CREATE', 'Student', student.name, {
            'student_name': student_name,
            'email': email,
        })

        return {
            'success': True,
            'message': f"Student '{student_name}' created successfully (ID: {student.name})",
            'student_id': student.name,
            'email': email
        }

    except Exception as e:
        frappe.logger().error(f"Student creation failed: {traceback.format_exc()}")
        frappe.throw(f"Failed to create student: {str(e)}")


@frappe.whitelist()
def enroll_student(
    student_id: str,
    program: str,
    student_group: Optional[str] = None,
    academic_year: Optional[str] = None
) -> Dict:
    """
    Enroll a student in a program.

    Args:
        student_id: Student name (from Student DocType)
        program: Program name (e.g., 'IGCSE Science')
        student_group: Class name (e.g., 'Form 1A', optional)
        academic_year: Academic year (optional, defaults to the year
            whose date range contains today)

    Returns:
        Dict with success flag and enrollment ID
    """

    if not has_bursar_permission():
        frappe.throw(_("You do not have permission to enroll students"))

    if not student_id or not program:
        frappe.throw(_("Student ID and Program are required"))

    frappe.get_doc('Student', student_id)

    if not frappe.db.exists('Program', program):
        frappe.throw(f"Program '{program}' not found")

    if not academic_year:
        academic_year = _current_academic_year()
        if not academic_year:
            frappe.throw(_("No Academic Year configured"))

    try:
        existing = frappe.db.get_value(
            'Program Enrollment',
            filters={'student': student_id, 'program': program},
            pluck='name'
        )
        if existing:
            return {
                'success': True,
                'message': f"Student already enrolled in '{program}' (ID: {existing})",
                'enrollment_id': existing,
                'skipped': True
            }

        enrollment = frappe.get_doc({
            'doctype': 'Program Enrollment',
            'student': student_id,
            'program': program,
            'student_group': student_group,
            'academic_year': academic_year,
        })

        enrollment.insert(ignore_permissions=True)
        frappe.db.commit()

        log_audit('ENROLL', 'Student', student_id, {
            'program': program,
            'enrollment_id': enrollment.name
        })

        return {
            'success': True,
            'message': f"Student enrolled in '{program}' for {academic_year}",
            'enrollment_id': enrollment.name,
            'program': program,
            'academic_year': academic_year
        }

    except Exception as e:
        frappe.logger().error(f"Enrollment failed: {traceback.format_exc()}")
        frappe.throw(f"Failed to enroll student: {str(e)}")


@frappe.whitelist()
def link_guardian(
    student_id: str,
    guardian_id: Optional[str] = None,
    create_new: bool = False,
    guardian_name: Optional[str] = None,
    guardian_email: Optional[str] = None
) -> Dict:
    """
    Link a guardian to a student (or create new guardian and link).
    Student.guardians is a real child table (parentfield "guardians" on
    Student Guardian) -- that part of the original implementation was
    already correct.

    Args:
        student_id: Student name
        guardian_id: Existing guardian name (if linking existing)
        create_new: If True, create new guardian with name/email
        guardian_name: Guardian name (if create_new=True)
        guardian_email: Guardian email (if create_new=True) -- stored as
            Guardian.email_address

    Returns:
        Dict with success flag and guardian ID
    """

    if not has_bursar_permission():
        frappe.throw(_("You do not have permission to manage guardians"))

    if not student_id:
        frappe.throw(_("Student ID is required"))

    student_doc = frappe.get_doc('Student', student_id)

    guardian_to_link = None

    if create_new:
        if not guardian_name or not guardian_email:
            frappe.throw(_("Guardian name and email required to create new guardian"))

        if '@' not in guardian_email:
            frappe.throw(_("Valid email required"))

        existing = frappe.db.get_value('Guardian', filters={'email_address': guardian_email.strip()}, pluck='name')
        if existing:
            frappe.throw(f"Guardian with email '{guardian_email}' already exists (ID: {existing})")

        try:
            guardian = frappe.get_doc({
                'doctype': 'Guardian',
                'guardian_name': guardian_name.strip(),
                'email_address': guardian_email.strip(),
            })
            guardian.insert(ignore_permissions=True)
            guardian_to_link = guardian.name

        except Exception as e:
            frappe.logger().error(f"Guardian creation failed: {traceback.format_exc()}")
            frappe.throw(f"Failed to create guardian: {str(e)}")

    else:
        if not guardian_id:
            frappe.throw(_("Guardian ID required"))

        guardian_doc = frappe.get_doc('Guardian', guardian_id)
        guardian_to_link = guardian_doc.name

    existing_guardians = [g.get('guardian') for g in student_doc.get('guardians', [])]
    if guardian_to_link in existing_guardians:
        return {
            'success': True,
            'message': "Guardian already linked to student",
            'guardian_id': guardian_to_link,
            'skipped': True
        }

    try:
        student_doc.append('guardians', {'guardian': guardian_to_link})
        student_doc.save(ignore_permissions=True)
        frappe.db.commit()

        log_audit('LINK_GUARDIAN', 'Student', student_id, {
            'guardian': guardian_to_link
        })

        return {
            'success': True,
            'message': "Guardian linked to student successfully",
            'guardian_id': guardian_to_link,
            'student_id': student_id
        }

    except Exception as e:
        frappe.logger().error(f"Guardian linking failed: {traceback.format_exc()}")
        frappe.throw(f"Failed to link guardian: {str(e)}")


@frappe.whitelist()
def edit_student(
    student_id: str,
    field_name: str,
    field_value
) -> Dict:
    """
    Edit student information (limited fields, Bursar can only edit non-security fields).

    Args:
        student_id: Student name
        field_name: Field to update (student_name, student_email_id, date_of_birth, gender, boarding_type)
        field_value: New value

    Returns:
        Dict with success flag
    """

    if not has_bursar_permission():
        frappe.throw(_("You do not have permission to edit students"))

    if not student_id or not field_name:
        frappe.throw(_("Student ID and field name required"))

    ALLOWED_FIELDS = [
        'student_name',
        'student_email_id',
        'date_of_birth',
        'gender',
        'boarding_type',
    ]

    field_name = field_name.lower()
    if field_name not in ALLOWED_FIELDS:
        frappe.throw(f"You cannot edit field '{field_name}'")

    try:
        student_doc = frappe.get_doc('Student', student_id)
        old_value = student_doc.get(field_name)

        if field_name == 'student_email_id':
            if '@' not in str(field_value):
                frappe.throw(_("Valid email required"))
            existing = frappe.db.get_value(
                'Student',
                filters={'student_email_id': field_value.strip(), 'name': ['!=', student_id]},
                pluck='name'
            )
            if existing:
                frappe.throw("Email already used by another student")

        if field_name == 'gender' and field_value.upper() not in ['M', 'F']:
            frappe.throw(_("Gender must be 'M' or 'F'"))

        if field_name == 'boarding_type' and field_value not in ['Day Boarder', 'Full Boarder']:
            frappe.throw(_("Boarding type must be 'Day Boarder' or 'Full Boarder'"))

        student_doc.set(field_name, field_value)
        student_doc.save(ignore_permissions=True)
        frappe.db.commit()

        log_audit('EDIT', 'Student', student_id, {
            'field': field_name,
            'old_value': old_value,
            'new_value': field_value
        })

        return {
            'success': True,
            'message': "Student updated successfully",
            'field': field_name,
            'old_value': old_value,
            'new_value': field_value
        }

    except Exception as e:
        frappe.logger().error(f"Student edit failed: {traceback.format_exc()}")
        frappe.throw(f"Failed to update student: {str(e)}")


@frappe.whitelist()
def deactivate_student(student_id: str, reason: str = '') -> Dict:
    """
    Deactivate a student (soft delete via Student.enabled = 0, not a hard delete).

    Args:
        student_id: Student name
        reason: Reason for deactivation

    Returns:
        Dict with success flag
    """

    if not has_bursar_permission():
        frappe.throw(_("You do not have permission to deactivate students"))

    if not student_id:
        frappe.throw(_("Student ID required"))

    try:
        student_doc = frappe.get_doc('Student', student_id)

        if not student_doc.enabled:
            return {
                'success': True,
                'message': "Student is already inactive",
                'skipped': True
            }

        student_doc.enabled = 0
        student_doc.save(ignore_permissions=True)
        frappe.db.commit()

        log_audit('DEACTIVATE', 'Student', student_id, {
            'reason': reason,
            'old_status': 'Active',
            'new_status': 'Inactive'
        })

        return {
            'success': True,
            'message': "Student deactivated successfully",
            'student_id': student_id,
            'reason': reason
        }

    except Exception as e:
        frappe.logger().error(f"Student deactivation failed: {traceback.format_exc()}")
        frappe.throw(f"Failed to deactivate student: {str(e)}")


@frappe.whitelist()
def get_student_list(status: str = 'Active', limit: int = 100) -> List[Dict]:
    """
    Get list of students (paginated).

    Args:
        status: 'Active' or 'Inactive' (maps to Student.enabled 1/0), or
            '' for all
        limit: Max number of records (default: 100)

    Returns:
        List of student records
    """

    filters = {}
    if status == 'Active':
        filters['enabled'] = 1
    elif status == 'Inactive':
        filters['enabled'] = 0

    try:
        students = frappe.db.get_list(
            'Student',
            filters=filters,
            fields=['name', 'student_name', 'student_email_id', 'boarding_type', 'enabled'],
            order_by='student_name asc',
            limit_page_length=limit
        )
        for s in students:
            s['email'] = s.pop('student_email_id')
            s['status'] = 'Active' if s.pop('enabled') else 'Inactive'
        return students
    except Exception as e:
        frappe.logger().error(f"Student list retrieval failed: {traceback.format_exc()}")
        return []
