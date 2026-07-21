app_name = "edupro_sms"
app_title = "Edupro SMS"
app_publisher = "Edupro"
app_description = "IGCSE Academic Reporting Platform"
app_email = "ttshava@gmail.com"
app_license = "mit"

# Boot session
# ------------------
# Force "setup complete" on every session -- see edupro_sms/boot.py.
boot_session = "edupro_sms.boot.boot_session"

# Apps screen
# ------------------
add_to_apps_screen = [
	{
		"name": "edupro_sms",
		"title": "Edupro SMS",
		"route": "/dashboard",
		"has_permission": "edupro_sms.dashboard.has_dashboard_access",
	}
]

# Website user home page (by role)
# ------------------
# edupro_sms loads after education in apps.txt, so this override wins.
role_home_page = {
	"Student": "my-reports",
	"Guardian": "my-reports",
	"Bursar": "bursar",
}

# Jinja
# ------------------
jinja = {
	"methods": [
		"edupro_sms.qr.report_card_verification_qr_data_uri",
		"edupro_sms.watermark.report_card_watermark_data_uri",
		"edupro_sms.watermark.school_logo_data_uri",
		"edupro_sms.fees.get_student_fee_statement",
		"edupro_sms.fees.get_student_ledger",
		"edupro_sms.fees.get_receipt_context",
		"edupro_sms.academic_calendar.get_next_term_start",
	],
}

# Permissions
# ------------------
permission_query_conditions = {
	"Report Card": "edupro_sms.edupro_sms.doctype.report_card.report_card.get_permission_query_conditions",
	"Assessment Plan": "edupro_sms.teacher_permissions.assessment_plan_query_conditions",
	"Assessment Result": "edupro_sms.teacher_permissions.assessment_result_query_conditions",
	"Student Fee": "edupro_sms.fee_permissions.get_permission_query_conditions",
	"Student Ledger Entry": "edupro_sms.fee_permissions.get_ledger_permission_query_conditions",
	"Student": "edupro_sms.student_permissions.get_permission_query_conditions",
}

has_permission = {
	"Report Card": "edupro_sms.edupro_sms.doctype.report_card.report_card.has_permission",
	"Assessment Plan": "edupro_sms.teacher_permissions.assessment_plan_has_permission",
	"Assessment Result": "edupro_sms.teacher_permissions.assessment_result_has_permission",
	"Student Fee": "edupro_sms.fee_permissions.has_permission",
	"Student Ledger Entry": "edupro_sms.fee_permissions.has_ledger_permission",
	"Student": "edupro_sms.student_permissions.has_permission",
}

# Document Events
# ------------------
doc_events = {
	"School Settings": {
		"on_update": "edupro_sms.branding.sync_website_branding",
	},
	"User": {
		"validate": "edupro_sms.dashboard.sync_dashboard_default_app",
	},
	"Assessment Plan": {
		"before_insert": "edupro_sms.teacher_assignment.default_examiner_from_assignment",
	},
	"Student": {
		"after_insert": "edupro_sms.student_hooks.ensure_student_role",
	},
}

# Fixtures
# ------------------
# Version-controlled, reproducible across sites.
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Headmaster", "Class Teacher", "Student", "Guardian", "Instructor", "Bursar"]]],
	},
	{"dt": "Grading Scale", "filters": [["name", "in", ["IGCSE Standard"]]]},
	{
		"dt": "Custom Field",
		"filters": [
			[
				"name",
				"in",
				[
					"Student Group-class_teacher",
					"Assessment Result-special_case",
					"Instructor-user",
					"Program-curriculum",
					"Student-boarding_type",
					"Program Course-elective_group",
				],
			]
		],
	},
	{"dt": "Workflow", "filters": [["name", "in", ["Report Card Approval"]]]},
	{"dt": "Workflow State", "filters": [["name", "in", ["Pending Approval", "Reviewed", "Published"]]]},
	{"dt": "Workflow Action Master", "filters": [["name", "in", ["Resubmit", "Publish"]]]},
	{
		"dt": "Custom DocPerm",
		"filters": [
			[
				"parent",
				"in",
				[
					"Student",
					"Instructor",
					"Student Group",
					"Student Group Student",
					"Guardian",
					"Course",
					"Program",
					"Assessment Plan",
					"Assessment Result",
					"Academic Term",
					"Academic Year",
					"Customer",
					"User",
				],
			],
			["role", "in", ["Headmaster", "Instructor", "Bursar"]],
		],
	},
]
