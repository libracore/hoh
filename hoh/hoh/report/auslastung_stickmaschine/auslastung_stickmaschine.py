# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime
import json

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    # strip datetime into date
    for d in data:
        try:
            d['start_date'] = d['start_date'].date()
        except:
            d['start_date'] = None
        try:
            d['end_date'] = d['end_date'].date()
        except:
            d['end_date'] = None
    return columns, data

def get_columns():
    return [
        {"label": _("Stickmaschine"), "fieldname": "stickmaschine", "fieldtype": "Link", "options": "Stickmaschine",  "width": 100},
        {"label": _("Work Orders"), "fieldname": "work_order_count", "fieldtype": "Int",  "width": 90},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 90},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date",  "width": 90},
        {"label": _("Ktm pro h"), "fieldname": "ktm_per_h", "fieldtype": "Float", "precision": 1, "width": 75},
        {"label": _("Ktm"), "fieldname": "ktm", "fieldtype": "Int", "width": 75},
        {"label": _("Ktm ges."), "fieldname": "ktm_total", "fieldtype": "Int", "width": 75},
        {"label": _("h ges."), "fieldname": "h_total", "fieldtype": "Int", "width": 75}
    ]

def get_data(filters):
    if type(filters) == str:
        filters = json.loads(filters)
    if not "stickmaschine" in filters:
        filters['stickmaschine'] = "%"
    else:
        filters['stickmaschine'] = "%{0}%".format(filters['stickmaschine'])
        
    sql_query = """
       SELECT 
         `raw`.`stickmaschine` AS `stickmaschine`,
         `raw`.`ktm_per_h` AS `ktm_per_h`,
         `raw`.`next_maintenance_date` AS `next_maintenance_date`,
         `raw`.`work_order_count` AS `work_order_count`,
         `raw`.`start_date` AS `start_date`,
         `raw`.`end_date` AS `end_date`,
         `raw`.`ktm` AS `ktm`,
         `raw`.`ktm_total` AS `ktm_total`,
         (IFNULL(`raw`.`ktm_total`, 0) / IF(IFNULL(`raw`.`ktm_per_h`, 0) = 0, 0.01, `raw`.`ktm_per_h`)) AS `h_total`
       FROM 
        (SELECT
           `tabStickmaschine`.`name` AS `stickmaschine`,
           `tabStickmaschine`.`ktm_per_h` AS `ktm_per_h`,
           `tabStickmaschine`.`next_maintenance_date` AS `next_maintenance_date`,
           `details`.`work_order_count` AS `work_order_count`,
           `details`.`start_date` AS `start_date`,
           `details`.`end_date` AS `end_date`,
           `details`.`ktm` AS `ktm`,
           `details`.`ktm_total` AS `ktm_total`
         FROM `tabStickmaschine` 
         JOIN (SELECT
             COUNT(`tabWork Order`.`name`) AS `work_order_count`,
             (SELECT MIN(`tabW1`.`planned_start_date`)
              FROM `tabWork Order` AS `tabW1`
              WHERE `tabW1`.`docstatus` < 2
               AND `tabW1`.`status` != "Completed"
               AND `tabW1`.`stickmaschine` = `tabWork Order`.`stickmaschine`
             ) AS `start_date`,
             (SELECT MAX(`tabW2`.`planned_end_date`)
              FROM `tabWork Order` AS `tabW2`
              WHERE `tabW2`.`docstatus` < 2
               AND `tabW2`.`status` != "Completed"
               AND `tabW2`.`stickmaschine` = `tabWork Order`.`stickmaschine`
             ) AS `end_date`,
             SUM(`tabDessin`.`gesamtmeter`) AS `ktm`,
             SUM(`tabWork Order`.`qty` * `tabDessin`.`gesamtmeter`) AS `ktm_total`,
             `tabWork Order`.`stickmaschine` AS `stickmaschine`
           FROM `tabWork Order`
           LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabWork Order`.`production_item`
           LEFT JOIN `tabDessin` ON `tabDessin`.`name` = `tabItem`.`dessin`
           WHERE 
             `tabWork Order`.`docstatus` < 2
             AND `tabWork Order`.`status` != "Completed"
           GROUP BY `tabWork Order`.`stickmaschine`
          ) AS `details` ON (`tabStickmaschine`.`name` = `details`.`stickmaschine`)
        WHERE `tabStickmaschine`.`name` LIKE "{stickmaschine}"
        ) AS `raw`
        ORDER BY `raw`.`stickmaschine` ASC;
      """.format(stickmaschine=filters['stickmaschine'])

    data = frappe.db.sql(sql_query, as_dict=1)
        
    return data

def get_planned_until(maschine):
    data = get_data({'stickmaschine': maschine})
    if len(data) > 0:
        return data[0]['end_date'] or datetime.now()
    else:
        return datetime.now()
