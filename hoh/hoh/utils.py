# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _

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
        elif item.item_group == "Stoffe" or item.item_group == "Hilfsstoffe":
            stoffe.append(item.item_name)
        elif item.item_group == "Pailletten":
            pailletten.append(item.item_name)
        elif item.item_group == "Monofil":
            monofil.append(item.item_name)
        elif item.item_group == "Bobinen":
            bobinen.append(item.item_name)
    details = {
        'garne': " + ".join(garne),
        'stoffe': " + ".join(stoffe),
        'pailletten': " + ".join(pailletten),
        'monofil': " + ".join(monofil),
        'bobinen': " + ".join(bobinen),
        'kartenmeter': dessin.gesamtmeter
    }
    if len(dessin.stickmaschine) > 0:
        details['stickmaschine'] = dessin.stickmaschine[0].stickmaschine
    return details
    
def complete_work_order_details(work_order):
    wo = frappe.get_doc("Work Order", work_order)
    if wo.production_item:
        details = compile_details(bemusterung)
        wo.garne = details['garne']
        wo.stoffe = details['stoffe']
        wo.pailletten = details['pailletten']
        wo.monofil = details['monofil']
        wo.bobinen = details['bobinen']
        wo.kartenmeter = details['kartenmeter']
        wo.stickmaschine = details['stickmaschine'] if 'stickmaschine' in details else None
        wo.save()
    return
