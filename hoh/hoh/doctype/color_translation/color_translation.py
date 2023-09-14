# -*- coding: utf-8 -*-
# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class ColorTranslation(Document):
    def before_save(self):
        self.check_conflicts()
         
    def check_conflicts(self):
        conflicts = frappe.db.sql("""
            SELECT `original`, `translated`, `language`
            FROM `tabColor Translation`
            WHERE `language` = "{language}"
              AND `original` LIKE "%{original}%"
              AND `name` != "{name}";
            """.format(language=self.language, original=self.original, name=self.name),
            as_dict=True)
        if len(conflicts) > 0:
            frappe.msgprint( _("Es gibt möglicherweise Konflikte mit {0}").format(conflicts), _("Konflikte") )
        return
