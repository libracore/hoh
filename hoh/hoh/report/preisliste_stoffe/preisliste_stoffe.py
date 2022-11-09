# Copyright (c) 2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast          # to parse str to dict (from JS calls)

def execute(filters=None):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Data", "width": 150},
        {"label": _("Width"), "fieldname": "width", "fieldtype": "Data", "width": 100},
        {"label": _("Composition"), "fieldname": "composition", "fieldtype": "Data", "width": 200},
        {"label": _("Weight"), "fieldname": "weight", "fieldtype": "Data", "width": 100},
        {"label": _("ERP Verkaufspreis"), "fieldname": "rate", "fieldtype": "Currency", "width": 150},
        # {"label": _("Verkaufspreis +20%"), "fieldname": "margin_rate", "fieldtype": "Currency", "width": 150},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]
    return columns

def get_data(filters):
    if 'name' in filters:
        name = "%{0}%".format(filters['name'])
    else:
        name = "%"
    pricelist = frappe.get_value("HOH settings", "HOH Settings", "sales_price_list")
    sql_query = """SELECT *
        FROM
        (
            SELECT
                SUBSTRING_INDEX(`tabItem`.`item_name`, " ", 1) As `item`,
                `tabItem Price`.`price_list_rate` AS `rate`,
                1.2 * `tabItem Price`.`price_list_rate` AS `margin_rate`,
                CONCAT(ROUND(`stoffbreite_von`), "-", ROUND(`stoffbreite_bis`), "cm") AS `width`,
                /* (SELECT REPLACE(GROUP_CONCAT(CONCAT("<img src='",
                    (SELECT `value` FROM `tabSingles` WHERE `doctype` = "HOH Settings" AND `field` = "label_image_host"), 
                     `tabPflegesymbol`.`image`, "' style='width: 20px;' >")
                     ORDER BY `tabPflegesymbol`.`sort` DESC), ",", "&nbsp;")
                    FROM `tabItem Pflegesymbol` 
                    LEFT JOIN `tabPflegesymbol` ON `tabPflegesymbol`.`name` = `tabItem Pflegesymbol`.`pflegesymbol`
                    WHERE `tabBemusterung`.`name` = `tabItem Pflegesymbol`.`parent` AND `tabItem Pflegesymbol`.`parenttype` = "Bemusterung"
               ) AS `pflegesymbole`, */
               (SELECT GROUP_CONCAT(CONCAT(ROUND(`tabItem Komposition`.`anteil`, 0), "% ", `tabItem Komposition`.`material`) ORDER BY `idx` ASC)
                FROM `tabItem Komposition`
                WHERE `tabItem`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Item"
               ) AS `composition`,
               CONCAT(ROUND(`gewicht`),  " g/lfm") AS `weight`
            FROM `tabItem`
            LEFT JOIN `tabItem Price` ON `tabItem`.`item_code` = `tabItem Price`.`item_code` AND `tabItem Price`.`price_list` = "{pricelist}"
            WHERE `tabItem`.`item_group` = "Stoffe"
              AND `tabItem`.`item_name` LIKE "{name}"
        ) AS `raw`
        GROUP By `raw`.`item`;
        """.format(name=name, pricelist=pricelist)
    
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
