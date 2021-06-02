# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StockControl(Document):
    def get_stock(self, item):
        stock = frappe.get_all("Bin", filters={'item_code': item, 'warehouse': self.warehouse}, fields=['name', 'actual_qty'])
        if stock and len(stock) > 0:
            return stock[0]['actual_qty']
        else:
            return None
    
    def on_submit(self):
        # collect item differences
        receipts = []
        issues = []
        for i in self.items:
            if i.difference_qty > 0:
                receipts.append({
                    'item_code': i.item,
                    'qty': i.difference_qty
                })
            elif i.difference_qty < 0:
                issues.append({
                    'item_code': i.item,
                    'qty': (-1) * i.difference_qty              # note: invert qty here, as this is coverd by the material issue
                })
        # create stock entries
        if len(receipts) > 0:
            self.material_receipt = self.create_stock_entry("Material Receipt", receipts)
        if len(issues) > 0:
            self.material_issue = self.create_stock_entry("Material Issue", issues)
        return
    
    def create_stock_entry(self, stock_entry_type, items):
        doc = frappe.get_doc({
            'doctype': "Stock Entry",
            'stock_entry_type': stock_entry_type,
            'to_warehouse': self.warehouse,
            'from_warehouse': self.warehouse,
            'set_posting_time': 1,
            'posting_date': self.date
        })
        for i in items:
            doc.append('items', {
                'item_code': i['item_code'],
                'qty': i['qty']
            })
        doc = doc.insert()
        doc.submit()
        return doc.name
