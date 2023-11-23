# Copyright (c) 2023, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, keys = get_columns()
    data = get_data(filters, keys)
    return columns, data

def get_columns():
    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 120}
    ]
    stickmaschinen = frappe.get_all("Stickmaschine", filters={'disabled': 0}, fields=['name'], order_by='name')
    schichten = frappe.get_all("Schicht", fields=['name', 'kurzzeichen'], order_by='name')
    keys = {}
    for m in range(0, len(stickmaschinen)):
        for s in range(0, len(schichten)):
            keys["k_{m}_{s}".format(m=m, s=s)] = {
                'stickmaschine': stickmaschinen[m]['name'],
                'schicht': schichten[s]['name'],
                'titel': "{0} {1}".format(stickmaschinen[m]['name'], schichten[s]['kurzzeichen'])
            }
            columns.append({
                "label": keys["k_{m}_{s}".format(m=m, s=s)]['titel'], 
                "fieldname": "k_{m}_{s}".format(m=m, s=s), 
                "fieldtype": "Float", 
                "width": 120
            })
            
    return columns, keys
    
def get_data(filters, keys):
    data = []
    months = [_("January"), _("February"), _("March"),
        _("April"), _("May"), _("June"),
        _("July"), _("August"), _("September"),
        _("October"), _("November"), _("December")]
        
    for month in range(1, 13):
        data.append({
            'month': "{0} {1}".format(months[(month - 1)], filters['year'])
        })
        for k, v in keys.items():
            #prepare query for each month
            sql_query = """SELECT 
                    SUM(IFNULL(((`tabWork Order`.`qty` / `tabStickmaschine`.`m_per_cp`) * `tabDessin`.`gesamtmeter`), 0)) AS `total_ktm`,
                    SUM(IFNULL(`tabWork Order`.`summe_maschinenstunden`, 0)) AS `h_total`,
                    SUM(IFNULL(`tabWork Order Nutzung`.`maschinenstunden`, 0)) AS `h_schicht`
                FROM `tabWork Order Nutzung` 
                LEFT JOIN `tabWork Order` ON `tabWork Order`.`name` = `tabWork Order Nutzung`.`parent`
                LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabWork Order`.`production_item`
                LEFT JOIN `tabDessin` ON `tabDessin`.`name` = `tabItem`.`dessin`
                LEFT JOIN `tabStickmaschine` ON `tabStickmaschine`.`name` = `tabWork Order`.`stickmaschine`
                WHERE `tabWork Order`.`docstatus` < 2
                    AND `tabWork Order Nutzung`.`start` LIKE "{year}-{month:02d}-%" 
                    AND `tabWork Order`.`stickmaschine` = "{maschine}" 
                    AND `tabWork Order Nutzung`.`schicht` = "{schicht}";""".format(
                    year=filters.year, month=month, schicht=v['schicht'], maschine=v['stickmaschine'])
            ktm_per_h = frappe.db.sql(sql_query, as_dict=True)

            data[-1][k] = ktm_per_h[0]['h_total']
    return data

