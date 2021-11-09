# Copyright (c) 2013-2021, libracore and contributors
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
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data",  "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group",  "width": 120},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link",  "options": "Warehouse", "width": 150},
        {"label": _("Regal"), "fieldname": "regal", "fieldtype": "Data", "width": 120},
        {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "width": 100, "options": "UOM"},
        {"label": _("Quantity"), "fieldname": "qty", "fieldtype": "Float", "width": 100},       
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Currency", "width": 100},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]

def get_data(filters):
    # prepare filters
    if not 'item_group' in filters:
        filters['item_group'] = "%"
    if not 'warehouse' in filters:
        filters['warehouse'] = "%"
        
    # fetch data
    sql_query = """SELECT
            `tabItem`.`item_code` AS `item_code`,
            `tabItem`.`item_name` AS `item_name`,
            `tabItem`.`item_group` As `item_group`,
            `tabBin`.`warehouse` AS `warehouse`,
            `tabItem`.`regal` AS `regal`,
            `tabItem`.`stock_uom` AS `stock_uom`,
            `tabBin`.`actual_qty` AS `qty`,
            `tabBin`.`stock_value` AS `value`
        FROM `tabBin`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabBin`.`item_code`
        WHERE 
            `tabItem`.`item_group` LIKE "{item_group}"
            AND `tabBin`.`warehouse` LIKE "{warehouse}"
        ORDER BY `tabItem`.`regal` ASC, `tabItem`.`item_code` ASC;""".format(item_group=filters['item_group'], warehouse=filters['warehouse'])
    data = frappe.db.sql(sql_query, as_dict=True)
    return data