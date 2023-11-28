# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    return [
        {'fieldname': 'stickmaschine', 'label': _("Stickmaschine"), 'fieldtype': 'Link', 'options': 'Stickmaschine', 'width': 200},
        {'fieldname': 'revenue', 'label': _("Umsatz"), 'fieldtype': 'Currency', 'width': 100},
        {'fieldname': 'count', 'label': _("Anzahl"), 'fieldtype': 'Int', 'width': 100}
    ]
    
def get_data(filters):
    data = frappe.db.sql("""
        SELECT 
            `tabWork Order`.`stickmaschine` AS `stickmaschine`,
            SUM(`tabSales Order Item`.`base_net_amount`) AS `revenue`,
            COUNT(`tabWork Order`.`name`) AS `count`
        FROM `tabWork Order`
        LEFT JOIN `tabSales Order Item` ON `tabSales Order Item`.`name` = `tabWork Order`.`sales_order_item`
        LEFT JOIN `tabSales Order` ON `tabSales Order Item`.`parent` = `tabSales Order`.`name`
        WHERE 
            `tabWork Order`.`planned_start_date` BETWEEN "{year}-01-01" AND "{year}-12-31"
            AND `tabWork Order`.`stickmaschine` LIKE "{stickmaschine}"
            AND `tabSales Order`.`customer` LIKE "{customer}"
            AND `tabSales Order`.`name` LIKE "{sales_order}"
            AND `tabWork Order`.`name` LIKE "{work_order}"
        GROUP BY `tabWork Order`.`stickmaschine`
        ORDER BY SUM(`tabSales Order Item`.`base_net_amount`) DESC;
    """.format(
        year=filters.year,
        stickmaschine=filters.stickmaschine or "%",
        customer=filters.customer or "%",
        sales_order=filters.sales_order or "%",
        work_order=filters.work_order or "%"
    ), as_dict=True)
    
    return data
