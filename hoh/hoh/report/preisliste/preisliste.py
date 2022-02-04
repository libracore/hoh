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
        {"label": _("Verkaufspreis +20%"), "fieldname": "margin_rate", "fieldtype": "Currency", "width": 150},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]
    return columns

def get_data(filters):
    if 'name' in filters:
        name = "%{0}%".format(filters['name'])
    else:
        name = "%"
        
    sql_query = """SELECT *
        FROM
        (
            SELECT
                SUBSTRING_INDEX(`name`, " ", 1) As `item`,
                `rate` AS `rate`,
                1.2 * `rate` AS `margin_rate`,
                CONCAT(ROUND(`fertigbreite_von`), "-", ROUND(`fertigbreite_bis`), "cm") AS `width`,
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
                WHERE `tabBemusterung`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Bemusterung"
               ) AS `composition`,
               CONCAT(ROUND(`gewicht`),  " g/lfm") AS `weight`
            FROM `tabBemusterung`
            WHERE `rate` > 0
              AND `name` LIKE "{name}"
        ) AS `raw`
        GROUP By `raw`.`item`;
        """.format(name=name)
    
    data = frappe.db.sql(sql_query, as_dict=True)
    
    return data
