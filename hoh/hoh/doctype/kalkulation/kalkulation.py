# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Kalkulation(Document):
    def load_items(self, base_item):
        root = frappe.get_doc("Bemusterung", base_item)
        material = []
        for item in root.items:
            item_master_data = frappe.get_doc("Item", item.item_code)
            cost = item_master_data.last_purchase_rate or item.valuation_rate or item_master_data.valuation_rate
            material.append({
                'item': item.item_code,
                'qty': item.qty,
                'rate': cost
            })
        return material
