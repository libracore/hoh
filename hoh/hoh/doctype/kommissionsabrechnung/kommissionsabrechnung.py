# -*- coding: utf-8 -*-
# Copyright (c) 2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime

class Kommissionsabrechnung(Document):
    def get_payments(self):
        sql_query = """SELECT 
             `sinv`.`name`,
             `sinv`.`customer`,
             `sinv`.`customer_name`,
             `sinv`.`base_net_total`,
             `sinv`.`total_taxes_and_charges`,
             `sinv`.`base_grand_total`,
             `sinv`.`base_freight`,
             `sinv`.`total_taxes_and_charges` AS `taxes`,
             (1 - ((`sinv`.`total_taxes_and_charges` + `sinv`.`base_freight`) / `sinv`.`base_grand_total`)) AS `commission_fraction`,
             `commission_rate`,
             `tabPayment Entry Reference`.`allocated_amount`,
             `tabPayment Entry`.`name`,
             `tabPayment Entry`.`posting_date`
            FROM
            (SELECT 
             `name`,
             `customer`,
             `customer_name`,
             `base_net_total`,
             `total_taxes_and_charges`,
             `base_grand_total`,
             (SELECT IFNULL(SUM(`base_amount`), 0)
              FROM `tabSales Invoice Item` 
              WHERE `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name`
                AND `tabSales Invoice Item`.`item_code` = "Fracht") AS `base_freight`,
             (`commission_rate` / 100) AS `commission_rate`
            FROM `tabSales Invoice`
            WHERE `tabSales Invoice`.`sales_partner` = "{sales_partner}"
            ) AS `sinv`
            JOIN `tabPayment Entry Reference` ON `tabPayment Entry Reference`.`reference_name` = `sinv`.`name`
            LEFT JOIN `tabPayment Entry` ON `tabPayment Entry`.`name` = `tabPayment Entry Reference`.`parent`
            WHERE `tabPayment Entry`.`docstatus` = 1
              AND `tabPayment Entry`.`posting_date` >= "{from_date}"
              AND `tabPayment Entry`.`posting_date` <= "{to_date}"
            ORDER BY `tabPayment Entry`.`posting_date`; 
        """.format(sales_partner=self.sales_partner, from_date=self.from_date, to_date=self.to_date)
        payments = frappe.db.sql(sql_query, as_dict=True)
        for p in payments:
            self.append('payments', {
                'date': p['posting_date'],
                'sales_invoice': p['name'],
                'customer': p['customer'],
                'customer_name': p['customer_name'],
                'paid_amount': p['allocated_amount'],
                'commission': (p['allocated_amount'] * p['commission_fraction'] * p['commission_rate']),
                'grand_total': p['base_grand_total'],
                'freight_charges': p['base_freight'],
                'taxes': p['taxes'],
                'allocated_amount': p['allocated_amount'] * p['commission_fraction'],
                'commission_fraction': p['commission_fraction'],
                'commission_rate': p['commission_rate']
            })
        return
    
    def get_receivables(self):
        sql_query = """SELECT 
             `name`,
             `posting_date`,
             `customer`,
             `customer_name`,
             `base_net_total`,
             `total_taxes_and_charges`,
             `base_grand_total`,
             (SELECT IFNULL(SUM(`base_amount`), 0)
              FROM `tabSales Invoice Item` 
              WHERE `tabSales Invoice Item`.`parent` = `tabSales Invoice`.`name`
                AND `tabSales Invoice Item`.`item_code` = "Fracht") AS `base_freight`,
             (`commission_rate` / 100) AS `commission_rate`,
             `outstanding_amount`
            FROM `tabSales Invoice`
            WHERE `tabSales Invoice`.`sales_partner` = "{sales_partner}"
              AND `tabSales Invoice`.`docstatus` = 1
              AND `tabSales Invoice`.`outstanding_amount` != 0
            ORDER BY `tabSales Invoice`.`posting_date`; 
        """.format(sales_partner=self.sales_partner)
        receivables = frappe.db.sql(sql_query, as_dict=True)
        for r in receivables:
            self.append('receivables', {
                'date': r['posting_date'],
                'sales_invoice': r['name'],
                'customer': r['customer'],
                'customer_name': r['customer_name'],
                'grand_total': r['base_grand_total'],
                'outstanding_amount': r['outstanding_amount']
            })
        return
        
    def before_save(self):
        # update totals
        total_commission = 0
        total_payments = 0
        for p in self.payments:
            total_commission += p.commission
            total_payments += p.allocated_amount
        total_outstanding = 0
        self.total_commission = total_commission
        self.total_payments = total_payments
        for r in self.receivables:
            total_outstanding += r.outstanding_amount
        self.total_outstanding = total_outstanding
        return
        
    def on_submit(self):
        # create purchase invoice
        config = frappe.get_doc("HOH Settings", "HOH Settigns")
        supplier = frappe.get_doc("Supplier", self.supplier)
        new_pinv = frappe.get_doc({
            "doctype": "Purchase Invoice",
            "supplier": self.supplier,
            "bill_no": self.name,
            "bill_date": datetime.now(),
            "taxes_and_charges": supplier.default_purchase_tax_template
        })
        new_pinv.append("items", {
            'item_code': config.commission_item,
            'qty': 1,
            'rate': self.total_commission
        })
        new_pinv.insert()
        self.purchase_invoice = new_pinv.name
        self.save()
        return
    
@frappe.whitelist()
def create(sales_partner, from_date, to_date, quarter):
    new_commission = frappe.get_doc({
        "doctype": "Kommissionsabrechnung",
        "sales_partner": sales_partner,
        "from_date": from_date,
        "to_date": to_date,
        "title": "{0} {1}".format(sales_partner, quarter)
    })
    
    new_commission.insert()
    new_commission.get_payments()
    new_commission.get_receivables()
    new_commission.save()
    return new_commission.name
