# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Dessinnummer(Document):
    def find_next_number(self):
        sql_query = """SELECT MAX(`name`) AS `max`
                       FROM `tabDessinnummer`;"""
        last_number = frappe.db.sql(sql_query, as_dict=True)[0]['max']
        try:
            next_number = int(last_number) + 1
        except:
            next_number = 1
        return "{0}".format(next_number)
        
