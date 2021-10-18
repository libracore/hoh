# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "hoh"
app_title = "hoh"
app_publisher = "libracore"
app_description = "ERPNext applications for Hoferhecht"
app_icon = "octicon octicon-bookmark"
app_color = "#a21f15"
app_email = "info@libracore.com"
app_license = "AGPL"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/hoh/css/hoh.css"
# app_include_js = "/assets/hoh/js/hoh.js"

# include js, css files in header of web template
# web_include_css = "/assets/hoh/css/hoh.css"
# web_include_js = "/assets/hoh/js/hoh.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Work Order" : "public/js/work_order.js",
    "Sales Order" : "public/js/sales_order.js"
}
doctype_list_js = {
    "Item" : "public/js/item_list.js",
    "Work Order" : "public/js/work_order_list.js",
    "Delivery Note" : "public/js/delivery_note_list.js"
}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "hoh.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Angebot"]

# Installation
# ------------

# before_install = "hoh.install.before_install"
# after_install = "hoh.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hoh.notifications.get_notification_config"

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hoh.tasks.all"
# 	],
# 	"daily": [
# 		"hoh.tasks.daily"
# 	],
# 	"hourly": [
# 		"hoh.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hoh.tasks.weekly"
# 	]
# 	"monthly": [
# 		"hoh.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "hoh.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hoh.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hoh.task.get_dashboard_data"
# }

# hook for migrate cleanup tasks
after_migrate = [
    'hoh.hoh.updater.cleanup_languages'
]
