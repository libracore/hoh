# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 110},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 110},
        {"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Data", "width": 50},
        {"label": _("Age"), "fieldname": "age", "fieldtype": "Float", "precission": 2, "width": 50},
        {"label": _("Voucher"), "fieldname": "voucher_no", "fieldtype": "Data", "width": 120},
        {"label": _("Rate"), "fieldname": "valuation_rate", "fieldtype": "Currency", "width": 80},
        {"label": _("Value"), "fieldname": "value", "fieldtype": "Currency", "width": 100},
        {"label": _("Reduced Value"), "fieldname": "reduced_value", "fieldtype": "Currency", "width": 150},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 20}
    ]

def get_data(filters):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    if not 'item_group' in filters:
        filters['item_group'] = "%"
    # prepare items
    sql_query = """SELECT *
              FROM (
                SELECT `item_code`, `stock_uom`,
                  (SELECT IFNULL(`qty_after_transaction`, 0)
                   FROM `tabStock Ledger Entry`
                   WHERE `posting_date` <= "{date}"
                     AND `tabStock Ledger Entry`.`item_code` = `tabItem`.`item_code`
                     AND `warehouse` LIKE "{warehouse}"
                   ORDER BY `posting_date` DESC, `posting_time` DESC, `modified` DESC, `actual_qty` DESC
                   LIMIT 1
                  ) AS `qty`,
                  0 AS `indent` 
                FROM `tabItem`
                WHERE `is_stock_item` = 1 
                  AND `disabled` = 0
                  AND `item_group` LIKE "{group}"
              ) AS `raw`
            WHERE `raw`.`qty` > 0;""".format(date=filters['date'], warehouse=filters['warehouse'], group=filters['item_group'])
    data = frappe.db.sql(sql_query, as_dict=1)

    # compute indent
    output = []
    total = {'value': 0, 'reduced_value': 0}
    date = datetime.strptime(filters['date'], "%Y-%m-%d").date()
    complete = False
    for row in data:
        detail = []
        sql_query = """SELECT IFNULL(`actual_qty`, 0) AS `actual_qty`, 
              `posting_date`, 
              `voucher_no`, 
              IFNULL(`valuation_rate`, 0) AS `valuation_rate`
            FROM `tabStock Ledger Entry` 
            WHERE `item_code` = "{item}"
              AND `actual_qty` > 0
              AND `warehouse` LIKE "{warehouse}"
            ORDER BY `posting_date` DESC, `posting_time` DESC, `modified` DESC, `actual_qty` DESC;""".format(
                item=row['item_code'], warehouse=filters['warehouse'])
        transactions = frappe.db.sql(sql_query, as_dict=True)
        allocated = {'qty': 0, 'value': 0, 'reduced_value': 0}
        for t in transactions:
            detail.append({
                'item_code': row['item_code'],
                'stock_uom': row['stock_uom'],
                'indent': 1,
                'date': t['posting_date'],
                'voucher_no': t['voucher_no'],
                'valuation_rate': t['valuation_rate'],
                'age': ((date - t['posting_date']).days / 365.25)
            })
            if (allocated['qty'] + t['actual_qty']) >= row['qty']:
                detail[-1]['qty'] = row['qty'] - allocated['qty']
                complete = True
            else:
                detail[-1]['qty'] = t['actual_qty']
            allocated['qty'] += detail[-1]['qty']
            detail[-1]['value'] = detail[-1]['qty'] * t['valuation_rate']
            allocated['value'] += detail[-1]['value']
            if detail[-1]['age'] > 4:
                detail[-1]['reduced_value'] = 0
            elif detail[-1]['age'] > 3:
                detail[-1]['reduced_value'] = 0.3 * detail[-1]['value']
            elif detail[-1]['age'] > 1:
                detail[-1]['reduced_value'] = 0.65 * detail[-1]['value']
            else:
                detail[-1]['reduced_value'] = detail[-1]['value']
            allocated['reduced_value'] += detail[-1]['reduced_value']
            # add to output
            if complete:
                complete = False
                break
        row['value'] = allocated['value']
        row['reduced_value'] = allocated['reduced_value']
        # add this item to output row with child rows
        output.append(row)
        [output.append(d) for d in detail]
        # updated totals
        total['value'] += allocated['value']
        total['reduced_value'] += allocated['reduced_value']
    # add total row
    output.append({
        'item_code': "<b>Total</b>",
        'value': total['value'],
        'reduced_value': total['reduced_value']
    })
    return output
