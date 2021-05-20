# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters):
    columns = get_columns()
    data = get_data()
    return columns, data

def get_columns():
    return [
        {"label": _("Stickmaschine"), "fieldname": "stickmaschine", "fieldtype": "Link", "options": "Stickmaschine", "width": 120},
        {"label": _("Sum Work Orders"), "fieldname": "sum_work_order", "fieldtype": "Data", "width": 140},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 100}
    ]

def get_data():
    sql_query = """
        SELECT
          `tabWork Order`.`stickmaschine` AS `stickmaschine`,
          COUNT(name) AS `sum_work_order`,
          MAX(`tabWork Order`.`expected_delivery_date`) AS `end_date`
        FROM `tabWork Order`
        WHERE 
          `tabWork Order`.`docstatus` < 2 AND `tabWork Order`.`status` NOT IN ("Completed", "Stopped", "Closed")
        GROUP BY `tabWork Order`.`stickmaschine`
        ORDER BY `tabWork Order`.`stickmaschine` ASC
        """.format()
        
    data = frappe.db.sql(sql_query, as_dict=1)
    
    return data
