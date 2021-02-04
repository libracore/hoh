# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("User"), "fieldname": "user", "fieldtype": "Data", "width": 150},
        {"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 150},
        {"label": _("Net Amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 120},
        {"label": _(""), "fieldname": "platzhalter", "fieldtype": "Data", "width": 50}
    ]

def get_data(filters):
    data = []
    from_date = getdate(filters.from_date)
    to_date = getdate(filters.to_date)
    sinvs = frappe.db.sql("""SELECT `name`, `base_net_total`, `posting_date`, `owner` FROM `tabSales Invoice` WHERE `owner` = '{user}' AND `posting_date` BETWEEN '{from_date}' AND '{to_date}'""".format(user=filters.owner, from_date=from_date, to_date=to_date), as_dict=True)
    sum_base_net_total = 0
    sum_deduction = 0
    for sinv in sinvs:
        _data = []
        _data.append(filters.owner)
        _data.append(sinv.name)
        _data.append(sinv.base_net_total)
        sum_base_net_total += sinv.base_net_total
        deduction = frappe.db.sql("""SELECT SUM(`debit`) AS `debit` FROM `tabGL Entry` WHERE `voucher_no` = '{sinv}' AND `account` = '7300 - Transporte durch Dritte - HOH'""".format(sinv=sinv.name), as_dict=True)
        if len(deduction) > 0:
            if deduction[0].debit:
                sum_deduction += float(deduction[0].debit)
        _data.append("")
        data.append(_data)
        
    _data = []
    _data.append("Nettoumsatz Total")
    _data.append("")
    _data.append(sum_base_net_total)
    _data.append("")
    data.append(_data)
    _data = []
    _data.append("Transportkosten Total")
    _data.append("")
    _data.append(sum_deduction)
    _data.append("")
    data.append(_data)
    _data = []
    _data.append("Zwischensumme")
    _data.append("")
    zwischensumme = sum_base_net_total - sum_deduction
    _data.append(zwischensumme)
    _data.append("")
    data.append(_data)
    _data = []
    _data.append("Kommission")
    _data.append("")
    kommission = zwischensumme * 0.03
    _data.append(kommission)
    _data.append("")
    data.append(_data)
    
    return data
