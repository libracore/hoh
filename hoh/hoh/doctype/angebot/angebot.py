# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe import _

class Angebot(WebsiteGenerator):
    website = frappe._dict(
        condition_field = "show_in_website",
        template = "templates/generators/angebot.html",
        no_cache = 1,
        show_sidebar = 1
    )
    
    def get_context(self, context):
        context.update({
            "items": frappe.get_list("Angebot", fields=['name', 'angebotsdatum']),
            "title": _("Quotations")
        })
        
        return context
        
# enable list view sidebar
def get_list_context(context=None):
    context.update({
        'no_breadcrumbs': True,
        'show_sidebar': True
    })
    return context
