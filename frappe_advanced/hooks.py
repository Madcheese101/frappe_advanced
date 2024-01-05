from . import __version__ as app_version

app_name = "frappe_advanced"
app_title = "Frappe Advanced"
app_publisher = "MadCheese"
app_description = "New ideas and fucntions"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "leg.ly@hotmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/frappe_advanced/css/frappe_advanced.css"
# app_include_js = "/assets/frappe_advanced/js/frappe_advanced.js"
app_include_js = ["frappe_advanced.bundle.js"]

# include js, css files in header of web template
# web_include_css = "/assets/frappe_advanced/css/frappe_advanced.css"
# web_include_js = "/assets/frappe_advanced/js/frappe_advanced.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_advanced/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}
# page_js = {"print" : "printing/page/print/custom_print.js"}
# page_js = {"print" : "page.bundle.js"}


# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {"Stock Entry" : "public/js/stock_entry.js",
              "Quotation" : "public/js/quotation.js",
              "Item" : "public/js/item.js",
              "Payment Entry" : "public/js/payment_entry.js"}
doctype_list_js = {"Payment Entry" : "public/js/payment_entry_list.js"}
# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "frappe_advanced.install.before_install"
# after_install = "frappe_advanced.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "frappe_advanced.uninstall.before_uninstall"
# after_uninstall = "frappe_advanced.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_advanced.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }
override_doctype_class = {
    # "Quotation": "frappe_advanced.frappe_advanced.overrides.quotation.CustomQuotation",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }
doc_events = {
	"Sales Invoice": {
		"on_cancel": "frappe_advanced.crud_events.warning_events.cancel_invoice_warning",
		"on_submit": "frappe_advanced.crud_events.warning_events.exceeded_discount_percentage"
	},
    "Payment Entry": {
		"on_submit": "frappe_advanced.crud_events.warning_events.partial_balance_transfer",
        "before_submit": "frappe_advanced.crud_events.warning_events.validate_write_off_limit",
        "validate": "frappe_advanced.crud_events.events.check_open_posa_shifts"
	},
    "Stock Entry": {
        "on_submit": "frappe_advanced.crud_events.events.split_batch_on_recieve",
        "before_save": "frappe_advanced.crud_events.events.stock_entry_set_default_from_target"
	},
    "POS Profile": {
		"after_insert": "frappe_advanced.crud_events.events.update_user_permissions_event",
        "on_update": "frappe_advanced.crud_events.events.update_user_permissions_event"
	},
    "Item": {
        "after_insert": "frappe_advanced.crud_events.events.generate_item_barcode"
    }
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"frappe_advanced.tasks.all"
#	],
#	"daily": [
#		"frappe_advanced.tasks.daily"
#	],
#	"hourly": [
#		"frappe_advanced.tasks.hourly"
#	],
#	"weekly": [
#		"frappe_advanced.tasks.weekly"
#	]
#	"monthly": [
#		"frappe_advanced.tasks.monthly"
#	]
# }
scheduler_events = {
	"cron": {
        # run at 12PM
		"0 12 * * *": [
            "frappe_advanced.frappe_advanced.tasks.tasks.account_closed_check",
            "frappe_advanced.frappe_advanced.tasks.tasks.stock_entry_check",
		],
        # run at 12AM
        "0 0 * * *":[
            "frappe_advanced.frappe_advanced.tasks.tasks.auto_close_shift",
        ]
	}
}

# Testing
# -------

# before_tests = "frappe_advanced.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "frappe_advanced.event.get_events"
# }
override_whitelisted_methods = {
    "erpnext.controllers.item_variant.create_variant": "frappe_advanced.frappe_advanced.api.api.create_variant",
    "erpnext.controllers.item_variant.enqueue_multiple_variant_creation": "frappe_advanced.frappe_advanced.api.api.enqueue_multiple_variant_creation"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "frappe_advanced.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Request Events
# ----------------
# before_request = ["frappe_advanced.utils.before_request"]
# after_request = ["frappe_advanced.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_advanced.utils.before_job"]
# after_job = ["frappe_advanced.utils.after_job"]

# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"frappe_advanced.auth.validate"
# ]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            
            [
                "name",
                "in",
                (
                    "Account-branch",
                    "Employee-default_in_transit_warehouse",
                    "Employee-default_warehouse",
                    "Property Setter-dont_replace",
                    "Payment Entry-note_count",
                    "Payment Entry-count_total",
                    "Branch-warehouse",
                    "Branch-parent_account",
                    "Branch-letter_head",
                    "Branch-mode_of_payment",
                    "Stock Entry-title",
                    "auto_items_barcode"
                ),
            ]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            
            [
                "name",
                "in",
                (
                    "Payment Entry-payment_type-default",
                    "Payment Entry-naming_series-default",
                    "Payment Entry-naming_series-options",
                    "Stock Entry-stock_entry_type-default",
                    "Stock Entry-main-title_field",
                    "Note Count-main-default_print_format"
                ),
            ]
        ]
    }
]

import frappe_advanced.frappe_advanced.overrides.meta as meta
meta.load_batches()