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
        {"label": _(""), "fieldname": "platzhalter", "fieldtype": "Data", "width": 150},
        {"label": _("Net Amount"), "fieldname": "net_amount", "fieldtype": "Currency", "width": 120}
    ]

def get_data(filters):
    data = []
    from_date = getdate(filters.from_date)
    to_date = getdate(filters.to_date)
    sinvs = frappe.db.sql("""SELECT 
    `tabSales Invoice`.`name` AS `name`, 
    `tabSales Invoice`.`base_net_total` AS `base_net_total`, 
    `tabSales Invoice`.`posting_date` AS `posting_date`,
    `tabSales Team`.`sales_person` AS `sales_person`
    FROM 
    `tabSales Invoice` 
    LEFT JOIN
    `tabSales Team` ON `tabSales Invoice`.`name` = `tabSales Team`.`parent`
    WHERE 
    `tabSales Team`.`sales_person` = '{sales_person}' AND `tabSales Invoice`.`posting_date` BETWEEN '{from_date}' AND '{to_date}'""".format(sales_person=filters.sales_person, from_date=from_date, to_date=to_date), as_dict=True)
    sum_base_net_total = 0
    sum_deduction = 0
    for sinv in sinvs:
        sum_base_net_total += sinv.base_net_total
        deduction = frappe.db.sql("""SELECT SUM(`debit`) AS `debit` FROM `tabGL Entry` WHERE `account` = '7300 - Transporte durch Dritte - HOH' AND `tabGL Entry`.`posting_date` BETWEEN '{from_date}' AND '{to_date}'""".format(sinv=sinv.name, from_date=from_date, to_date=to_date), as_dict=True)
        if len(deduction) > 0:
            if deduction[0].debit:
                sum_deduction += float(deduction[0].debit)

    _data = []
    _data.append("Nettoumsatz Total")
    _data.append(sum_base_net_total)
    _data.append("")
    data.append(_data)
    _data = []
    _data.append("Transportkosten Total")
    _data.append(sum_deduction)
    _data.append("")
    data.append(_data)
    _data = []
    _data.append("Zwischensumme")
    zwischensumme = sum_base_net_total - sum_deduction
    _data.append(zwischensumme)
    _data.append("")
    data.append(_data)
    _data = []
    _data.append("Kommission")
    kommission = zwischensumme * 0.03
    _data.append(kommission)
    _data.append("")
    data.append(_data)
    
    return data
