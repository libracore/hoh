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
    # get net revenue
    sum_net_base_total = frappe.db.sql("""SELECT 
        SUM(`tabSales Invoice`.`base_net_total`) AS `base_net_total`
    FROM `tabSales Invoice` 
    LEFT JOIN `tabSales Team` ON `tabSales Invoice`.`name` = `tabSales Team`.`parent`
    WHERE `tabSales Team`.`sales_person` = '{sales_person}' AND `tabSales Invoice`.`docstatus` = '1'
      AND `tabSales Invoice`.`posting_date` BETWEEN '{from_date}' AND '{to_date}'
    """.format(sales_person=filters.sales_person, from_date=from_date, to_date=to_date), as_dict=True)
    net_revenue = sum_net_base_total[0]['base_net_total'] or 0
    data.append({
        'platzhalter': _("Nettoumsatz Total"),
        'net_amount': net_revenue
    })

    # get transport deduction
    deduction = frappe.db.sql("""SELECT SUM(`debit`) AS `debit` 
      FROM `tabGL Entry` 
      WHERE `account` = '7300 - Transporte durch Dritte - HOH' 
        AND `tabGL Entry`.`posting_date` BETWEEN '{from_date}' AND '{to_date}'
    """.format(from_date=from_date, to_date=to_date), as_dict=True)
    deductions = (-1) * (deduction[0]['debit'] or 0)
    data.append({
        'platzhalter': _("Transportkosten Total"),
        'net_amount': deductions
    })

    # get transport deduction
    deduction2 = frappe.db.sql("""SELECT SUM(`debit`) AS `debit` 
      FROM `tabGL Entry` 
      WHERE `account` LIKE '7790%' 
        AND `tabGL Entry`.`posting_date` BETWEEN '{from_date}' AND '{to_date}'
    """.format(from_date=from_date, to_date=to_date), as_dict=True)
    deductions2 = (-1) * (deduction2[0]['debit'] or 0)
    data.append({
        'platzhalter': _("Bankgebühren"),
        'net_amount': deductions2
    })
    
    # intermediate sum
    intermediate = net_revenue + deductions + deductions2
    data.append({
        'platzhalter': _("Zwischensumme"),
        'net_amount': intermediate
    })

    # commission
    commission = 0.03 * intermediate
    data.append({
        'platzhalter': _("Kommission"),
        'net_amount': commission
    })
    
    return data
