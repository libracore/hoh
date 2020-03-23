# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Bemusterung(Document):
    def validate(self):
        # make sure only one sample with this colour is used
        same_color_dessins = frappe.get_all("Bemusterung", 
            filters={'dessinnummer': self.dessinnummer, 'farbe': self.farbe},
            fields=['name'])
        if len(same_color_dessins) > 1 or \
           (len(same_color_dessins) == 1 and same_color_dessins[0]['name'] != self.name):
            frappe.throw( _("Diese Dessin/Farb-Kombination existiert bereits in {0}.".format(
                same_color_dessins[0]['name'])) )
        return
        
    def create_item(self):
        # create new item
        new_item = frappe.get_doc({
            'doctype': 'Item',
            'item_name': self.bezeichnung,
            'item_code': self.name,
            'item_group': 'Stickereien',
            'is_stock_item': 1,
            'dessin': self.dessin,
            'komposition': self.komposition,
            'pflegesymbole': self.pflegesymbole
        })
        item = new_item.insert()
        # create new BOM
        new_bom = frappe.get_doc({
            'doctype': 'BOM',
            'item': item.item_code,
            'quantity': 1,
            'is_active': 1,
            'is_default': 1
        })
        for i in self.items:
            row = new_bom.append('items', {
                'item_code': i.item_code,
                'qty': i.qty,
                'rate': i.valuation_rate
            })
        bom = new_bom.insert()
        # create reference
        self.item = item.name
        self.save()
        # write changes
        frappe.db.commit()
        # return item code
        return item.name
