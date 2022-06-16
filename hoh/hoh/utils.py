# Copyright (c) 2019-2022, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _, get_print
from datetime import datetime
from hoh.hoh.report.auslastung_stickmaschine.auslastung_stickmaschine import get_planned_until

@frappe.whitelist()
def get_batch_info(item_code):
    sql_query = """SELECT 
          `batches`.`item_code`, 
          `batches`.`batch_no`, 
          `batches`.`qty`, 
        FROM (
          SELECT `item_code`, `batch_no`, SUM(`actual_qty`) AS `qty`
          FROM `tabStock Ledger Entry`        
          WHERE `item_code` = '{item_code}'
          GROUP BY `batch_no`) AS `batches`
        LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `batches`.`item_code`
        WHERE `qty` > 0;""".format(item_code=item_code)
    
    data = frappe.db.sql(sql_query, as_dict=1)
    return data

"""
   :params:
   item_code_pattern: "CAI%": item_code mask to find items
   price_list: name of target price list
   rate: set this rate
"""
@frappe.whitelist()
def bulk_set_prices(item_code_pattern, price_list, rate):
    # find applicable items
    sql_query = """SELECT `name` 
                   FROM `tabItem`
                   WHERE `tabItem`.`item_code` LIKE '{pattern}' 
                     AND `tabItem`.`disabled` = 0;""".format(pattern=item_code_pattern)
    applicable_items = frappe.db.sql(sql_query, as_dict=True)
    updated_item_prices = []
    # loop through items
    for item in applicable_items:
        # check if item price exists
        item_prices = frappe.get_all("Item Price", filters={'item_code': item['name'], 'price_list': price_list}, fields=['name'])
        if item_prices:
            # update existing price record
            item_price = frappe.get_doc("Item Price", item_prices[0]['name'])
            item_price.price_list_rate = rate
            item_price.save()
            updated_item_prices.append(item_price.name)
        else:
            # create new item price record
            new_item_price = frappe.get_doc({
                'doctype': 'Item Price',
                'item_code': item['name'],
                'price_list': price_list,
                'price_list_rate': rate
            })
            new_record = new_item_price.insert()
            updated_item_prices.append(new_record.name)
    # write changes to database
    frappe.db.commit()
    return updated_item_prices

@frappe.whitelist()
def compile_details(bemusterung):
    # collect values from bemusterung > BOM
    bemusterung = frappe.get_doc("Bemusterung", bemusterung)
    dessin = frappe.get_doc("Dessin", bemusterung.dessin)
    garne = []
    stoffe = []
    pailletten = []
    monofil = []
    bobinen = []
    for item in bemusterung.items:
        if item.item_group == "Garne" or item.item_group == "Kordel":
            garne.append(item.item_name)
        elif item.item_group == "Stoffe" or item.item_group == "Eigenware Stoffe" or item.item_group == "Hilfsstoffe":
            stoffe.append(item.item_name)
        elif item.item_group == "Pailletten":
            pailletten.append(item.item_name)
        elif item.item_group == "Monofil":
            monofil.append(item.item_name)
        elif item.item_group == "Bobinen":
            bobinen.append(item.item_code)
    finish_steps = []
    for fs in bemusterung.finish_steps:
        finish_steps.append({
            'finish_step': fs.finish_step,
            'supplier': fs.supplier,
            'supplier_name': fs.supplier_name,
            'remarks': fs.remarks
        })
    details = {
        'garne': " + ".join(garne),
        'stoffe': " + ".join(stoffe),
        'pailletten': " + ".join(pailletten),
        'monofil': " + ".join(monofil),
        'bobinen': " + ".join(bobinen),
        'kartenmeter': dessin.gesamtmeter,
        'finish_steps': finish_steps
    }
    if len(dessin.stickmaschine) > 0:
        details['stickmaschine'] = dessin.stickmaschine[0].stickmaschine
        details['start_date'] = get_start_date(dessin.stickmaschine[0].stickmaschine)
    return details

def get_start_date(stickmaschine):
    return get_planned_until(stickmaschine)
    
def complete_work_order_details(work_order):
    wo = frappe.get_doc("Work Order", work_order)
    if wo.production_item:
        details = compile_details(wo.production_item)
        wo.stickmaschine = details['stickmaschine'] if 'stickmaschine' in details else None
        wo.kartenmeter = details['kartenmeter']
        # if this has not sequin details, it is fresh from a Sales Order
        if not wo.stoff and not wo.garn:
            # set start date as last date of the machine
            if wo.stickmaschine:
                wo.planned_start_date = get_start_date(wo.stickmaschine)
        wo.garn = details['garne']
        wo.stoff = details['stoffe']
        wo.pailletten = details['pailletten']
        wo.monofil = details['monofil']
        wo.bobinen = details['bobinen']
        wo.finish_steps = []
        for fs in details['finish_steps']:
            row = wo.append('finish_steps', {
                'finish_step': fs['finish_step'],
                'supplier': fs['supplier'],
                'supplier_name': fs['supplier_name'],
                'remarks': fs['remarks']
            })
        wo.save()
    return

def write_local_pdf(doctype, docname, print_format, target, language=None):
    # set language
    if language:
        frappe.local.lang = language
    # get pdf output
    pdf = get_print(doctype=doctype, name=docname, print_format=print_format, as_pdf=True)
    # save file
    with open(target, 'wb') as f:
        f.write(pdf)
    return

@frappe.whitelist()
def set_wo_timetracking(work_order):
    wo = frappe.get_doc("Work Order", work_order)
    if wo.nutzungen and (len(wo.nutzungen) > 0) and (not wo.nutzungen[-1].end):
        wo.nutzungen[-1].end = datetime.now()
        hours = round(((wo.nutzungen[-1].end - wo.nutzungen[-1].start).total_seconds() / 3600), 2)
        wo.nutzungen[-1].maschinenstunden = hours
        # update total hours
        total_hours = 0
        for n in wo.nutzungen:
            total_hours += n.maschinenstunden
        wo.summe_maschinenstunden = total_hours
    else:
        row = wo.append('nutzungen', {
            'start': datetime.now()
        })
    wo.save()
    return

@frappe.whitelist()
def update_pinv_to_price_list(pinv):
    pi = frappe.get_doc("Purchase Invoice", pinv)
    buying_price_lists = frappe.get_all("Price List", filters={'enabled': 1, 'buying': 1}, fields=['name'])
    buying_price_list = buying_price_lists[0]['name']
    for item in pi.items:
        item_prices = frappe.get_all("Item Price", filters={'item_code': item.item_code, 'buying': 1, 'price_list': buying_price_list}, fields=['name'])
        if len(item_prices) > 0:
            item_price = frappe.get_doc("Item Price", item_prices[0]['name'])
            item_price.price_list_rate = item.rate
            item_price.save()
        else:
            item_price = frappe.get_doc({
                'doctype': "Item Price",
                'item_code': item.item_code,
                'selling': 0,
                'buying': 1,
                'price_list_rate': item.rate,
                'price_list': buying_price_list
            })
            item_price.insert()
    return

"""
Write changed weight values (default current day) to bmeusterung
"""
def update_bemusterung_weight_from_item(date=None, debug=False):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    sql_query = """SELECT `name`, `bemusterung`, `gewicht` 
                   FROM `tabItem`
                   WHERE DATE(`modified`) >= "{date}"
                     AND `bemusterung` IS NOT NULL
                     AND `gewicht` IS NOT NULL
                     AND `gewicht` > 0
                     AND `disabled` = 0;""".format(date=date)
    items = frappe.db.sql(sql_query, as_dict=True)
    if items and len(items) > 0:
        for item in items:
            bemusterung = frappe.get_doc("Bemusterung", item['bemusterung'])
            bemusterung.gewicht = item['gewicht'] / 1000        # item weight is in g/m, bemusterung is in kg/m
            try:
                bemusterung.save()
            except Exception as err:
                frappe.log_error("{0}: {1}".format(item['name'], err), "Update weights from items (cron)")
            if debug:
                print("Updated {0}".format(item['name']))
    frappe.db.commit()
    return
