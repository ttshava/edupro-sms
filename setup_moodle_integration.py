#!/usr/bin/env python3
"""Setup Edupro Primary Moodle Integration"""
import sys
import os

sys.path.insert(0, '/home/frappe/frappe-bench/apps/frappe')
sys.path.insert(0, '/home/frappe/frappe-bench/apps/education')
sys.path.insert(0, '/home/frappe/frappe-bench/apps/edupro_sms')
sys.path.insert(0, '/home/frappe/frappe-bench/apps/edupro_primary')
os.chdir('/home/frappe/frappe-bench')

import frappe
frappe.init('edupro.localhost', sites_path='/home/frappe/frappe-bench/sites')
frappe.connect()
frappe.set_user('Administrator')

print('\n=== Edupro Primary + Moodle 5.0.1 Integration ===\n')

# Step 1: Configure Moodle Settings
print('Step 1: Configuring Moodle Settings...')
try:
    if frappe.db.exists('Moodle Settings'):
        doc = frappe.get_doc('Moodle Settings')
        action = 'Updated'
    else:
        doc = frappe.get_doc({'doctype': 'Moodle Settings'})
        action = 'Created'

    doc.moodle_url = 'http://moodle_app:80'
    doc.moodle_token = 'edupro_moodle_6c9e8d7f2a4b5c3e1f9g2h4j5k7m8n0p'
    doc.sync_enabled = 1
    doc.sync_direction = 'frappe_to_moodle'
    doc.save()
    frappe.db.commit()
    print(f'✅ Moodle Settings {action}\n')
except Exception as e:
    print(f'❌ Error: {str(e)}\n')
    sys.exit(1)

# Step 2: Test Moodle Connection
print('Step 2: Testing Moodle Connection...')
try:
    from edupro_primary.moodle.client import MoodleClient
    client = MoodleClient()
    if client.test_connection():
        print('✅ Connected to Moodle successfully\n')
    else:
        print('⚠️  Connection test returned False\n')
except Exception as e:
    print(f'❌ Error: {str(e)}\n')

# Step 3: Create Test Student (triggers sync)
print('Step 3: Creating Test Student to trigger sync...')
try:
    student_id = 'TEST_MOODLE_SYNC_001'

    # Delete if exists
    if frappe.db.exists('Student', student_id):
        frappe.delete_doc('Student', student_id, force=True)
        frappe.db.commit()

    # Create student
    student = frappe.get_doc({
        'doctype': 'Student',
        'name': student_id,
        'first_name': 'Test',
        'last_name': 'Sync',
        'email': 'testsync@edupro.local',
        'date_of_birth': '2010-05-15',
        'gender': 'Male'
    })
    student.insert()
    frappe.db.commit()
    print(f'✅ Student created: {student_id}')

    # Check for Moodle sync
    import time
    time.sleep(3)

    student.reload()
    moodle_id = student.get('moodle_user_id')

    if moodle_id:
        print(f'✅ SYNC SUCCESSFUL! Moodle User ID: {moodle_id}')

        # Verify in Moodle database
        try:
            moodle_user = frappe.db.sql(
                'SELECT username FROM `moodle`.mdl_user WHERE id = %s',
                (moodle_id,)
            )
            if moodle_user:
                print(f'✅ Verified in Moodle: User "{moodle_user[0][0]}" (ID: {moodle_id})')
        except Exception as db_err:
            print(f'⚠️  Could not verify in Moodle DB: {str(db_err)}')
    else:
        print('⚠️  Moodle ID not set (sync may have failed)')
        print('   Check Frappe logs for errors')

except Exception as e:
    print(f'❌ Error: {str(e)}')
    import traceback
    traceback.print_exc()

print('\n=== Integration Setup Complete ===\n')
