"""
Import Handler Module — Bulk Data Import API

Whitelisted server methods for handling bulk imports with:
- Preview mode (shows 5 records, validation results, total count)
- Actual import with transaction rollback on error
- Progress tracking & audit logging
- Duplicate detection & skipping

Usage:
    from edupro_sms.import_handler import import_bulk_data
    result = import_bulk_data('Student', file_data, preview=True)
"""

import frappe
from frappe import _
import json
import traceback
from datetime import datetime
from typing import Dict, List

from .import_parser import parse_and_validate_file
from .bursar_student_management import _current_academic_year


class ImportLog:
    """Track import operations for audit trail"""

    def __init__(self, doctype: str, user: str):
        self.doctype = doctype
        self.user = user
        self.timestamp = datetime.now()
        self.records_imported = 0
        self.records_skipped = 0
        self.records_failed = 0
        self.errors = []

    def log_success(self, record_num: int, doc_name: str):
        """Log successful import"""
        self.records_imported += 1

    def log_skip(self, record_num: int, reason: str):
        """Log skipped record"""
        self.records_skipped += 1
        self.errors.append({
            'row': record_num,
            'status': 'skipped',
            'reason': reason
        })

    def log_error(self, record_num: int, error_msg: str):
        """Log failed import"""
        self.records_failed += 1
        self.errors.append({
            'row': record_num,
            'status': 'error',
            'message': error_msg
        })

    def to_dict(self):
        return {
            'doctype': self.doctype,
            'user': self.user,
            'timestamp': self.timestamp.isoformat(),
            'records_imported': self.records_imported,
            'records_skipped': self.records_skipped,
            'records_failed': self.records_failed,
            'total': self.records_imported + self.records_skipped + self.records_failed,
            'errors': self.errors
        }


def create_student_from_record(record: Dict, import_log: ImportLog, row_num: int) -> str:
    """Create a Student DocType from import record"""

    email = str(record.get('Email', '')).strip()

    # Check for duplicates. Student has no admission_number field at all
    # (real Education-app schema), and email is stored as student_email_id.
    existing = frappe.db.get_value('Student', filters={'student_email_id': email}, pluck='name')
    if existing:
        import_log.log_skip(row_num, f"Student with email '{email}' already exists")
        return None

    # Gender is a Link to the Gender doctype ("Male"/"Female"), not a
    # plain M/F value -- map the CSV's documented M/F shorthand across.
    gender_code = str(record.get('Gender', 'M')).strip().upper()
    gender = 'Female' if gender_code == 'F' else 'Male'

    # first_name/last_name are the real source of truth -- Education's own
    # Student.set_title() recomputes student_name from them on every
    # validate(), and validate_user()'s auto-created User doc requires
    # first_name directly. Setting only student_name (as before) leaves
    # first_name empty and fails User creation.
    name_parts = str(record.get('Student Name', '')).strip().split(' ', 1)
    first_name = name_parts[0] if name_parts else ''
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    try:
        student = frappe.get_doc({
            'doctype': 'Student',
            'name': frappe.generate_hash('Student', 10),  # Auto-generate ID
            'first_name': first_name,
            'last_name': last_name,
            'student_email_id': email,
            'date_of_birth': record.get('Date of Birth'),
            'gender': gender,
            'boarding_type': record.get('Boarding Type', 'Day Boarder'),
            'enabled': 1,
        })

        student.insert(ignore_permissions=True)

        # Enroll in program if provided. Program Enrollment has no
        # student_group field at all -- real class/Student Group
        # membership lives on a separate child table (Student Group's
        # own "students" table), a different mechanism this doesn't
        # attempt to wire up. The "Student Group (Class)" CSV column is
        # accepted but not yet applied anywhere.
        if record.get('Program'):
            program_name = str(record['Program']).strip()

            try:
                enrollment = frappe.get_doc({
                    'doctype': 'Program Enrollment',
                    'student': student.name,
                    'program': program_name,
                    'academic_year': _current_academic_year() or 'Academic Year',
                })
                enrollment.insert(ignore_permissions=True)
            except Exception as e:
                import_log.log_error(row_num, f"Enrollment failed: {str(e)}")
                return None

        import_log.log_success(row_num, student.name)
        return student.name

    except Exception as e:
        import_log.log_error(row_num, str(e))
        frappe.logger().error(f"Student import error (row {row_num}): {traceback.format_exc()}")
        return None


def create_instructor_from_record(record: Dict, import_log: ImportLog, row_num: int) -> str:
    """Create an Instructor (User + Instructor DocType) from import record"""

    email = str(record.get('Email', '')).strip()

    # Check if user already exists
    existing_user = frappe.db.get_value('User', filters={'email': email}, pluck='name')
    if existing_user:
        import_log.log_skip(row_num, f"User with email '{email}' already exists")
        return None

    try:
        # Create User first
        user = frappe.get_doc({
            'doctype': 'User',
            'email': email,
            'first_name': str(record.get('Instructor Name', '')).strip(),
            'user_type': 'System User',
            'roles': [{'role': 'Instructor'}]
        })
        user.insert(ignore_permissions=True)

        # Create Instructor DocType
        instructor = frappe.get_doc({
            'doctype': 'Instructor',
            'user': user.email,
            'instructor_name': str(record.get('Instructor Name', '')).strip(),
        })
        instructor.insert(ignore_permissions=True)

        # Handle class teacher assignment if applicable
        is_class_teacher = str(record.get('Class Teacher', 'No')).strip().lower() == 'yes'
        if is_class_teacher and record.get('Class Teacher For'):
            class_name = str(record['Class Teacher For']).strip()
            try:
                student_group = frappe.get_doc('Student Group', class_name)
                student_group.class_teacher = user.email
                student_group.save(ignore_permissions=True)
            except Exception as e:
                import_log.log_error(row_num, f"Class teacher assignment failed: {str(e)}")

        import_log.log_success(row_num, user.email)
        return user.email

    except Exception as e:
        import_log.log_error(row_num, str(e))
        frappe.logger().error(f"Instructor import error (row {row_num}): {traceback.format_exc()}")
        return None


def create_guardian_from_record(record: Dict, import_log: ImportLog, row_num: int) -> str:
    """Create a Guardian from import record"""

    email = str(record.get('Email', '')).strip()

    # Guardian has no status field, and email is stored as email_address.
    existing = frappe.db.get_value('Guardian', filters={'email_address': email}, pluck='name')
    if existing:
        import_log.log_skip(row_num, f"Guardian with email '{email}' already exists")
        return None

    try:
        guardian = frappe.get_doc({
            'doctype': 'Guardian',
            'guardian_name': str(record.get('Guardian Name', '')).strip(),
            'email_address': email,
        })

        guardian.insert(ignore_permissions=True)

        # Link students
        student_ids = [s.strip() for s in str(record.get('Student IDs', '')).split(',')]
        for student_id in student_ids:
            if student_id:
                try:
                    # Update Student to link guardian
                    student_doc = frappe.get_doc('Student', student_id)
                    if guardian.name not in [g.get('guardian') for g in student_doc.get('guardians', [])]:
                        student_doc.append('guardians', {'guardian': guardian.name})
                        student_doc.save(ignore_permissions=True)
                except Exception as e:
                    import_log.log_error(row_num, f"Guardian-student linking failed: {str(e)}")

        import_log.log_success(row_num, guardian.name)
        return guardian.name

    except Exception as e:
        import_log.log_error(row_num, str(e))
        frappe.logger().error(f"Guardian import error (row {row_num}): {traceback.format_exc()}")
        return None


def create_assessment_plan_from_record(record: Dict, import_log: ImportLog, row_num: int) -> str:
    """Create an Assessment Plan from import record"""

    try:
        exam_name = str(record.get('Exam Name', 'Assessment')).strip()
        student_group = str(record.get('Class (Student Group)', '')).strip()
        course = str(record.get('Subject (Course)', '')).strip()

        # Generate unique name
        plan_name = f"{student_group}-{course}-{exam_name}".replace(' ', '_')

        # Check if already exists. Assessment Plan has no "exam" field --
        # the real field is assessment_name.
        existing = frappe.db.get_value(
            'Assessment Plan',
            filters={
                'student_group': student_group,
                'course': course,
                'assessment_name': exam_name
            },
            pluck='name'
        )

        if existing:
            import_log.log_skip(row_num, f"Assessment Plan '{plan_name}' already exists")
            return None

        # Parse time fields. Real fields are from_time/to_time, not
        # start_time/end_time.
        start_time = None
        end_time = None

        if record.get('Start Time'):
            try:
                start_time = record['Start Time']
            except:
                pass

        if record.get('End Time'):
            try:
                end_time = record['End Time']
            except:
                pass

        assessment_plan = frappe.get_doc({
            'doctype': 'Assessment Plan',
            'student_group': student_group,
            'course': course,
            'academic_term': record.get('Academic Term'),
            'assessment_name': exam_name,
            'schedule_date': record.get('Schedule Date'),
            'from_time': start_time,
            'to_time': end_time,
        })

        assessment_plan.insert(ignore_permissions=True)
        import_log.log_success(row_num, assessment_plan.name)
        return assessment_plan.name

    except Exception as e:
        import_log.log_error(row_num, str(e))
        frappe.logger().error(f"Assessment Plan import error (row {row_num}): {traceback.format_exc()}")
        return None


# Mapping of DocType to creation function
CREATOR_FUNCTIONS = {
    'Student': create_student_from_record,
    'Instructor': create_instructor_from_record,
    'Guardian': create_guardian_from_record,
    'Assessment Plan': create_assessment_plan_from_record,
}


@frappe.whitelist()
def import_bulk_data(doctype: str, file_path: str, preview: bool = True) -> Dict:
    """
    Whitelist method: Import bulk data with optional preview mode

    Args:
        doctype: 'Student', 'Instructor', 'Guardian', or 'Assessment Plan'
        file_path: Path to CSV or XLSX file
        preview: If True, show preview (5 records) without importing

    Returns:
        Dict with:
        - mode: 'preview' or 'import'
        - valid_records: List of valid records
        - invalid_records: List of invalid records
        - import_log: Summary of actual import (if preview=False)
        - message: Human-readable summary
    """

    # Permission check
    if not frappe.has_permission('Student', 'create'):
        frappe.throw(_("You do not have permission to import data"))

    # Validate doctype
    if doctype not in CREATOR_FUNCTIONS:
        frappe.throw(f"Unsupported doctype: {doctype}")

    # Parse and validate
    try:
        validation_result = parse_and_validate_file(file_path, doctype)
    except Exception as e:
        frappe.logger().error(f"Validation failed: {traceback.format_exc()}")
        return {
            'success': False,
            'message': f"Validation failed: {str(e)}",
            'errors': []
        }

    valid_records = validation_result.get('valid_records', [])
    invalid_records = validation_result.get('invalid_records', [])

    # PREVIEW MODE: Show results without importing
    if preview:
        preview_records = valid_records[:5]  # First 5 records
        return {
            'mode': 'preview',
            'success': True,
            'preview_records': [r['data'] for r in preview_records],
            'total_valid': len(valid_records),
            'total_invalid': len(invalid_records),
            'invalid_sample': invalid_records[:5] if invalid_records else [],
            'message': f"Preview: {len(valid_records)} valid records, {len(invalid_records)} invalid. "
                      f"First 5 records shown. Confirm to proceed with import."
        }

    # ACTUAL IMPORT MODE: Import all valid records
    import_log = ImportLog(doctype, frappe.session.user)
    creator_func = CREATOR_FUNCTIONS[doctype]

    try:
        # No explicit frappe.db.begin() -- Frappe already wraps every
        # request in its own transaction, and calling begin() again on
        # top of pending writes trips Frappe's own ImplicitCommitError
        # guard. commit()/rollback() below are enough.
        for record_dict in valid_records:
            row_num = record_dict['row_num']
            record = record_dict['data']

            creator_func(record, import_log, row_num)

        frappe.db.commit()  # Commit if all successful

    except Exception as e:
        frappe.db.rollback()  # Rollback on error
        frappe.logger().error(f"Import failed, rolled back: {traceback.format_exc()}")

        return {
            'mode': 'import',
            'success': False,
            'message': f"Import failed and rolled back: {str(e)}",
            'import_log': import_log.to_dict()
        }

    # Success response
    return {
        'mode': 'import',
        'success': True,
        'message': f"Import complete: {import_log.records_imported} imported, "
                  f"{import_log.records_skipped} skipped, "
                  f"{import_log.records_failed} failed.",
        'import_log': import_log.to_dict()
    }


@frappe.whitelist()
def get_import_history(doctype: str, limit: int = 10) -> List[Dict]:
    """
    Get recent import history for a DocType

    Args:
        doctype: 'Student', 'Instructor', 'Guardian', or 'Assessment Plan'
        limit: Number of records to return (default 10)

    Returns:
        List of import logs
    """
    try:
        # Query import logs from database (would need a dedicated doctype for this)
        # For now, return empty list (can be implemented with a custom doctype)
        return []
    except Exception as e:
        frappe.logger().error(f"Import history retrieval failed: {str(e)}")
        return []
