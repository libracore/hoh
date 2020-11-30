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
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 150},
        {"label": _("Customer"), "fieldname": "customer", "options": "Customer", "width": 150},
        {"label": _("Customer name"), "fieldname": "customer_name", "width": 150},
        {"label": _("Supplier"), "fieldname": "supplier", "options": "Supplier", "width": 150},
        {"label": _("Supplier name"), "fieldname": "supplier_name", "width": 150},
        {"label": _("Qty [m]"), "fieldname": "qty", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _("Number of sales orders"), "fieldname": "number_of_sales_orders", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _(" "), "fieldname": "blank", "width": 20}
    ]

def get_data(filters):
    sql_query = """SELECT 
            `tabDelivery Note`.`posting_date` AS `date`,
            `tabDelivery Note`.`name` AS `delivery_note`,
            `tabDelivery Note`.`customer` AS `customer`,
            `tabDelivery Note`.`customer_name` AS `customer_name`,
            `tabDelivery Note Item`.`stock_qty` AS `qty`,
            null AS `purchase_receipt`,
            null AS `supplier`,
            null AS `supplier_name`
           FROM `tabDelivery Note Item`
           LEFT JOIN `tabDelivery Note` ON `tabDelivery Note`.`name` = `tabDelivery Note Item`.`parent`
           WHERE `tabDelivery Note Item`.`item_code` IN (SELECT `tabBOM`.`item` 
                                                         FROM `tabBOM Item` 
                                                         LEFT JOIN `tabBOM` ON `tabBOM`.`name` = `tabBOM Item`.`parent`
                                                         WHERE `tabBOM Item`.`item_code` = "{item_code}")
             AND `tabDelivery Note`.`docstatus` = 1
             AND `tabDelivery Note`.`posting_date` >= "{from_date}"
             AND `tabDelivery Note`.`posting_date` <= "{to_date}"
        UNION SELECT
            `tabPurchase Receipt`.`posting_date` AS `date`,
            null AS `delivery_note`,
            null AS `customer`,
            null AS `customer_name`,
            `tabPurchase Receipt Item`.`stock_qty` AS `qty`,
            `tabPurchase Receipt`.`name` AS `purchase_receipt`,
            `tabPurchase Receipt`.`supplier` AS `supplier`,
            `tabPurchase Receipt`.`supplier_name` AS `supplier_name`
            FROM `tabPurchase Receipt Item`
            LEFT JOIN `tabPurchase Receipt` ON `tabPurchase Receipt`.`name` = `tabPurchase Receipt Item`.`parent`
                   WHERE `tabPurchase Receipt Item`.`item_code` = "{item_code}"
                     AND `tabPurchase Receipt`.`docstatus` = 1
                     AND `tabPurchase Receipt`.`posting_date` >= "{from_date}"
                     AND `tabPurchase Receipt`.`posting_date` <= "{to_date}";""".format(
                from_date=filters.from_date, to_date=filters.to_date, item_code=filters.item)
    
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
