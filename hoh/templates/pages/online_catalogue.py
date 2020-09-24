# Copyright (c) 2020, libracore and Contributors
# License: AGPL. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

no_cache = 1
# check login
if frappe.session.user=='Guest':
    frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)
        
def get_context(context):
    sidebar_title = "Sidebar"
    items = frappe.get_all("Bemusterung", filters=[['image', 'LIKE', '%']], fields=['name'])
    
    context.no_cache = 1
    context.show_sidebar = False
    context.sidebar_title = sidebar_title
    context.intro = "Intro"
    context.items = items

