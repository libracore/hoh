# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json

class OnlineCatalogueRequest(Document):
    pass

@frappe.whitelist()
def place_request(user, items):
    if isinstance(items, str):
        items = json.loads(items)
    new_request = frappe.get_doc({
        'doctype': "Online Catalogue Request",
        'user': user,
        'items': items
    })
    new_request.insert()
    return
