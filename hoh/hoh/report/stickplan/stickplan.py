# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast
from datetime import datetime, timedelta
from hoh-hoh.utils import complete_work_order_details

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 100},
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Rap."), "fieldname": "stickrapport", "fieldtype": "Data", "width": 50},
        {"label": _("Materialstatus"), "fieldname": "ready", "fieldtype": "Data", "width": 120},
        {"label": _("Stoff"), "fieldname": "stoff", "fieldtype": "Data", "width": 100},
        {"label": _("Garn"), "fieldname": "garn", "fieldtype": "Data", "width": 100},
        {"label": _("Pailletten"), "fieldname": "pailletten", "fieldtype": "Data", "width": 100},
        {"label": _("Monofil"), "fieldname": "monofil", "fieldtype": "Data", "width": 100},
        {"label": _("Bobinen"), "fieldname": "bobinen", "fieldtype": "Data", "width": 100},
        {"label": _("Stickmaschine"), "fieldname": "stickmaschine", "fieldtype": "Link", "options": "Stickmaschine",  "width": 100},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 100},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 80},
        {"label": _("Kundenlieferdatum"), "fieldname": "delivery_date", "fieldtype": "Date",  "width": 90},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Datetime", "width": 140},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date",  "width": 90},
        {"label": _("Nächste Wartung"), "fieldname": "next_maintenance_date", "fieldtype": "Date", "width": 75},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 100},
        {"label": _("Anmerkung"), "fieldname": "anmerkung", "fieldtype": "Data", "width": 100},
        {"label": _("Ktm pro h"), "fieldname": "ktm_per_h", "fieldtype": "Float", "precision": 1, "width": 75},
        {"label": _("Ktm"), "fieldname": "ktm", "fieldtype": "Int", "width": 75},
        {"label": _("Ktm ges."), "fieldname": "ktm_total", "fieldtype": "Int", "width": 75},
        {"label": _("h"), "fieldname": "h_total", "fieldtype": "Float", "precision": 1, "width": 50},
        {"label": _("Schicht"), "fieldname": "schicht", "fieldtype": "Float", "precision": 1, "width": 50},
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    # get additional conditions
    conditions = ""
    if 'stickmaschine' in filters and filters['stickmaschine']:
        conditions += """ AND `tabWork Order`.`stickmaschine` = "{0}" """.format(filters['stickmaschine'])
    if 'from_date' in filters and filters['from_date']:
        conditions += """ AND (`tabWork Order`.`expected_delivery_date` >= '{from_date}' OR `tabWork Order`.`expected_delivery_date` IS NULL)""".format(from_date=filters['from_date'])
    if 'to_date' in filters and filters['to_date']:
        conditions += """ AND (`tabWork Order`.`expected_delivery_date` <= '{to_date}' OR `tabWork Order`.`expected_delivery_date` IS NULL)""".format(to_date=filters['to_date'])
    if 'item_code' in filters and filters['item_code']:
        conditions += """ AND `tabWork Order`.`production_item` = '{item_code}'""".format(item_code=filters['item_code'])
    if 'sales_order' in filters and filters['sales_order']:
        conditions += """ AND `tabWork Order`.`sales_order` = '{sales_order}'""".format(sales_order=filters['sales_order'])
    # get shift hours
    company = frappe.defaults.get_global_default('company')
    hours_per_shift = frappe.get_value('Company', company, 'h_pro_schicht') 
    
    # prepare query
    sql_query = """SELECT
         `tabWork Order`.`name` AS `work_order`,
         IFNULL(`tabWork Order`.`sales_order`, "-") AS `sales_order`,
         `tabWork Order`.`status` AS `status`, 
         IFNULL(`tabSales Order`.`customer`, "-") AS `customer`,
         IFNULL(`tabSales Order`.`customer_name`, "-") AS `customer_name`,
         `tabSales Order`.`delivery_Date` AS `delivery_date`,
         `tabWork Order`.`planned_start_date` AS `start_date`,
         `tabWork Order`.`expected_delivery_date` AS `end_date`,
         `tabWork Order`.`stickmaschine` AS `stickmaschine`,
         `tabWork Order`.`production_item` AS `item`,
         `tabWork Order`.`qty` AS `qty`,
         `tabWork Order`.`stock_uom` AS `uom`,
         `tabDessin`.`stickrapport` AS `stickrapport`,
         `tabWork Order`.`stoff` AS `stoff`,
         `tabWork Order`.`garn` AS `garn`,
         `tabWork Order`.`pailletten` AS `pailletten`,
         `tabWork Order`.`monofil` AS `monofil`,
         `tabWork Order`.`bobinen` AS `bobinen`,
         `tabWork Order`.`anmerkung` AS `anmerkung`,
         `tabStickmaschine`.`ktm_per_h` AS `ktm_per_h`,
         `tabStickmaschine`.`next_maintenance_date` AS `next_maintenance_date`,
         `tabDessin`.`gesamtmeter` AS `ktm`,
         (`tabWork Order`.`qty` / 9.1) * `tabDessin`.`gesamtmeter` AS `ktm_total`,
         (((`tabWork Order`.`qty` / 9.1) * `tabDessin`.`gesamtmeter`) / IFNULL(`tabStickmaschine`.`ktm_per_h`, 1)) AS `h_total`,
         ((((`tabWork Order`.`qty` / 9.1) * `tabDessin`.`gesamtmeter`) / IFNULL(`tabStickmaschine`.`ktm_per_h`, 1)) / {hours_per_shift}) AS `schicht`,
         (SELECT 
          IF(SUM(IF(`tWOI`.`required_qty` <= (`tWOI`.`available_qty_at_source_warehouse` + `tWOI`.`available_qty_at_wip_warehouse`), 1, 0)) / COUNT(`tWOI`.`item_code`) = 1, "<span style='color:green;'>&cir; OK</span>", "<span style='color: red;'>&squf; NOK</span>")
          FROM `tabWork Order Item` AS `tWOI`
          WHERE `tWOI`.`parent` = `tabWork Order`.`name`) AS `ready`
        FROM `tabWork Order`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabWork Order`.`production_item`
        LEFT JOIN `tabDessin` ON `tabDessin`.`name` = `tabItem`.`dessin`
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabWork Order`.`sales_order`
        LEFT JOIN `tabStickmaschine` ON `tabWork Order`.`stickmaschine` = `tabStickmaschine`.`name`
        WHERE 
          `tabWork Order`.`docstatus` < 2
          AND `tabWork Order`.`status` != "Completed"
          {conditions}
        ORDER BY `tabDessin`.`stickmaschine` ASC, `tabWork Order`.`planned_start_date` ASC, `tabWork Order`.`expected_delivery_date` ASC;
      """.format(conditions=conditions, hours_per_shift=hours_per_shift)

    data = frappe.db.sql(sql_query, as_dict=1)

    return data

@frappe.whitelist()
def update_material_status():
    data = get_data(filters={'stickmaschine': None, 'from_date': None, 'to_date': None})
    for entry in data:
        wo = frappe.get_doc("Work Order", entry['work_order'])
        wo.set_available_qty()
        wo.save()
        # complete details if missing
        if not wo.stoffe:
            complete_work_order_details(wo.name)
    return

@frappe.whitelist()
def plan_machine(machine):
    data = get_data(filters={'stickmaschine': machine, 'from_date': None, 'to_date': None})
    now = datetime.now()
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    last_start = now
    for i in range(len(data)):
        wo = frappe.get_doc("Work Order", data[i]['work_order'])
        if i == 0 and wo.status in ('Draft', 'Not Started'):
            # first planning row: if not started and in the past, move to now
            if wo.planned_start_date < now:
                wo.planned_start_date = now
        else:
            # other rows: at least (duration + break)
            earliest_start = last_start + timedelta(hours=(settings.work_order_spacing or 1))
            if wo.planned_start_date < (earliest_start):
                wo.planned_start_date = earliest_start
        last_start = wo.planned_start_date + timedelta(hours=data[i]['h_total']) # add duration so that earliest next start is at end
        wo.save()
    return
