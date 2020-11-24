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
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Qty sold [m]"), "fieldname": "qty_sold", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _("Qty purchased [m]"), "fieldname": "qty_purchased", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _("Number of sales orders"), "fieldname": "number_of_sales_orders", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _(" "), "fieldname": "blank", "width": 20}
    ]

def get_data(filters):
    sql_query = """SELECT
         `item_code`,
         `item_name`,
         `qty_sold`,
         `number_of_sales_orders`,
         `qty_purchased`
        FROM
        (SELECT 
         `item_code`,
         `item_name`,
         SUM(`qty_sold`) AS `qty_sold`,
         SUM(`number_of_sales_orders`) AS `number_of_sales_orders`,
         (SELECT SUM(`stock_qty`)
           FROM `tabPurchase Receipt Item`
           LEFT JOIN `tabPurchase Receipt` ON `tabPurchase Receipt`.`name` = `tabPurchase Receipt Item`.`parent`
           WHERE `tabPurchase Receipt Item`.`item_code` = `products`.`item_code`
             AND `tabPurchase Receipt`.`docstatus` = 1
             AND `tabPurchase Receipt`.`posting_date` >= "{from_date}"
             AND `tabPurchase Receipt`.`posting_date` <= "{to_date}") AS `qty_purchased`
        FROM
        (SELECT `tabItem`.`item_code`, 
          `tabItem`.`item_name`,
          `tabBOM`.`item`,
          (SELECT SUM(`stock_qty`)
           FROM `tabDelivery Note Item`
           LEFT JOIN `tabDelivery Note` ON `tabDelivery Note`.`name` = `tabDelivery Note Item`.`parent`
           WHERE `tabDelivery Note Item`.`item_code` = `tabBOM`.`item`
             AND `tabDelivery Note`.`docstatus` = 1 
             AND `tabDelivery Note`.`posting_date` >= "{from_date}"
             AND `tabDelivery Note`.`posting_date` <= "{to_date}") AS `qty_sold`,
          (SELECT COUNT(DISTINCT(`tabSales Order`.`name`))
           FROM `tabSales Order Item`
           LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabSales Order Item`.`parent`
           WHERE `tabSales Order Item`.`item_code` = `tabBOM`.`item`
             AND `tabSales Order`.`docstatus` = 1
             AND `tabSales Order`.`transaction_date` >= "{from_date}"
             AND `tabSales Order`.`transaction_date` <= "{to_date}") AS `number_of_sales_orders`
        FROM `tabItem`
        JOIN `tabBOM Item` ON `tabBOM Item`.`item_code` = `tabItem`.`item_code`
        LEFT JOIN `tabBOM` ON `tabBOM`.`name` = `tabBOM Item`.`parent`
        WHERE `tabItem`.`item_group` = "{item_group}") AS `products`
        GROUP BY `products`.`item_code`) AS `data`
        WHERE `data`.`qty_sold` > 0 OR `data`.`qty_purchased` > 0;""".format(
                from_date=filters.from_date, to_date=filters.to_date, item_group=filters.item_group)
    
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
