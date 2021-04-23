# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item","width": 110},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 130},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 50},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 50},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Data", "width": 70},
        {"label": _("Currency"), "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 50},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150, 'precision': '2'},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 80},
        {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 90},        
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date",  "width": 90},
    ]

def get_data(filters):
    if not filters.item_code:
        filters.item_code = "%"
    if not filters.customer:
        filters.customer = "%"
        
    # prepare query
    sql_query = """SELECT
        `tabSales Invoice Item`.`item_name` AS `item_name`,
        `tabSales Invoice Item`.`item_code` AS `item_code`,
        `tabSales Invoice Item`.`parent` AS `sales_invoice`,
        `tabSales Invoice Item`.`qty` AS `qty`,
        `tabSales Invoice Item`.`rate` AS `rate`,
        `tabSales Invoice Item`.`uom` AS `uom`,
        `tabSales Invoice Item`.`description` AS `description`,
        `tabSales Invoice`.`posting_date`,
        `tabSales Invoice`.`customer`,
        `tabSales Invoice`.`customer_name`,
        `tabSales Invoice`.`currency`
        FROM `tabSales Invoice Item`
        LEFT JOIN `tabSales Invoice` ON `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name`
        WHERE `tabSales Invoice`.`docstatus` = 1
            AND `tabSales Invoice`.`customer` LIKE '{customer}'
            AND `tabSales Invoice Item`.`item_code` LIKE '{item_code}'
        ORDER BY `tabSales Invoice Item`.`item_code` ASC, `tabSales Invoice`.`posting_date` ASC;
      """.format(customer=filters.customer, item_code=filters.item_code)
    
    data = frappe.db.sql(sql_query, as_dict=1)
    return data
