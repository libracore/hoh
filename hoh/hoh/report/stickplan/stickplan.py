# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 80},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 90},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date",  "width": 90},
        {"label": _("Stickmaschine"), "fieldname": "stickmaschine", "fieldtype": "Link", "options": "Stickmaschine",  "width": 100},
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):
    if not filters.stickmaschine:
        filters.stickmaschine = "%"
    else:
        filters.stickmaschine = "%{0}%".format(filters.stickmaschine)
        
    sql_query = """SELECT
         `tabWork Order`.`name` AS `work_order`,
         `tabWork Order`.`status` AS `status`, 
         `tabSales Order`.`customer` AS `customer`,
         `tabSales Order`.`customer_name` AS `customer_name`,
         SUBSTRING_INDEX(`tabWork Order`.`planned_start_date`, ' ', 1)  AS `start_date`,
         `tabWork Order`.`expected_delivery_date` AS `end_date`,
         `tabDessin`.`stickmaschine` AS `stickmaschine`,
         `tabWork Order`.`production_item` AS `item`,
         `tabWork Order`.`qty` AS `qty`,
         `tabWork Order`.`stock_uom` AS `uom`
        FROM `tabWork Order`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabWork Order`.`production_item`
        LEFT JOIN `tabDessin` ON `tabDessin`.`name` = `tabItem`.`dessin`
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabWork Order`.`sales_order`
        WHERE `tabDessin`.`stickmaschine` LIKE "{stickmaschine}"
        ORDER BY `tabWork Order`.`expected_delivery_date` ASC;
      """.format(stickmaschine=filters.stickmaschine)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
