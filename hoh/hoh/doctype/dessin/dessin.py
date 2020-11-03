# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Dessin(Document):
    def before_save(self):
        # update all related bemusterung & items
        update_related_doctypes(self, "Bemusterung")
        update_related_doctypes(self, "Item")
        return

def update_related_doctypes(dessin, target_type):
    child_bems = frappe.get_all(target_type, filters={'dessin': dessin.name}, fields=['name'])
    for bem in child_bems:
        b = frappe.get_doc(target_type, bem['name'])
        b.stickmaschine = []    # clear previous machines
        b.save()
        for s in dessin.stickmaschine:    # add current machines
            b.append('stickmaschine', {'stickmaschine': s.stickmaschine})
        b.save()
    return
