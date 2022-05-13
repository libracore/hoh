# Copyright (c) 2019-2020, libracore and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import csv
from erpnextswiss.erpnextswiss.page.bank_wizard.bank_wizard import make_payment_entry, get_receivable_account, get_payable_account, get_default_customer, get_default_supplier
import datetime

def import_payments(file, account, cost_center):
    # this function will import payments from an export-CSV file
    # defaults
    receivable_account = get_receivable_account()['account']
    payable_account = get_payable_account()['account']
    default_supplier = get_default_supplier()['supplier']
    default_customer = get_default_customer()['customer']
    # read csv file
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            # determine content
            print("{0}".format(row))
            amount = float(row['GW-Soll'] or row['GW-Haben'])
            date = datetime.datetime.strptime(row['Beleg-Dat'], '%d.%m.%Y')
            if amount < 0:
                payment_type = "Pay"
            else:
                payment_type = "Receive"
            payment = {
                'date': date,
                'reference_date': date,
                'amount': abs(amount),
                'reference_no': row['Beleg-Nr'],
                'remarks': row['Text']
            }
            if len(row['GKto-Nr']) == 6:
                # debtor or creditor
                if row['GKto-Nr'].startswith('30'):
                    # creditor
                    payment['paid_from'] = account
                    payment['paid_to'] = payable_account
                    payment['type'] = "Pay"
                    payment['party_type'] = "Supplier"
                    payment['party'] = "S-{0}".format(row['GKto-Nr'])
                    submit = False
                else:
                    # debtor
                    payment['paid_from'] = receivable_account
                    payment['paid_to'] = account
                    payment['type'] = "Receive"
                    payment['party_type'] = "Customer"
                    payment['party'] = "C-{0}".format(row['GKto-Nr'])
                    submit = False
            elif len(row['GKto-Nr']) == 4:
                # direct payment of expense
                payment['paid_from'] = account
                payment['paid_to'] = payable_account
                payment['type'] = "Pay"
                payment['party_type'] = "Supplier"
                payment['party'] = default_supplier
                payment['deductions'] = [{
                    'account': get_account(row['GKto-Nr']),
                    'cost_center': cost_center,
                    'amount': abs(amount)
                }]
                submit = True
            else:
                # no against account: book against income 4022
                payment['paid_from'] = receivable_account
                payment['paid_to'] = account
                payment['type'] = "Receive"
                payment['party_type'] = "Customer"
                payment['party'] = default_customer
                payment['deductions'] = [{
                    'account': get_account("4022"),
                    'cost_center': cost_center,
                    'amount': (-1) * abs(amount)
                }]
                submit = True
            # create payment entry
            print("Creating {0}...".format(payment))
            new_pe = make_payment_entry(amount=payment['amount'], 
                date=payment['date'], 
                reference_no=payment['reference_no'], 
                paid_from=payment['paid_from'], 
                paid_to=payment['paid_to'], 
                type=payment['type'], 
                party=payment['party'], 
                party_type=payment['party_type'], 
                references=None, 
                remarks=payment['remarks'], 
                auto_submit=False, 
                exchange_rate=1,
                company=None)
            payment_entry = frappe.get_doc("Payment Entry", new_pe)
            if 'deductions' in payment:
                row = payment_entry.append('deductions', payment['deductions'][0])
            if submit:
                payment_entry.submit()
            frappe.db.commit()
    print("Done")
    return

def get_account(account_number):
    account = frappe.get_all("Account", filters={'account_number': account_number}, fields=['name'])
    return account[0]['name']

# this function will update machines from dessin
def update_machines():
    # loog through bemusterung
    bemusterungen = frappe.get_all("Bemusterung", fields=['name'])
    for b in bemusterungen:
        print("Updating Bemusterung {0} ...".format(b['name']))
        b_doc = frappe.get_doc("Bemusterung", b['name'])
        b_doc.stickmaschine = []
        d_doc = frappe.get_doc("Dessin", b_doc.dessin)
        for s in d_doc.stickmaschine:
            row = b_doc.append('stickmaschine', { 'stickmaschine': s.stickmaschine })
        b_doc.save()
    frappe.db.commit()
    # loog through items
    items = frappe.get_all("Item", fields=['name'])
    for i in items:
        print("Updating Item {0} ...".format(i['name']))
        i_doc = frappe.get_doc("Item", i['name'])
        if i_doc.dessin:
            i_doc.stickmaschine = []
            d_doc = frappe.get_doc("Dessin", i_doc.dessin)
            for s in d_doc.stickmaschine:
                row = i_doc.append('stickmaschine', { 'stickmaschine': s.stickmaschine })
            i_doc.save()
    frappe.db.commit()
    print("done")
    return

# this function will remove breaks from machine times
def remove_breaks():
    wos = frappe.get_all("Work Order", filters={'docstatus': 1}, fields=['name'])
    count = 0
    for wo in wos:
        count += 1
        print("Processing {0}... {1}%".format(wo['name'], count * 100 / len(wos)))
        work_order = frappe.get_doc("Work Order", wo['name'])
        total_hours = 0
        if work_order.nutzungen:
            for n in work_order.nutzungen:
                if n.activity_type != "Pause" and n.maschinenstunden > 0:
                    total_hours += n.maschinenstunden
        work_order.summe_maschinenstunden = total_hours
        try:
            work_order.save()
        except Exception as err:
            print("Error: {0}".format(err))
    frappe.db.commit()
    print("done")
