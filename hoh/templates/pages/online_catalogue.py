# Copyright (c) 2020, libracore and Contributors
# License: AGPL. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hoh.hoh.doctype.angebot.angebot import get_care_symbol_html, get_composition_string, get_category_string

no_cache = 1
# check login
if frappe.session.user=='Guest':
    frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)
        
def get_context(context):
    items = frappe.get_all("Bemusterung", 
        filters=[['image', 'LIKE', '%']], 
        fields=['name', 'image', 'stoffbreite_von', 'stoffbreite_bis', 'fertigbreite_von',
                'fertigbreite_bis', 'gewicht', 'rate',
                'country_of_origin'],
        order_by='name')
    
    context.no_cache = 1
    context.show_sidebar = False
    
    for item in items:
        item['zusammensetzung'] = get_composition_string(item.name)
        item['pflegesymbole'] = get_care_symbol_html(item.name)
        item['rate'] = 1.2 * float(item['rate'])
        item['categories'] = get_category_string(item.name)

    context.items = items

    raw_filters = frappe.get_all("Produktkategorie", fields=['name'], order_by='sort_index')
    filters = []
    for f in raw_filters:
        filters.append(f['name'])
    context.filters = filters
    
