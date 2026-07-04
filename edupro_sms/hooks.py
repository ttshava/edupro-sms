app_name = "edupro_sms"
app_title = "Edupro SMS"
app_publisher = "Edupro"
app_description = "IGCSE academic reporting and school management platform"
app_email = "ttshava@gmail.com"
app_license = "mit"

# Boot session
# ------------------
# Force "setup complete" on every session -- see edupro_sms/boot.py and
# .claude/DECISIONS.md 0011 for why.
boot_session = "edupro_sms.edupro_sms.boot.boot_session"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "edupro_sms",
		"title": "Edupro SMS",
		"route": "/dashboard",
		"has_permission": "edupro_sms.edupro_sms.dashboard.has_dashboard_access",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/edupro_sms/css/edupro_sms.css"
# app_include_js = "/assets/edupro_sms/js/edupro_sms.js"

# include js, css files in header of web template
# web_include_css = "/assets/edupro_sms/css/edupro_sms.css"
# web_include_js = "/assets/edupro_sms/js/edupro_sms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "edupro_sms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "edupro_sms/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# Education's own hooks set Student/Guardian -> edu-portal (its own
# built-in, compiled-JS portal we can't safely customize). role_home_page
# hooks merge into a list across apps and frappe/website/utils.py takes
# the LAST entry (role_home_page[role][-1]) -- edupro_sms loads after
# education in apps.txt, so this override wins. See
# .claude/DECISIONS.md for why we're not customizing edu-portal itself.
role_home_page = {
	"Student": "my-reports",
	"Guardian": "my-reports",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
	"methods": [
		"edupro_sms.edupro_sms.qr.report_card_verification_qr_data_uri",
	],
}

# Installation
# ------------

# before_install = "edupro_sms.install.before_install"
# after_install = "edupro_sms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "edupro_sms.uninstall.before_uninstall"
# after_uninstall = "edupro_sms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "edupro_sms.utils.before_app_install"
# after_app_install = "edupro_sms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "edupro_sms.utils.before_app_uninstall"
# after_app_uninstall = "edupro_sms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "edupro_sms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Report Card": "edupro_sms.edupro_sms.doctype.report_card.report_card.get_permission_query_conditions",
	"Assessment Plan": "edupro_sms.edupro_sms.teacher_permissions.assessment_plan_query_conditions",
	"Assessment Result": "edupro_sms.edupro_sms.teacher_permissions.assessment_result_query_conditions",
}

has_permission = {
	"Report Card": "edupro_sms.edupro_sms.doctype.report_card.report_card.has_permission",
	"Assessment Plan": "edupro_sms.edupro_sms.teacher_permissions.assessment_plan_has_permission",
	"Assessment Result": "edupro_sms.edupro_sms.teacher_permissions.assessment_result_has_permission",
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	"School Settings": {
		"on_update": "edupro_sms.edupro_sms.branding.sync_website_branding",
	},
	"User": {
		"validate": "edupro_sms.edupro_sms.dashboard.sync_dashboard_default_app",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"edupro_sms.tasks.all"
# 	],
# 	"daily": [
# 		"edupro_sms.tasks.daily"
# 	],
# 	"hourly": [
# 		"edupro_sms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"edupro_sms.tasks.weekly"
# 	],
# 	"monthly": [
# 		"edupro_sms.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "edupro_sms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "edupro_sms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "edupro_sms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Fixtures
# --------
# Version-controlled, reproducible across sites — see CODING_STANDARDS.md

fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Headmaster", "Class Teacher", "Student", "Guardian", "Instructor"]]],
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
				],
			],
			["role", "in", ["Headmaster", "Instructor"]],
		],
	},
]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["edupro_sms.utils.before_request"]
# after_request = ["edupro_sms.utils.after_request"]

# Job Events
# ----------
# before_job = ["edupro_sms.utils.before_job"]
# after_job = ["edupro_sms.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"edupro_sms.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

