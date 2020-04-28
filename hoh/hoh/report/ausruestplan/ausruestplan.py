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
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 80},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Kundenlieferdatum"), "fieldname": "delivery_date", "fieldtype": "Date",  "width": 90},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 90},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date",  "width": 90},
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 100},
        {"label": _("Anmerkung"), "fieldname": "anmerkung", "fieldtype": "Data", "width": 100},
    ]

def get_data(filters):       
    sql_query = """SELECT
         `tabWork Order`.`name` AS `work_order`,
         IFNULL(`tabWork Order`.`sales_order`, "-") AS `sales_order`,
         "Ausrüsten" AS `status`, 
         IFNULL(`tabSales Order`.`customer`, "-") AS `customer`,
         IFNULL(`tabSales Order`.`customer_name`, "-") AS `customer_name`,
         `tabSales Order`.`delivery_Date` AS `delivery_date`,
         SUBSTRING_INDEX(`tabWork Order`.`planned_start_date`, ' ', 1)  AS `start_date`,
         `tabWork Order`.`expected_delivery_date` AS `end_date`,
         `tabWork Order`.`production_item` AS `item`,
         `tabWork Order`.`qty` AS `qty`,
         `tabWork Order`.`stock_uom` AS `uom`,
         `tabWork Order`.`anmerkung` AS `anmerkung`
        FROM `tabWork Order`
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabWork Order`.`sales_order`
        WHERE 
          `tabWork Order`.`docstatus` < 2
          AND `tabWork Order`.`status` = "Completed"
          AND `tabWork Order`.`ausruestung_fertig` = 0
        ORDER BY `tabWork Order`.`expected_delivery_date` ASC;
      """

    data = frappe.db.sql(sql_query, as_dict=1)

    return data
