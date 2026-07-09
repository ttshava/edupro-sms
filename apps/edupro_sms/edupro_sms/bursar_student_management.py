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

        # Education's own Student.validate_user() creates the linked User
        # with send_welcome_email=1 (unlike our own _create_user() helper
        # for Guardians/Instructors, which always sets 0) -- with real SMTP
        # configured, a bounce on that welcome email raises and aborts the
        # whole student creation. Mute it here for consistency with every
        # other role: nobody gets an automatic core Frappe welcome email.
        original_mute = frappe.flags.mute_emails
        frappe.flags.mute_emails = True
        try:
            student.insert(ignore_permissions=True)
        finally:
            frappe.flags.mute_emails = original_mute
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


def _elective_groups_for(program: str) -> Dict[str, List[str]]:
    """Map of elective_group name -> list of course options, for whichever
    Program Course rows on this Program have a non-blank elective_group.
    A Program with no elective groups returns {}."""
    rows = frappe.get_all(
        'Program Course',
        filters={'parent': program, 'elective_group': ['is', 'set']},
        fields=['course', 'elective_group'],
    )
    groups: Dict[str, List[str]] = {}
    for row in rows:
        if row.elective_group:
            groups.setdefault(row.elective_group, []).append(row.course)
    return groups


def _sync_program_enrollment_courses(enrollment_name: str, program: str, electives: Optional[Dict[str, str]] = None) -> None:
    """Populate Program Enrollment.courses: every required=1 Program
    Course, plus one elective per elective_group if a valid choice was
    given. Never removes a course the student already has -- swapping an
    elective is update_student_elective()'s job, not this one's."""
    enrollment = frappe.get_doc('Program Enrollment', enrollment_name)
    existing_courses = {row.course for row in enrollment.courses}
    changed = False

    required = frappe.get_all(
        'Program Course', filters={'parent': program, 'required': 1}, fields=['course']
    )
    for row in required:
        if row.course not in existing_courses:
            enrollment.append('courses', {'course': row.course})
            existing_courses.add(row.course)
            changed = True

    # Programs like A-Level's Lower/Upper 6 model "pick 3 from one pool" as
    # 3 elective groups with an IDENTICAL option list (Subject Choice 1/2/3)
    # -- group by the option set itself so "already satisfied" is judged by
    # how many DISTINCT choices from that shared pool exist, not by "does
    # any existing course happen to also be a valid option here" (which,
    # for identical pools, is true again the moment the first slot fills,
    # silently skipping every other slot).
    elective_groups = _elective_groups_for(program)
    pools: Dict[tuple, List[str]] = {}
    for group_name, options in elective_groups.items():
        pools.setdefault(tuple(sorted(options)), []).append(group_name)

    for pool_key, group_names in pools.items():
        options = list(pool_key)
        needed = len(group_names)
        already_chosen = [c for c in existing_courses if c in options]
        still_needed = needed - len(already_chosen)
        if still_needed <= 0:
            continue

        candidates = []
        for g in group_names:
            chosen = (electives or {}).get(g)
            if chosen and chosen not in already_chosen and chosen not in candidates:
                candidates.append(chosen)

        for chosen in candidates[:still_needed]:
            if chosen not in options:
                frappe.throw(_("'{0}' is not a valid choice for this elective.").format(chosen))
            enrollment.append('courses', {'course': chosen})
            existing_courses.add(chosen)
            already_chosen.append(chosen)
            changed = True

    if changed:
        enrollment.save(ignore_permissions=True)


@frappe.whitelist()
def enroll_student(
    student_id: str,
    program: str,
    student_group: Optional[str] = None,
    academic_year: Optional[str] = None,
    electives: Optional[Dict[str, str]] = None,
) -> Dict:
    """
    Enroll a student in a program.

    Args:
        student_id: Student name (from Student DocType)
        program: Program name (e.g., 'IGCSE Science')
        student_group: Class name (e.g., 'Form 1A', optional)
        academic_year: Academic year (optional, defaults to the year
            whose date range contains today)
        electives: {elective_group: chosen_course}, one entry per
            elective group the Program defines (e.g. {"Practical":
            "Computer Science"}). Required if the Program has any
            elective groups and the student doesn't already have a
            choice recorded for them.

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

    # Elective groups are mandatory at enrollment time -- the system has
    # no way to guess which practical subject a student wants, and a
    # Report Card can't generate correctly without a full course list.
    elective_groups = _elective_groups_for(program)
    if elective_groups:
        missing = [g for g in elective_groups if not (electives or {}).get(g)]
        if missing:
            frappe.throw(_("Please choose a subject for: {0}").format(", ".join(missing)))

        # Programs like A-Level's Lower/Upper 6 model "pick 3 from one
        # pool" as 3 identical elective groups (Subject Choice 1/2/3) --
        # nothing else stops the same course being picked for two slots.
        chosen = [electives[g] for g in elective_groups if g in electives]
        if len(chosen) != len(set(chosen)):
            frappe.throw(_("Each subject choice must be different -- you picked the same subject twice."))

    try:
        existing = frappe.db.get_value(
            'Program Enrollment',
            filters={'student': student_id, 'program': program},
            pluck='name'
        )

        enrollment_name = existing
        skipped = bool(existing)

        if not existing:
            enrollment = frappe.get_doc({
                'doctype': 'Program Enrollment',
                'student': student_id,
                'program': program,
                'academic_year': academic_year,
            })
            enrollment.insert(ignore_permissions=True)
            enrollment_name = enrollment.name

        _sync_program_enrollment_courses(enrollment_name, program, electives)

        # Program Enrollment has no student_group field -- passing it in
        # the dict above is a silent no-op (Frappe ignores unknown keys).
        # Class roster membership is a separate child table on Student
        # Group itself; add it here explicitly, and do it even when the
        # Program Enrollment already existed, so re-running enroll_student
        # can still fix up a student who's missing from their class.
        if student_group:
            already_member = frappe.db.exists(
                'Student Group Student',
                {'parent': student_group, 'student': student_id, 'active': 1}
            )
            if not already_member:
                student_name = frappe.db.get_value('Student', student_id, 'student_name')
                frappe.get_doc({
                    'doctype': 'Student Group Student',
                    'parenttype': 'Student Group',
                    'parent': student_group,
                    'parentfield': 'students',
                    'student': student_id,
                    'student_name': student_name,
                    'active': 1,
                }).insert(ignore_permissions=True)

        frappe.db.commit()

        log_audit('ENROLL', 'Student', student_id, {
            'program': program,
            'student_group': student_group,
            'enrollment_id': enrollment_name,
            'electives': electives,
        })

        return {
            'success': True,
            'message': f"Student enrolled in '{program}'" + (f" / '{student_group}'" if student_group else "") + f" for {academic_year}",
            'enrollment_id': enrollment_name,
            'program': program,
            'student_group': student_group,
            'academic_year': academic_year,
            'skipped': skipped
        }

    except Exception as e:
        frappe.logger().error(f"Enrollment failed: {traceback.format_exc()}")
        frappe.throw(f"Failed to enroll student: {str(e)}")


@frappe.whitelist()
def update_student_elective(student_id: str, elective_group: str, new_course: str) -> Dict:
    """
    Change a student's elective choice (e.g. switching Computer Science ->
    Textile Technology mid-year). Only swaps the Program Enrollment
    course row -- any Assessment Result already recorded under the
    dropped subject is left untouched as historical data; report card
    completeness only checks the student's *current* enrollment, so a
    switch never blocks their report.

    Args:
        student_id: Student name
        elective_group: Which elective group to change (e.g. "Practical")
        new_course: The course to switch to -- must be a valid option in
            that elective group for the student's Program

    Returns:
        Dict with success flag and the old/new course
    """

    if not has_bursar_permission():
        frappe.throw(_("You do not have permission to manage student subjects"))

    enrollment_name = frappe.db.get_value('Program Enrollment', {'student': student_id}, 'name')
    if not enrollment_name:
        frappe.throw(_("This student has no Program Enrollment to update."))

    enrollment = frappe.get_doc('Program Enrollment', enrollment_name)
    elective_groups = _elective_groups_for(enrollment.program)

    if elective_group not in elective_groups:
        frappe.throw(_("'{0}' is not an elective group on this student's Program.").format(elective_group))

    options = elective_groups[elective_group]
    if new_course not in options:
        frappe.throw(_("'{0}' is not a valid choice for the '{1}' elective.").format(new_course, elective_group))

    # Programs with multiple identical elective slots (e.g. A-Level's
    # "pick 3 from one pool") could otherwise end up with the same
    # course chosen for two different slots.
    other_slot_courses = {
        row.course for row in enrollment.courses
        if row.course in {c for g, opts in elective_groups.items() if g != elective_group for c in opts}
    }
    if new_course in other_slot_courses:
        frappe.throw(_("'{0}' is already chosen for another subject slot.").format(new_course))

    old_course = None
    for row in list(enrollment.courses):
        if row.course in options and row.course != new_course:
            old_course = row.course
            enrollment.remove(row)

    if new_course not in {row.course for row in enrollment.courses}:
        enrollment.append('courses', {'course': new_course})

    enrollment.save(ignore_permissions=True)
    frappe.db.commit()

    log_audit('UPDATE_ELECTIVE', 'Student', student_id, {
        'elective_group': elective_group,
        'old_course': old_course,
        'new_course': new_course,
    })

    return {
        'success': True,
        'message': f"Elective changed from '{old_course}' to '{new_course}'" if old_course else f"Elective set to '{new_course}'",
        'old_course': old_course,
        'new_course': new_course,
    }


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
            # Guardian, unlike Student, has no on_insert hook that creates
            # a linked portal login -- without this the guardian has no
            # way to ever log in and see their child's reports/fees.
            email_clean = guardian_email.strip()
            if not frappe.db.exists('User', email_clean):
                user = frappe.get_doc({
                    'doctype': 'User',
                    'email': email_clean,
                    'first_name': guardian_name.strip().split(' ')[0],
                    'send_welcome_email': 0,
                    'user_type': 'Website User',
                    'roles': [{'role': 'Guardian'}],
                })
                user.insert(ignore_permissions=True)

            guardian = frappe.get_doc({
                'doctype': 'Guardian',
                'guardian_name': guardian_name.strip(),
                'email_address': guardian_email.strip(),
                'user': email_clean,
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
