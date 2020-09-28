# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OnlineCatalogueLikeTrace(Document):
    pass

@frappe.whitelist()
def add_like(user, bemusterung, like=1):
    new_comment = frappe.get_doc({
        'doctype': "Online Catalogue Like Trace",
        'user': user,
        'bemusterung': bemusterung,
        'like': like
    })
    new_comment.insert()
    return
