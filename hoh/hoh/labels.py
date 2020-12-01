# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime
from erpnextswiss.erpnextswiss.doctype.label_printer.label_printer import create_pdf

def get_label_data(selected_items):
    sql_query = """SELECT
                       `tabBemusterung`.`item` AS `item`,
                       `tabBemusterung`.`name` AS `name`,
                       `tabBemusterung`.`stoffbreite_von` AS `stoffbreite_von`,
                       `tabBemusterung`.`stoffbreite_bis` AS `stoffbreite_bis`,
                       `tabBemusterung`.`fertigbreite_von` AS `fertigbreite_von`,
                       `tabBemusterung`.`fertigbreite_bis` AS `fertigbreite_bis`,
                       `tabBemusterung`.`minimalmenge` AS `minimalmenge`,
                       `tabBemusterung`.`preisgruppe` AS `preisgruppe`,
                       `tabBemusterung`.`rate` AS `preis`,
                       (SELECT GROUP_CONCAT(CONCAT("<img src='", `tabPflegesymbol`.`image`, "'>"))
                        FROM `tabItem Pflegesymbol` 
                        LEFT JOIN `tabPflegesymbol` ON `tabPflegesymbol`.`name` = `tabItem Pflegesymbol`.`pflegesymbol`
                        WHERE `tabBemusterung`.`name` = `tabItem Pflegesymbol`.`parent` AND `tabItem Pflegesymbol`.`parenttype` = "Bemusterung") AS `pflegesymbole`,
                       (SELECT GROUP_CONCAT(CONCAT(ROUND(`tabItem Komposition`.`anteil`, 0), "% ", `tabItem Komposition`.`material`))
                        FROM `tabItem Komposition`
                        WHERE `tabBemusterung`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Bemusterung") AS `material`,
                       IFNULL(`tabItem Price`.`price_list_rate`, 0) AS `standard_selling_rate`
                    FROM `tabBemusterung`
                    LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabBemusterung`.`name`
                    LEFT JOIN `tabItem Price` ON (`tabItem Price`.`item_code` = `tabBemusterung`.`name` AND `tabItem Price`.`selling` = 1)
                   WHERE `tabBemusterung`.`name` IN ({selected_items});""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)

def get_item_label_data(selected_items):
    sql_query = """SELECT
                       `tabItem`.`item_code` AS `item_code`,
                       `tabItem`.`item_name` AS `item_name`,
                       `tabItem`.`item_group` AS `item_group`,
                       `tabItem`.`stock_uom` AS `stock_uom`
                    FROM `tabItem`
                    WHERE `tabItem`.`name` IN ({selected_items});""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)

def get_work_order_label_data(selected_items):
    sql_query = """SELECT
                       `tabItem`.`item_code` AS `item_code`,
                       `tabItem`.`item_name` AS `item_name`,
                       `tabWork Order`.`stoff` AS `stoff`,
                       `tabWork Order`.`pailletten` AS `pailletten`,
                       (SELECT CONCAT(ROUND(`tabSales Order Item`.`anzahl`, 0), " x ", ROUND(`tabSales Order Item`.`verkaufseinheit`, 1), " ", `tabSales Order Item`.`uom`) 
                        FROM `tabSales Order Item`
                        WHERE `tabSales Order Item`.`item_code` = `tabItem`.`item_code`
                          AND `tabSales Order Item`.`parent` = `tabWork Order`.`sales_order`) AS `qty`,
                        `tabItem`.`fertigbreite_von` AS `fertigbreite_von`,
                        `tabItem`.`fertigbreite_bis` AS `fertigbreite_bis`
                    FROM `tabWork Order`
                    LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabWork Order`.`production_item`
                    WHERE `tabWork Order`.`name` IN ({selected_items});""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)
    
@frappe.whitelist()
def get_label(selected_items):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.label_printer_prices:
        frappe.throw( _("Please define a label printer for price labels under HOH Settings.") )
    label_printer = settings.label_printer_prices
    # get raw data
    data = { 
        'items': get_label_data(selected_items),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('hoh/templates/labels/price_label.html', data)
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
   
@frappe.whitelist()
def get_item_label(selected_items):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.item_label_printer:
        frappe.throw( _("Please define an item label printer under HOH Settings.") )
    label_printer = settings.item_label_printer
    # get raw data
    data = { 
        'items': get_item_label_data(selected_items),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('hoh/templates/labels/item_label.html', data)
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"

@frappe.whitelist()
def get_work_order_label(selected_items):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.work_order_label_printer:
        frappe.throw( _("Please define a work order label printer under HOH Settings.") )
    label_printer = settings.work_order_label_printer
    # get raw data
    data = { 
        'items': get_work_order_label_data(selected_items),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('hoh/templates/labels/work_order_label.html', data)
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
