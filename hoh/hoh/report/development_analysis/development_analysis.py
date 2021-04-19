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
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 140},
        {"label": _("Customer Name"), "fieldname": "customer_name", "width": 100},
        {"label": _("Customer Group"), "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 100},
        {"label": _("Territory"), "fieldname": "territory", "fieldtype": "Link", "options": "Territory", "width": 100},
        {"label": _("Kollektion"), "fieldname": "kollektion", "fieldtype": "Link", "options": "Kollektion", "width": 100},
        {"label": _("DWG"), "fieldname": "dwg", "fieldtype": "Data", "width": 100},
        {"label": _("Anzahl Dessins"), "fieldname": "dessin_count", "fieldtype": "Int", "width": 50},
        {"label": _("Entwicklungskosten"), "fieldname": "develpment_cost", "fieldtype": "Currency", "width": 100},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]

@frappe.whitelist()
def get_data(filters):
    filter_str = ""
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)

    filter_str = """ `tabDessin`.`creation` >= '{0}' AND `tabDessin`.`creation` <= '{1}'""".format(filters['from_date'], filters['to_date'])
    group_str = """ GROUP BY `customer` """
    if 'territory' in filters:
        filter_str += """ AND `tabItem`.`item_code` = '{item_code}'""".format(item_code=filters['territory'])
    if 'kollektion' in filters:
        filter_str += """ AND `tabItem`.`item_name` LIKE '%{item_name}%'""".format(item_name=filters['kollektion'])
    if 'customer_group' in filters:
        filter_str += """ AND `tabItem`.`item_group` = '{item_group}'""".format(item_group=filters['customer_group'])
    if filters['gruppierung'] == "Nach DWG":
        group_str = """ GROUP BY `dwg` """
    elif filters['gruppierung'] == "Nach Kundengruppe":
        group_str = """ GROUP BY `customer_group` """
    elif filters['gruppierung'] == "Nach Region":
        group_str = """ GROUP BY `territory` """
        
    sql_query = """
                SELECT  
                    `dessin`,
                    `customer`,
                    `customer_name`,
                    `dwg`,
                    `territory`,
                    `customer_group`,
                    `kollektion`,
                    COUNT(`dessin_count`) AS `dessin_count`,
                    SUM(`develpment_cost`) AS `develpment_cost`
                FROM
                (SELECT 
                    `tabDessin`.`name` AS `dessin`,
                    IFNULL(`tabDessin`.`customer`, "-") AS `customer`,
                    IFNULL(`tabDessin`.`customer_name`, "-") AS `customer_name`,
                    IFNULL(`tabDessin`.`dwg_nummer`, "-") AS `dwg`,
                    IFNULL(`tabCustomer`.`territory`, "-") AS `territory`,
                    IFNULL(`tabCustomer`.`customer_group`, "-") AS `customer_group`,
                    IFNULL((SELECT `kollektion` 
                     FROM `tabBemusterung` 
                     WHERE `tabBemusterung`.`dessin` = `tabDessin`.`name` 
                     LIMIT 1), "-") AS `kollektion`,
                    `tabDessin`.`name` AS `dessin_count`,
                    `tabDessin`.`entwicklungskosten` AS `develpment_cost`
                FROM `tabDessin`
                LEFT JOIN `tabCustomer` ON `tabDessin`.`customer` = `tabCustomer`.`name`
                WHERE {filter_str}) AS`raw`
            {group_str};""".format(
              filter_str=filter_str, group_str=group_str)

    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
