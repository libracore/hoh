# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import ast          # to parse str to dict (from JS calls)
from datetime import datetime

def execute(filters=None):
    if type(filters) is str:
        filters = ast.literal_eval(filters)
    else:
        filters = dict(filters)
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 100},
        {"label": _("OP Debitoren"), "fieldname": "receivables", "fieldtype": "Currency", "width": 100},
        {"label": _("OP Kreditoren"), "fieldname": "payables", "fieldtype": "Currency", "width": 100},
        {"label": _("Liquidität"), "fieldname": "liquidity", "fieldtype": "Currency", "width": 100},
        {"label": _("New Orders"), "fieldname": "new_orders", "fieldtype": "Int", "width": 100},
        {"label": _("New Order Volume"), "fieldname": "new_order_volume", "fieldtype": "Currency", "width": 100},
        {"label": _("New Orders Africa"), "fieldname": "new_orders_africa", "fieldtype": "Int", "width": 100},
        {"label": _("New Order Africa Volume"), "fieldname": "new_order_africa_volume", "fieldtype": "Currency", "width": 100},
        {"label": _("New Orders Europe"), "fieldname": "new_orders_europe", "fieldtype": "Int", "width": 100},
        {"label": _("New Order Europe Volume"), "fieldname": "new_order_europe_volume", "fieldtype": "Currency", "width": 100},
        {"label": _("New Invoices"), "fieldname": "new_invoices", "fieldtype": "Int", "width": 100},
        {"label": _("New Invoice Volume"), "fieldname": "new_invoice_volume", "fieldtype": "Currency", "width": 100},
        {"label": _("Entwicklungskosten"), "fieldname": "development_costs", "fieldtype": "Currency", "width": 100},
        {"label": _("Work Orders"), "fieldname": "work_orders", "fieldtype": "Int", "width": 100},
        {"label": _("Ktm"), "fieldname": "ktm", "fieldtype": "Float", "Precision": 1, "width": 100},
        {"label": _("Ktm per h"), "fieldname": "ktm_per_h", "fieldtype": "Float", "Precision": 1, "width": 100},
        {"label": _("Payment Days"), "fieldname": "payment_speed", "fieldtype": "Float", "Precision": 1, "width": 100},
        {"label": _(""), "fieldname": "blank", "fieldtype": "Data", "width": 10}
    ]
    return columns

@frappe.whitelist()
def get_data(filters):
    data = []
    months = [_("January"), _("February"), _("March"),
        _("April"), _("May"), _("June"),
        _("July"), _("August"), _("September"),
        _("October"), _("November"), _("December")]
    for month in range(1, 13):
        receivables = frappe.db.sql("""
            SELECT IFNULL(SUM(`debit` - `credit`), 0) AS `receivables`
            FROM `tabGL Entry` 
            WHERE `account` IN (SELECT `name` FROM `tabAccount` WHERE `account_type` = "Receivable")
              AND `posting_date` <= LAST_DAY("{year}-{month:02d}-01")
        ;""".format(year=filters['year'], month=month), as_dict=True)
        payables = frappe.db.sql("""
            SELECT IFNULL(SUM(`debit` - `credit`), 0) AS `payables`
            FROM `tabGL Entry` 
            WHERE `account` IN (SELECT `name` FROM `tabAccount` WHERE `account_type` = "Payable")
              AND `posting_date` <= LAST_DAY("{year}-{month:02d}-01")
        ;""".format(year=filters['year'], month=month), as_dict=True)
        liquidity = frappe.db.sql("""
            SELECT IFNULL(SUM(`debit` - `credit`), 0) AS `liquidity`
            FROM `tabGL Entry` 
            WHERE `account` IN (SELECT `account` FROM `tabKennzahlen Account` WHERE `parentfield` = "liquidity_accounts")
              AND `posting_date` <= LAST_DAY("{year}-{month:02d}-01")
        ;""".format(year=filters['year'], month=month), as_dict=True)
        new_orders = frappe.db.sql("""
            SELECT IFNULL(COUNT(`name`), 0) AS `orders`,
                IFNULL(SUM(`base_net_total`), 0) As `volume`
            FROM `tabSales Order` 
            WHERE `docstatus` = 1
              AND `transaction_date` LIKE "{year}-{month:02d}-%"
        ;""".format(year=filters['year'], month=month), as_dict=True)
        new_orders_africa = frappe.db.sql("""
            SELECT IFNULL(COUNT(`name`), 0) AS `orders`,
                IFNULL(SUM(`base_net_total`), 0) As `volume`
            FROM `tabSales Order` 
            WHERE `docstatus` = 1
              AND `transaction_date` LIKE "{year}-{month:02d}-%"
              AND `territory` IN (SELECT `name` FROM `tabTerritory` WHERE `parent` LIKE "%Afrika%" OR `name` LIKE "%Afrika%")
        ;""".format(year=filters['year'], month=month), as_dict=True)
        new_orders_europe = frappe.db.sql("""
            SELECT IFNULL(COUNT(`name`), 0) AS `orders`,
                IFNULL(SUM(`base_net_total`), 0) As `volume`
            FROM `tabSales Order` 
            WHERE `docstatus` = 1
              AND `transaction_date` LIKE "{year}-{month:02d}-%"
              AND `territory` IN (SELECT `name` FROM `tabTerritory` WHERE `parent` LIKE "%Europa%" OR `name` LIKE "%Europa%")
        ;""".format(year=filters['year'], month=month), as_dict=True)
        new_invoices = frappe.db.sql("""
            SELECT IFNULL(COUNT(`name`), 0) AS `orders`,
                IFNULL(SUM(`base_net_total`), 0) As `volume`
            FROM `tabSales Invoice` 
            WHERE `docstatus` = 1
              AND `posting_date` LIKE "{year}-{month:02d}-%"
        ;""".format(year=filters['year'], month=month), as_dict=True)
        development_costs = frappe.db.sql("""
            SELECT IFNULL(SUM(`entwicklungskosten`), 0) AS `development_costs`
            FROM `tabDessin` 
            WHERE `creation` LIKE "{year}-{month:02d}-%"
        ;""".format(year=filters['year'], month=month), as_dict=True)
        new_work_orders = frappe.db.sql("""
            SELECT IFNULL(COUNT(`name`), 0) AS `work_orders`
            FROM `tabWork Order` 
            WHERE `docstatus` < 2
              AND `planned_start_date` LIKE "{year}-{month:02d}-%"
        ;""".format(year=filters['year'], month=month), as_dict=True)
        ktm = frappe.db.sql("""
            SELECT 
                SUM(IFNULL(((`tabWork Order`.`qty` / `tabStickmaschine`.`m_per_cp`) * `tabDessin`.`gesamtmeter`), 0)) AS `ktm`
            FROM `tabWork Order` 
            LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabWork Order`.`production_item`
            LEFT JOIN `tabDessin` ON `tabDessin`.`name` = `tabItem`.`dessin`
            LEFT JOIN `tabStickmaschine` ON `tabStickmaschine`.`name` = `tabWork Order`.`stickmaschine`
            WHERE `tabWork Order`.`docstatus` < 2
              AND `planned_start_date` LIKE "{year}-{month:02d}-%"
        ;""".format(year=filters['year'], month=month), as_dict=True)
        ktm_per_h = frappe.db.sql("""
            SELECT 
                SUM((IFNULL(((`tabWork Order`.`qty` / `tabStickmaschine`.`m_per_cp`) * `tabDessin`.`gesamtmeter`), 0) /
                IFNULL(`tabWork Order`.`summe_maschinenstunden`, 0))) AS `ktm_per_h`
            FROM `tabWork Order` 
            LEFT JOIN `tabItem` ON `tabItem`.`item_code` = `tabWork Order`.`production_item`
            LEFT JOIN `tabDessin` ON `tabDessin`.`name` = `tabItem`.`dessin`
            LEFT JOIN `tabStickmaschine` ON `tabStickmaschine`.`name` = `tabWork Order`.`stickmaschine`
            WHERE `tabWork Order`.`docstatus` < 2
              AND `planned_start_date` LIKE "{year}-{month:02d}-%"
        ;""".format(year=filters['year'], month=month), as_dict=True)
        payment_speed = frappe.db.sql("""
            SELECT 
                  AVG(DATEDIFF(`tabPayment Entry`.`posting_date`, `tabSales Invoice`.`posting_date`)) AS `payment_speed`
                FROM `tabPayment Entry Reference`
                LEFT JOIN `tabPayment Entry` ON `tabPayment Entry`.`name` = `tabPayment Entry Reference`.`parent`
                LEFT JOIN `tabSales Invoice` ON `tabSales Invoice`.`name` = `tabPayment Entry Reference`.`reference_name`
                LEFT JOIN `tabCustomer` ON `tabCustomer`.`name` = `tabSales Invoice`.`customer`
                WHERE `tabPayment Entry Reference`.`reference_doctype` = 'Sales Invoice'
                  AND `tabSales Invoice`.`docstatus` = 1
                  AND `tabPayment Entry`.`docstatus` = 1
                  AND `tabSales Invoice`.`posting_date` LIKE "{year}-{month:02d}-%"
        ;""".format(year=filters['year'], month=month), as_dict=True)
         
        data.append({
            'month': "{0} {1}".format(months[(month - 1)], filters['year']),
            'receivables': receivables[0]['receivables'],
            'payables': payables[0]['payables'],
            'liquidity': liquidity[0]['liquidity'],
            'new_orders': new_orders[0]['orders'],
            'new_order_volume': new_orders[0]['volume'],
            'new_orders_africa': new_orders_africa[0]['orders'],
            'new_order_africa_volume': new_orders_africa[0]['volume'],
            'new_orders_europe': new_orders_europe[0]['orders'],
            'new_order_europe_volume': new_orders_europe[0]['volume'],
            'new_invoices': new_invoices[0]['orders'],
            'new_invoice_volume': new_invoices[0]['volume'],
            'development_costs': development_costs[0]['development_costs'],
            'work_orders': new_work_orders[0]['work_orders'],
            'ktm': ktm[0]['ktm'],
            'ktm_per_h': ktm_per_h[0]['ktm_per_h'],
            'payment_speed' : payment_speed[0]['payment_speed']
        })
    
    return data
