# -*- coding: utf-8 -*-
# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast          # to parse str to dict (from JS calls)

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 100},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 100},
        {"label": _("An Lager"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
        {"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 50},
        {"label": _("Verkaufspreis"), "fieldname": "price_list_rate", "fieldtype": "Currency", "width": 100},
        {"label": _("Wert"), "fieldname": "value", "fieldtype": "Currency", "width": 100},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]

@frappe.whitelist()
def get_data(filters):
    item_code_filter = ""
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    if 'warehouse' in filters:
        item_code_filter = """ `tabBin`.`warehouse` = '{warehouse}'""".format(warehouse=filters['warehouse'])
    else:
        item_code_filter = """ `tabBin`.`warehouse` LIKE '%'"""
    if 'item_code' in filters:
        item_code_filter += """ AND `tabItem`.`item_code` = '{item_code}'""".format(item_code=filters['item_code'])
    if 'item_name' in filters:
        item_code_filter += """ AND `tabItem`.`item_name` LIKE '%{item_name}%'""".format(item_name=filters['item_name'])
    if 'item_group' in filters:
        item_code_filter += """ AND `tabItem`.`item_group` = '{item_group}'""".format(item_group=filters['item_group'])
    
    sql_query = """SELECT *, (`raw`.`actual_qty` * `raw`.`price_list_rate`)  AS `value`
                   FROM (SELECT 
                    `tabBin`.`item_code` AS `item_code`,
                    `tabItem`.`item_name` AS `item_name`,
                    `tabItem`.`item_group` AS `item_group`,
                    `tabItem`.`stock_uom` AS `stock_uom`,
                    `tabItem`.`safety_stock` AS `safety_stock`,
                    `tabBin`.`warehouse` As `warehouse`,
                    IFNULL(`tabBin`.`actual_qty`, 0) AS `actual_qty`,
                    IFNULL((SELECT `price_list_rate` 
                     FROM `tabItem Price`
                     WHERE `tabItem Price`.`item_code` = `tabBin`.`item_code`
                       AND `tabItem Price`.`selling` = 1
                       AND `tabItem Price`.`currency` = "EUR"
                     LIMIT 1), 0) AS `price_list_rate`
                FROM `tabBin`
                LEFT JOIN `tabItem` ON `tabBin`.`item_code` = `tabItem`.`name`
                WHERE `tabBin`.`actual_qty` > 0 AND {item_code_filter}) AS `raw`;""".format(
              item_code_filter=item_code_filter)

    data = frappe.db.sql(sql_query, as_dict=True)
        
    # add totals
    totals = {'qty': 0, 'value': 0}
    for r in data:
        totals['qty'] += r['actual_qty']
        totals['value'] += r['value']
    data.append({
        'item_code': "",
        'item_name': "Total",
        'actual_qty': totals['qty'],
        'value': totals['value']
    })

    return data
