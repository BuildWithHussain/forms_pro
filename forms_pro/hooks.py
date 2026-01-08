app_name = "forms_pro"
app_title = "Forms Pro"
app_publisher = "harsh@buildwithhussain.com"
app_description = "Web Forms on steroids!"
app_email = "developers@buildwithhussain.com"
app_license = "agpl-3.0"


fixtures = [
    {"dt": "Role", "filters": {"role_name": "Forms Pro User"}},
]
# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
    {
        "name": "forms_pro",
        "logo": "/assets/forms_pro/images/logo_300.png",
        "title": "Forms Pro",
        "route": "/forms_pro",
        "has_permission": "forms_pro.overrides.roles.has_forms_pro_permission",
    }
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/forms_pro/css/forms_pro.css"
# app_include_js = "/assets/forms_pro/js/forms_pro.js"

# include js, css files in header of web template
# web_include_css = "/assets/forms_pro/css/forms_pro.css"
# web_include_js = "/assets/forms_pro/js/forms_pro.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "forms_pro/public/scss/website"

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
# app_include_icons = "forms_pro/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "forms_pro.utils.jinja_methods",
# 	"filters": "forms_pro.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "forms_pro.install.before_install"
after_install = "forms_pro.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "forms_pro.uninstall.before_uninstall"
# after_uninstall = "forms_pro.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "forms_pro.utils.before_app_install"
# after_app_install = "forms_pro.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "forms_pro.utils.before_app_uninstall"
# after_app_uninstall = "forms_pro.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "forms_pro.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User": {
        "on_update": "forms_pro.overrides.roles.handle_forms_pro_role_change",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"forms_pro.tasks.all"
# 	],
# 	"daily": [
# 		"forms_pro.tasks.daily"
# 	],
# 	"hourly": [
# 		"forms_pro.tasks.hourly"
# 	],
# 	"weekly": [
# 		"forms_pro.tasks.weekly"
# 	],
# 	"monthly": [
# 		"forms_pro.tasks.monthly"
# 	],
# }

# Testing
# -------

before_tests = "forms_pro.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "forms_pro.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "forms_pro.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["forms_pro.utils.before_request"]
# after_request = ["forms_pro.utils.after_request"]

# Job Events
# ----------
# before_job = ["forms_pro.utils.before_job"]
# after_job = ["forms_pro.utils.after_job"]

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
# 	"forms_pro.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


website_route_rules = [
    {"from_route": "/forms/<path:app_path>", "to_route": "forms"},
]
