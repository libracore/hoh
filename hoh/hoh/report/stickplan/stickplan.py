# Copyright (c) 2020-2022, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast
from datetime import datetime, timedelta
from hoh.hoh.utils import complete_work_order_details
from frappe.utils import cint

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Work Order"), "fieldname": "work_order", "fieldtype": "Link", "options": "Work Order", "width": 110},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Datetime", "width": 140},
        {"label": _("Sales Order"), "fieldname": "sales_order", "fieldtype": "Link", "options": "Sales Order", "width": 90},        
        {"label": _("Customer name"), "fieldname": "customer_name", "fieldtype": "Data", "width": 150},
        {"label": _("Anmerkung"), "fieldname": "anmerkung", "fieldtype": "Data", "width": 100},
        {"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Rap."), "fieldname": "stickrapport", "fieldtype": "Data", "width": 50},
        {"label": _("Material"), "fieldname": "ready", "fieldtype": "Data", "width": 60},
        {"label": _("Stoff"), "fieldname": "stoff", "fieldtype": "Data", "width": 100},
        {"label": _("Garn"), "fieldname": "garn", "fieldtype": "Data", "width": 200},
        {"label": _("Pailletten"), "fieldname": "pailletten", "fieldtype": "Data", "width": 200},
        {"label": _("Monofil"), "fieldname": "monofil", "fieldtype": "Data", "width": 200},
        {"label": _("Bobinen"), "fieldname": "bobinen", "fieldtype": "Data", "width": 200},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 80},
        {"label": _("Kundenlieferdatum"), "fieldname": "delivery_date", "fieldtype": "Date",  "width": 90},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date",  "width": 90},
        #{"label": _("Nächste Wartung"), "fieldname": "next_maintenance_date", "fieldtype": "Date", "width": 75},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 50},
        {"label": _("UOM"), "fieldname": "uom", "fieldtype": "Data", "width": 50},
        {"label": _("Qty full"), "fieldname": "qty_full", "fieldtype": "Data", "width": 100},
        #{"label": _("Ktm pro h"), "fieldname": "ktm_per_h", "fieldtype": "Float", "precision": 1, "width": 75},
        {"label": _("Ktm"), "fieldname": "ktm", "fieldtype": "Int", "width": 60},
        {"label": _("Ktm ges."), "fieldname": "ktm_total", "fieldtype": "Int", "width": 75},
        {"label": _("h"), "fieldname": "h_total", "fieldtype": "Float", "precision": 1, "width": 50},
        {"label": _("Schicht"), "fieldname": "schicht", "fieldtype": "Float", "precision": 1, "width": 50},
        {"label": _("Stickmaschine"), "fieldname": "stickmaschine", "fieldtype": "Link", "options": "Stickmaschine",  "width": 100},
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
        conditions += """ AND (`tabWork Order`.`planned_start_date` >= '{from_date}' OR `tabWork Order`.`planned_start_date` IS NULL)""".format(from_date=filters['from_date'])
    if 'to_date' in filters and filters['to_date']:
        conditions += """ AND (`tabWork Order`.`planned_start_date` <= '{to_date}' OR `tabWork Order`.`planned_start_date` IS NULL)""".format(to_date=filters['to_date'])
    if 'item' in filters and filters['item']:
        conditions += """ AND `tabWork Order`.`production_item` LIKE '%{item}%'""".format(item=filters['item'])
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
         (SELECT CONCAT(ROUND(`tabSales Order Item`.`anzahl`, 0), " x ", ROUND(`tabSales Order Item`.`verkaufseinheit`, 1), " ", `tabSales Order Item`.`uom`) 
            FROM `tabSales Order Item`
            WHERE `tabSales Order Item`.`item_code` = `tabItem`.`item_code`
              AND `tabSales Order Item`.`parent` = `tabWork Order`.`sales_order`
            LIMIT 1) AS `qty_full`,
         `tabWork Order`.`stock_uom` AS `uom`,
         `tabDessin`.`stickrapport` AS `stickrapport`,
         IFNULL(`tabWork Order`.`stoff`, "-") AS `stoff`,
         IFNULL(`tabWork Order`.`garn`, "-") AS `garn`,
         IFNULL(`tabWork Order`.`pailletten`, "-") AS `pailletten`,
         IFNULL(`tabWork Order`.`monofil`, "-") AS `monofil`,
         IFNULL(`tabWork Order`.`bobinen`, "-") AS `bobinen`,
         IFNULL(`tabWork Order`.`anmerkung`, "-") AS `anmerkung`,
         `tabStickmaschine`.`ktm_per_h` AS `ktm_per_h`,
         `tabStickmaschine`.`next_maintenance_date` AS `next_maintenance_date`,
         `tabDessin`.`gesamtmeter` AS `ktm`,
         (`tabWork Order`.`qty` / `tabStickmaschine`.`m_per_cp`) * `tabDessin`.`gesamtmeter` AS `ktm_total`,
         (((`tabWork Order`.`qty` / `tabStickmaschine`.`m_per_cp`) * `tabDessin`.`gesamtmeter`) / IFNULL(`tabStickmaschine`.`ktm_per_h`, 1)) AS `h_total`,
         ((((`tabWork Order`.`qty` / `tabStickmaschine`.`m_per_cp`) * `tabDessin`.`gesamtmeter`) / IFNULL(`tabStickmaschine`.`ktm_per_h`, 1)) / {hours_per_shift}) AS `schicht`,
         IF (`tabWork Order`.`status` = 'In Process', 
           /* material prepared, show ready date */
          (SELECT CONCAT(SUBSTRING(`tabStock Entry`.`modified`, 9, 2), ".", SUBSTRING(`tabStock Entry`.`modified`, 6, 2), ".")
           FROM `tabStock Entry` 
           WHERE `tabStock Entry`.`stock_entry_type` = "Material Transfer for Manufacture" 
             AND `tabStock Entry`.`docstatus` = 1
             AND `tabStock Entry`.`work_order` = `tabWork Order`.`name`
           LIMIT 1
          ), 
          /* material not prepared, show availability */
          (SELECT 
           IF(SUM(IF(`tWOI`.`required_qty` <= (`tWOI`.`available_qty_at_source_warehouse` + `tWOI`.`available_qty_at_wip_warehouse`), 1, 0)) / COUNT(`tWOI`.`item_code`) = 1, "<span style='color:green;'>&cir; OK</span>", "<span style='color: red;'>&squf; NOK</span>")
           FROM `tabWork Order Item` AS `tWOI`
           WHERE `tWOI`.`parent` = `tabWork Order`.`name`)) AS `ready`
        FROM `tabWork Order`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabWork Order`.`production_item`
        LEFT JOIN `tabDessin` ON `tabDessin`.`name` = `tabItem`.`dessin`
        LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabWork Order`.`sales_order`
        LEFT JOIN `tabStickmaschine` ON `tabWork Order`.`stickmaschine` = `tabStickmaschine`.`name`
        WHERE 
          `tabWork Order`.`docstatus` < 2
          AND `tabWork Order`.`status` NOT IN ("Completed", "Stopped")
          {conditions}
        ORDER BY `tabWork Order`.`stickmaschine` ASC, `tabWork Order`.`planned_start_date` ASC, `tabWork Order`.`expected_delivery_date` ASC;
      """.format(conditions=conditions, hours_per_shift=hours_per_shift)
    
    data = frappe.db.sql(sql_query, as_dict=1)

    # compute indent
    previous_so = None
    row_idx = 0
    header_row_idx = 0
    for row in data:
        if row['sales_order'] == previous_so:
            row['indent'] = 1
        else:
            row['indent'] = 0
            header_row_idx = row_idx
        previous_so = row['sales_order']
        row_idx += 1
        
        # mark material status
        if "NOK" in row['ready']:
            if "background" not in data[header_row_idx]['ready']:
                data[header_row_idx]['ready'] = "<span style='background-color: yellow; '>{0}</span>".format(
                    data[header_row_idx]['ready'])
    return data

@frappe.whitelist()
def update_material_status():
    data = get_data(filters={'stickmaschine': None, 'from_date': None, 'to_date': None})
    frappe.log_error("{0}".format(data))
    for entry in data:
        wo = frappe.get_doc("Work Order", entry['work_order'])
        wo.set_available_qty()
        wo.save()
        # complete details if missing
        if not wo.stoff:
            complete_work_order_details(wo.name)
        # flush cache
        frappe.db.commit()
    return

@frappe.whitelist()
def plan_machine(machine, debug=False):
    data = get_data(filters={'stickmaschine': machine, 'from_date': None, 'to_date': None})
    if debug:
        print("Maschine planning debug for {0}".format(machine))
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
            earliest_start = last_start + timedelta(hours=(settings.work_order_spacing or 0))
            if wo.planned_start_date < (earliest_start):
                wo.planned_start_date = earliest_start
        #last_start = wo.planned_start_date + timedelta(hours=data[i]['h_total']) # add duration so that earliest next start is at end
        last_start = compute_end_datetime(start=wo.planned_start_date, duration_h=data[i]['h_total'])  # earliest start of next work order during working hours
        wo.planned_end_date = last_start
        if debug:
            print("{wo}: planned start at {start} (last_start: {last})".format(
                wo=wo.name, start=wo.planned_start_date, last=last_start))
        wo.save()
    if debug:
        print("done")
    return

""" This function returns planning date for a work order """
@frappe.whitelist()
def get_planning_wo(wo):
    work_order = frappe.get_doc("Work Order", wo)
    previous_date = None
    next_date = None
    if work_order.stickmaschine:
        data = get_data(filters={'stickmaschine': work_order.stickmaschine, 
            'from_date': (work_order.planned_start_date - timedelta(days=30)).date(), 
            'to_date': (work_order.planned_start_date + timedelta(days=30)).date() 
        })
        for row in range(len(data)):
            if data[row]['work_order'] == wo:
                if row > 0:
                    previous_date = data[row - 1]['start_date']
                if row < (len(data) - 1):
                    next_date = data[row + 1]['start_date']
                break
    return {
        'work_order': wo,
        'sales_order': work_order.sales_order,
        'planned_start_date': work_order.planned_start_date,
        'previous_date': previous_date,
        'next_date': next_date,
        'stickmaschine': work_order.stickmaschine
    }

@frappe.whitelist()
def replan_work_order(work_order, sales_order, maschine, target_date, all_sales_order):
    target_date = datetime.strptime(target_date, '%Y-%m-%d %H:%M:%S')
    if cint(all_sales_order) == 1:
        # replan complete work order
        all_wos = frappe.get_all("Work Order", filters=[['sales_order', '=', sales_order], ['docstatus', '<', 2]], 
            fields=['name'], order_by='planned_start_date')
        for wo in all_wos:
            replan(wo['name'], target_date, maschine)
            target_date = target_date + timedelta(seconds=1)
    else:
        # single work order
        replan(work_order, target_date, maschine)
    plan_machine(maschine)
    frappe.db.commit()
    return
    
def replan(work_order, target_date, maschine):
    wo = frappe.get_doc("Work Order", work_order)
    wo.planned_start_date = target_date
    wo.stickmaschine = maschine
    duration_h = wo.kartenmeter / frappe.get_value("Stickmaschine", maschine, 'ktm_per_h')
    wo.planned_end_date = compute_end_datetime(target_date, duration_h)
    wo.save()
    return

def compute_end_datetime(start, duration_h, debug=False):
    # config
    config = frappe.get_doc("HOH Settings", "HOH Settings")
    work_start = {'hour': config.work_start, 'minute': 0}
    work_end = {'hour': config.work_end, 'minute': 0}
    hours_per_day = (datetime(2000,1,1,work_end['hour'],work_end['minute']) -
        datetime(2000,1,1,work_start['hour'],work_start['minute'])).seconds / 3600
    
    holidays = get_holidays(config.holiday_list)

    remaining_h = duration_h or 0
    current_day = start
    end = start
    while (remaining_h > 0):
        if debug:
            print("new day {d} (remaining {r} h".format(d=current_day, r=remaining_h))
        # check if current day is a working day
        if "{y:04}-{m:02}-{d:02}".format(y=current_day.year, m=current_day.month,
            d=current_day.day) in holidays:
            current_day = current_day + timedelta(days=1)
            if debug:
                print("holiday")
            continue
        # when is end of work on current day
        end_of_work = datetime(year=current_day.year,
            month=current_day.month, day=current_day.day,
            hour=work_end['hour'], minute=work_end['minute'])
        # how long until the end of the current day
        hours_today = (end_of_work - current_day).seconds / 3600
        # if less hours required than available --> finish
        if (remaining_h <= hours_today):
            end = current_day + timedelta(hours=remaining_h)
            remaining_h = 0
        else:
            # go to next day
            remaining_h = remaining_h - hours_today
            current_day = (end_of_work - timedelta(hours=hours_per_day) +
               timedelta(days=1))
    return end

def get_holidays(holiday_list):
    sql_query = """SELECT `holiday_date` FROM `tabHoliday` WHERE `parent` = "{h}";""".format(h=holiday_list)
    data = frappe.db.sql(sql_query, as_dict=True)
    dates = []
    for d in data:
        dates.append(d['holiday_date'].strftime("%Y-%m-%d"))
    return dates
