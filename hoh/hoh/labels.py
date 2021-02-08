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
                       (SELECT GROUP_CONCAT(CONCAT("<img src='",
                        (SELECT `value` FROM `tabSingles` WHERE `doctype` = "HOH Settings" AND `field` = "label_image_host"), 
                         `tabPflegesymbol`.`image`, "' style='width: 20px;' >")
                         ORDER BY `tabPflegesymbol`.`sort` DESC)
                        FROM `tabItem Pflegesymbol` 
                        LEFT JOIN `tabPflegesymbol` ON `tabPflegesymbol`.`name` = `tabItem Pflegesymbol`.`pflegesymbol`
                        WHERE `tabBemusterung`.`name` = `tabItem Pflegesymbol`.`parent` AND `tabItem Pflegesymbol`.`parenttype` = "Bemusterung"
                       ) AS `pflegesymbole`,
                       (SELECT GROUP_CONCAT(CONCAT(ROUND(`tabItem Komposition`.`anteil`, 0), "% ", `tabItem Komposition`.`material`))
                        FROM `tabItem Komposition`
                        WHERE `tabBemusterung`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Bemusterung"
                       ) AS `material`,
                       (SELECT GROUP_CONCAT(`item_name`)
                        FROM `tabBemusterung Artikel`
                        WHERE `tabBemusterung`.`name` = `tabBemusterung Artikel`.`parent` AND `tabBemusterung Artikel`.`item_group` = "Stoffe"
                       ) AS `stoffe`,
                       (SELECT GROUP_CONCAT(`item_name`)
                        FROM `tabBemusterung Artikel`
                        WHERE `tabBemusterung`.`name` = `tabBemusterung Artikel`.`parent` AND `tabBemusterung Artikel`.`item_group` = "Pailletten"
                       ) AS `pailletten`,
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

def get_delivery_note_label_data(selected_delivery_notes):
    sql_query = """SELECT
                       `tabDelivery Note`.`customer_name` AS `customer_name`,
                       `tabAddress`.`address_line1` AS `address_line1`,
                       `tabAddress`.`address_line2` AS `address_line2`,
                       `tabAddress`.`address_line3` AS `address_line3`,
                       `tabAddress`.`zusatzbezeichnung` AS `zusatzbezeichnung`,
                       `tabAddress`.`pincode` AS `pincode`,
                       `tabAddress`.`city` AS `city`,
                       `tabAddress`.`country` AS `country`,
                       `tabDelivery Note`.`name` AS `delivery_note`,
                       `tabDelivery Note`.`po_no` AS `po_no`
                    FROM `tabDelivery Note`
                    LEFT JOIN `tabAddress` ON `tabAddress`.`name` = `tabDelivery Note`.`shipping_address_name`
                    WHERE `tabDelivery Note`.`name` IN ({selected_delivery_notes});""".format(selected_delivery_notes=selected_delivery_notes)

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

@frappe.whitelist()
def get_delivery_note_label(selected_delivery_notes):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.work_order_label_printer:
        frappe.throw( _("Please define a work order label printer under HOH Settings.") )
    label_printer = settings.work_order_label_printer
    # get raw data
    data = { 
        'delivery_notes': get_delivery_note_label_data(selected_delivery_notes),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('hoh/templates/labels/delivery_note_label.html', data)
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"

@frappe.whitelist()
def get_sales_order_label(sales_order):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.work_order_label_printer:
        frappe.throw( _("Please define a work order label printer under HOH Settings.") )
    label_printer = settings.work_order_label_printer
    # get raw data
    so = frappe.get_doc("Sales Order", sales_order)
    # prepare content
    content = frappe.render_template('hoh/templates/labels/sales_order_label.html', so.as_dict())
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
