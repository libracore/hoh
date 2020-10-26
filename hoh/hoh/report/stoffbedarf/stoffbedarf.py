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
        {"label": _("Item Name"), "fieldname": "item_name", "width": 150},
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 100},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Start date"), "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": _("Required Qty"), "fieldname": "required_qty", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _("Actual Qty"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _("Planned Qty"), "fieldname": "planned_qty", "fieldtype": "Float", "width": 100, "precission": 1},
        {"label": _(" "), "fieldname": "blank", "width": 20}
    ]

def get_data(filters):
    primary_warehouse = frappe.get_value("HOH Settings", "HOH Settings", "primary_warehouse")
    sql_query = """SELECT 
                  `tabWork Order Item`.`item_code` AS `item_code`, 
                  `tabWork Order Item`.`item_name` AS `item_name`, 
                  `tabWork Order Item`.`required_qty` AS `required_qty`,
                  `tabWork Order`.`name` AS `work_order`,
                  `tabWork Order`.`sales_order` AS `sales_order`,
                  DATE(`tabWork Order`.`planned_start_date`) AS `start_date`,
                  (SELECT `actual_qty` 
                   FROM `tabBin` 
                   WHERE `tabBin`.`item_code` = `tabWork Order Item`.`item_code` 
                     AND `tabBin`.`warehouse` = "{warehouse}") AS `actual_qty`,
                  (SELECT `planned_qty` 
                   FROM `tabBin` 
                   WHERE `tabBin`.`item_code` = `tabWork Order Item`.`item_code` 
                     AND `tabBin`.`warehouse` = "{warehouse}") AS `planned_qty`
                FROM `tabWork Order Item`
                LEFT JOIN `tabWork Order` ON `tabWork Order Item`.`parent` = `tabWork Order`.`name`
                WHERE 
                  `tabWork Order`.`status` = "Not Started"
                  AND `tabWork Order`.`planned_start_date` <= "{to_date}"
                ORDER BY `tabWork Order Item`.`item_code` ASC, `tabWork Order`.`planned_start_date` ASC;;""".format(
                to_date=filters.to_date, warehouse=primary_warehouse)
    
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
