# Copyright (c) 2020-2021, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime
from erpnextswiss.erpnextswiss.doctype.label_printer.label_printer import create_pdf
from urllib.parse import quote

def get_price_label_data(bemusterung):
    sql_query = """SELECT
                       `tabBemusterung`.`item` AS `item`,
                       `tabBemusterung`.`name` AS `name`,
                       `tabItem`.`item_group` AS `item_group`,
                       `tabBemusterung`.`stoffbreite_von` AS `stoffbreite_von`,
                       `tabBemusterung`.`stoffbreite_bis` AS `stoffbreite_bis`,
                       `tabBemusterung`.`fertigbreite_von` AS `fertigbreite_von`,
                       `tabBemusterung`.`fertigbreite_bis` AS `fertigbreite_bis`,
                       `tabBemusterung`.`gewicht` AS `gewicht`,
                       `tabBemusterung`.`preisgruppe` AS `preisgruppe`,
                       `tabBemusterung`.`rate` AS `preis`,
                       "muster" AS `source_type`,
                       (SELECT REPLACE(GROUP_CONCAT(CONCAT("<img src='",
                        (SELECT `value` FROM `tabSingles` WHERE `doctype` = "HOH Settings" AND `field` = "label_image_host"), 
                         `tabPflegesymbol`.`image`, "' style='width: 20px;' >")
                         ORDER BY `tabPflegesymbol`.`sort` DESC), ",", "&nbsp;")
                        FROM `tabItem Pflegesymbol` 
                        LEFT JOIN `tabPflegesymbol` ON `tabPflegesymbol`.`name` = `tabItem Pflegesymbol`.`pflegesymbol`
                        WHERE `tabBemusterung`.`name` = `tabItem Pflegesymbol`.`parent` AND `tabItem Pflegesymbol`.`parenttype` = "Bemusterung"
                       ) AS `pflegesymbole`,
                       (SELECT GROUP_CONCAT(CONCAT(ROUND(`tabItem Komposition`.`anteil`, 0), "% ", `tabItem Komposition`.`material`) ORDER BY `idx` ASC)
                        FROM `tabItem Komposition`
                        WHERE `tabBemusterung`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Bemusterung"
                       ) AS `material`,
                       (SELECT GROUP_CONCAT(`item_name`)
                        FROM `tabBemusterung Artikel`
                        WHERE `tabBemusterung`.`name` = `tabBemusterung Artikel`.`parent` AND `tabBemusterung Artikel`.`item_group` IN ("Stoffe", "Eigenware Stoffe")
                       ) AS `stoffe`,
                       (SELECT GROUP_CONCAT(`item_name`)
                        FROM `tabBemusterung Artikel`
                        WHERE `tabBemusterung`.`name` = `tabBemusterung Artikel`.`parent` AND `tabBemusterung Artikel`.`item_group` = "Pailletten"
                       ) AS `pailletten`,
                       IFNULL(`tabItem Price`.`price_list_rate`, 0) AS `standard_selling_rate`
                    FROM `tabBemusterung`
                    LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabBemusterung`.`name`
                    LEFT JOIN `tabItem Price` ON (`tabItem Price`.`item_code` = `tabBemusterung`.`name` AND `tabItem Price`.`selling` = 1)
                   WHERE `tabBemusterung`.`name` = '{bemusterung}'
                   
UNION SELECT
                   `tabItem`.`name` AS `item`,
                   `tabItem`.`item_name` AS `name`,
                   `tabItem`.`item_group` AS `item_group`,
                   `tabItem`.`stoffbreite_von` AS `stoffbreite_von`,
                   `tabItem`.`stoffbreite_bis` AS `stoffbreite_bis`,
                   0 AS `fertigbreite_von`,
                   0 AS `fertigbreite_bis`,
                   `tabItem`.`gewicht` AS `gewicht`,
                   "" AS `preisgruppe`,
                   "" AS `preis`,
                   "stoff" AS `source_type`,
                   (SELECT REPLACE(GROUP_CONCAT(CONCAT("<img src='",
                    (SELECT `value` FROM `tabSingles` WHERE `doctype` = "HOH Settings" AND `field` = "label_image_host"), 
                     `tabPflegesymbol`.`image`, "' style='width: 20px;' >")
                     ORDER BY `tabPflegesymbol`.`sort` DESC), ",", "&nbsp;")
                    FROM `tabItem Pflegesymbol` 
                    LEFT JOIN `tabPflegesymbol` ON `tabPflegesymbol`.`name` = `tabItem Pflegesymbol`.`pflegesymbol`
                    WHERE `tabItem`.`name` = `tabItem Pflegesymbol`.`parent` AND `tabItem Pflegesymbol`.`parenttype` = "Item"
                   ) AS `pflegesymbole`,
                   (SELECT GROUP_CONCAT(CONCAT(ROUND(`tabItem Komposition`.`anteil`, 0), "% ", `tabItem Komposition`.`material`) ORDER BY `idx` ASC)
                    FROM `tabItem Komposition`
                    WHERE `tabItem`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Item"
                   ) AS `material`,
                   "" AS `stoffe`,
                   "" AS `pailletten`,
                   IFNULL(`tabItem Price`.`price_list_rate`, 0) AS `standard_selling_rate`
                FROM `tabItem`
                LEFT JOIN `tabItem Price` ON (`tabItem Price`.`item_code` = `tabItem`.`name` AND `tabItem Price`.`selling` = 1)
               WHERE `tabItem`.`name` = '{bemusterung}' AND `tabItem`.`item_group` IN ("Stoffe", "Eigenware Stoffe", "Applikationen");""".format(bemusterung=bemusterung)
    
    return frappe.db.sql(sql_query, as_dict=True)

def get_bemusterung_label_data(selected_items):
    sql_query = """SELECT
       `tabBemusterung`.`item` AS `item`,
       `tabBemusterung`.`name` AS `name`,
       `tabBemusterung`.`bezeichnung` AS `bezeichnung`,
       `tabBemusterung`.`stoffbreite_von` AS `stoffbreite_von`,
       `tabBemusterung`.`stoffbreite_bis` AS `stoffbreite_bis`,
       `tabBemusterung`.`fertigbreite_von` AS `fertigbreite_von`,
       `tabBemusterung`.`fertigbreite_bis` AS `fertigbreite_bis`,
       `tabBemusterung`.`gewicht` AS `gewicht`,
       `tabBemusterung`.`d_stoffe` AS `d_stoffe`,
       `tabBemusterung`.`d_pailletten` AS `d_pailletten`,
       `tabBemusterung`.`d_applikationen` AS `d_applikationen`,
       `tabBemusterung`.`d_prints` AS `d_prints`,
       `tabBemusterung`.`preisgruppe` AS `preisgruppe`,
       `tabBemusterung`.`rate` AS `preis`,
       "muster" AS `source_type`,
       (SELECT GROUP_CONCAT(CONCAT("<img src='",
        (SELECT `value` FROM `tabSingles` WHERE `doctype` = "HOH Settings" AND `field` = "label_image_host"), 
         `tabPflegesymbol`.`image`, "' style='width: 20px;' >")
         ORDER BY `tabPflegesymbol`.`sort` DESC)
        FROM `tabItem Pflegesymbol` 
        LEFT JOIN `tabPflegesymbol` ON `tabPflegesymbol`.`name` = `tabItem Pflegesymbol`.`pflegesymbol`
        WHERE `tabBemusterung`.`name` = `tabItem Pflegesymbol`.`parent` AND `tabItem Pflegesymbol`.`parenttype` = "Bemusterung"
       ) AS `pflegesymbole`,
       (SELECT GROUP_CONCAT(CONCAT(ROUND(`tabItem Komposition`.`anteil`, 0), "% ", `tabItem Komposition`.`material`) ORDER BY `idx` ASC)
        FROM `tabItem Komposition`
        WHERE `tabBemusterung`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Bemusterung"
       ) AS `material`,
       (SELECT GROUP_CONCAT(`item_name`)
        FROM `tabBemusterung Artikel`
        WHERE `tabBemusterung`.`name` = `tabBemusterung Artikel`.`parent` AND `tabBemusterung Artikel`.`item_group` IN ("Stoffe", "Eigenware Stoffe")
       ) AS `stoffe`,
       (SELECT GROUP_CONCAT(`item_name`)
        FROM `tabBemusterung Artikel`
        WHERE `tabBemusterung`.`name` = `tabBemusterung Artikel`.`parent` AND `tabBemusterung Artikel`.`item_group` = "Pailletten"
       ) AS `pailletten`,
       IFNULL(`tabItem Price`.`price_list_rate`, 0) AS `standard_selling_rate`
    FROM `tabBemusterung`
    LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabBemusterung`.`name`
    LEFT JOIN `tabItem Price` ON (`tabItem Price`.`item_code` = `tabBemusterung`.`name` AND `tabItem Price`.`selling` = 1)
   WHERE `tabBemusterung`.`name` IN ({selected_items})
   
UNION SELECT
		   `tabItem`.`name` AS `item`,
		   `tabItem`.`item_code` AS `name`,
		   `tabItem`.`item_name` AS `bezeichnung`,
		   `tabItem`.`stoffbreite_von` AS `stoffbreite_von`,
		   `tabItem`.`stoffbreite_bis` AS `stoffbreite_bis`,
		   `tabItem`.`fertigbreite_von` AS `fertigbreite_von`,
		   `tabItem`.`fertigbreite_bis` AS `fertigbreite_bis`,
		   `tabItem`.`gewicht` AS `gewicht`,
		   "" AS `d_stoffe`,
		   "" AS `d_pailletten`,
		   "" AS `d_applikationen`,
		   "" AS `d_prints`,
		   "" AS `preisgruppe`,
		   "" AS `preis`,
           "stoff" AS `source_type`,
		   (SELECT GROUP_CONCAT(CONCAT("<img src='",
			(SELECT `value` FROM `tabSingles` WHERE `doctype` = "HOH Settings" AND `field` = "label_image_host"), 
			 `tabPflegesymbol`.`image`, "' style='width: 20px;' >")
			 ORDER BY `tabPflegesymbol`.`sort` DESC)
			FROM `tabItem Pflegesymbol` 
			LEFT JOIN `tabPflegesymbol` ON `tabPflegesymbol`.`name` = `tabItem Pflegesymbol`.`pflegesymbol`
			WHERE `tabItem`.`name` = `tabItem Pflegesymbol`.`parent` AND `tabItem Pflegesymbol`.`parenttype` = "Item"
		   ) AS `pflegesymbole`,
		   (SELECT GROUP_CONCAT(CONCAT(ROUND(`tabItem Komposition`.`anteil`, 0), "% ", `tabItem Komposition`.`material`) ORDER BY `idx` ASC)
			FROM `tabItem Komposition`
			WHERE `tabItem`.`name` = `tabItem Komposition`.`parent` AND `tabItem Komposition`.`parenttype` = "Item"
		   ) AS `material`,
		   "" AS `stoffe`,
		   "" AS `pailletten`,
		   IFNULL(`tabItem Price`.`price_list_rate`, 0) AS `standard_selling_rate`
		FROM `tabItem`
		LEFT JOIN `tabItem Price` ON (`tabItem Price`.`item_code` = `tabItem`.`name` AND `tabItem Price`.`selling` = 1)
	   WHERE `tabItem`.`name` IN ({selected_items}) AND `tabItem`.`item_group` IN ("Stoffe", "Eigenware Stoffe", "Applikationen");""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)
    
def get_item_label_data(selected_items):
    sql_query = """SELECT
                       `tabItem`.`item_code` AS `item_code`,
                       `tabItem`.`item_name` AS `item_name`,
                       `tabItem`.`item_group` AS `item_group`,
                       `tabItem`.`stock_uom` AS `stock_uom`,
                       `tabItem`.`d_stoffe` AS `d_stoffe`,
                       `tabItem`.`d_pailletten` AS `d_pailletten`,
                       `tabItem`.`d_applikationen` AS `d_applikationen`, 
                       `tabItem`.`d_prints` AS `d_prints`
                    FROM `tabItem`
                    WHERE `tabItem`.`name` IN ({selected_items});""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)

def get_work_order_label_data(selected_items):
    sql_query = """SELECT
                       `tabItem`.`item_code` AS `item_code`,
                       `tabItem`.`item_name` AS `item_name`,
                       `tabWork Order`.`stoff` AS `stoff`,
                       `tabWork Order`.`sales_order` AS `sales_order`,
                       `tabWork Order`.`name` AS `name`,
                       `tabWork Order`.`fg_warehouse` AS `fg_warehouse`,
                       `tabWork Order`.`production_item` AS `production_item`,
                       `tabWork Order`.`stickmaschine` AS `stickmaschine`,
                       `tabWork Order`.`pailletten` AS `pailletten`,
                       (SELECT CONCAT(ROUND(`tabSales Order Item`.`anzahl`, 0), " x ", ROUND(`tabSales Order Item`.`verkaufseinheit`, 1), " ", `tabSales Order Item`.`uom`) 
                        FROM `tabSales Order Item`
                        WHERE `tabSales Order Item`.`item_code` = `tabItem`.`item_code`
                          AND `tabSales Order Item`.`parent` = `tabWork Order`.`sales_order`
                        LIMIT 1) AS `qty`,
                        `tabItem`.`fertigbreite_von` AS `fertigbreite_von`,
                        `tabItem`.`fertigbreite_bis` AS `fertigbreite_bis`,
                        `tabSales Order`.`customer_name` AS `customer_name`
                    FROM `tabWork Order`
                    LEFT JOIN `tabItem` ON `tabItem`.`name` = `tabWork Order`.`production_item`
                    LEFT JOIN `tabSales Order` ON `tabSales Order`.`name` = `tabWork Order`.`sales_order`
                    WHERE `tabWork Order`.`name` IN ({selected_items});""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)

def get_delivery_note_label_data(selected_delivery_notes):
    sql_query = """SELECT
                       `tabDelivery Note`.`customer_name` AS `customer_name`,
                       IFNULL(`tA1`.`address_line1`, `tA2`.`address_line1`) AS `address_line1`,
                       IFNULL(`tA1`.`address_line2`, `tA2`.`address_line2`) AS `address_line2`,
                       IFNULL(`tA1`.`address_line3`, `tA2`.`address_line3`) AS `address_line3`,
                       IFNULL(`tA1`.`zusatzbezeichnung`, `tA2`.`zusatzbezeichnung`) AS `zusatzbezeichnung`,
                       IFNULL(`tA1`.`pincode`, `tA2`.`pincode`) AS `pincode`,
                       IFNULL(`tA1`.`city`, `tA2`.`city`) AS `city`,
                       IFNULL(`tA1`.`country`, `tA2`.`country`) AS `country`,
                       `tabDelivery Note`.`name` AS `delivery_note`,
                       `tabDelivery Note`.`po_no` AS `po_no`
                    FROM `tabDelivery Note`
                    LEFT JOIN `tabAddress` AS `tA1` ON `tA1`.`name` = `tabDelivery Note`.`shipping_address_name`
                    LEFT JOIN `tabAddress` AS `tA2` ON `tA2`.`name` = `tabDelivery Note`.`customer_address`
                    WHERE `tabDelivery Note`.`name` IN ({selected_delivery_notes});""".format(selected_delivery_notes=selected_delivery_notes)

    return frappe.db.sql(sql_query, as_dict=True)
    
def get_angebot_label_data(selected_quotation):
    sql_query = """SELECT
                       `tabBemusterung`.`item` AS `item`,
                       `tabBemusterung`.`name` AS `name`,
                       `tabBemusterung`.`bezeichnung` AS `bezeichnung`,
                       `tabBemusterung`.`stoffbreite_von` AS `stoffbreite_von`,
                       `tabBemusterung`.`stoffbreite_bis` AS `stoffbreite_bis`,
                       `tabBemusterung`.`fertigbreite_von` AS `fertigbreite_von`,
                       `tabBemusterung`.`fertigbreite_bis` AS `fertigbreite_bis`,
                       `tabBemusterung`.`gewicht` AS `gewicht`,
                       `tabBemusterung`.`d_stoffe` AS `d_stoffe`,
                       `tabBemusterung`.`d_pailletten` AS `d_pailletten`,
                       `tabBemusterung`.`d_applikationen` AS `d_applikationen`,
                       `tabBemusterung`.`d_prints` AS `d_prints`
                    FROM `tabAngebot Muster`
                    LEFT JOIN `tabAngebot` ON `tabAngebot Muster`.`parent` = `tabAngebot`.`name`
                    LEFT JOIN `tabBemusterung` ON `tabAngebot Muster`.`bemusterung` = `tabBemusterung`.`name`
                    WHERE `tabAngebot Muster`.`parent` IN ({selected_quotation});""".format(selected_quotation=selected_quotation)

    return frappe.db.sql(sql_query, as_dict=True)
    
@frappe.whitelist()
def get_price_label(musterkarte):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.label_printer_prices:
        frappe.throw( _("Please define a label printer for price labels under HOH Settings.") )
    label_printer = settings.label_printer_prices
    # get raw data
    mk = frappe.get_doc("Musterkarte", musterkarte)
    if len(mk.muster) > 0:
        title = mk.muster[0].bemusterung.split(" ")[0]
        source = mk.muster[0].bemusterung
    else:
        # fetch title from fabric
        fabric_item = frappe.get_doc("Item", mk.stoffe[0].stoffe)
        title = mk.title
        source = fabric_item.item_code
    data = { 
        'items': get_price_label_data(source),
        'date': datetime.today().strftime('%d.%m.%Y'),
        'rates': mk.preise,
        'title': title,
        'currency': mk.currency
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
    if not settings.item_label_printer or not settings.delivery_note_label_printer:
        frappe.throw( _("Please define an item label printer and a delivery note label printer under HOH Settings.") )
    # get raw data
    data = { 
        'items': get_item_label_data(selected_items),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    if len(data['items']) > 0 and data['items'][0]['item_group'] == 'Stickereien':
        content = frappe.render_template('hoh/templates/labels/item_label_sequin.html', data)
        label_printer = settings.delivery_note_label_printer
    else:
        content = frappe.render_template('hoh/templates/labels/item_label.html', data)
        label_printer = settings.item_label_printer
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
    items = get_work_order_label_data(selected_items)
    for i in items:
        i.url = quote("{host}/desk#Form/Work Order/{item_code}".format(host=settings.label_image_host, item_code=i.production_item), safe='')
    data = { 
        'items': items,
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('hoh/templates/labels/qr_wo_label.html', data)
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
    if not settings.delivery_note_label_printer:
        frappe.throw( _("Please define a delivery note label printer under HOH Settings.") )
    label_printer = settings.delivery_note_label_printer
    # get raw data
    data = { 
        'delivery_notes': get_delivery_note_label_data(selected_delivery_notes),
        'date': datetime.today().strftime('%d.%m.%Y'),
        'details': [],
        'detail_count': 0
    }
    # enrich item data
    for dn in data['delivery_notes']:
        dn_doc = frappe.get_doc("Delivery Note", dn['delivery_note'])
        data['details'].append(dn_doc.as_dict())
        for i in dn_doc.items:
            data['detail_count'] += i.anzahl
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
    if not settings.delivery_note_label_printer:
        frappe.throw( _("Please define a delivery note label printer under HOH Settings.") )
    label_printer = settings.delivery_note_label_printer
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

@frappe.whitelist()
def get_bemusterung_label(selected_items):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.bemusterung_label_printer:
        frappe.throw( _("Please define an bemusterung label printer under HOH Settings.") )
    label_printer = settings.bemusterung_label_printer
    # get raw data
    data = { 
        'items': get_bemusterung_label_data(selected_items),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('hoh/templates/labels/bemusterung_label.html', data)
    # create pdf
    if not label_printer:
        frappe.throw( _("Please set a printer under HOH settings") )
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"

@frappe.whitelist()
def get_angebot_label(selected_quotation):
    # get label printer
    settings = frappe.get_doc("HOH Settings", "HOH Settings")
    if not settings.bemusterung_label_printer:
        frappe.throw( _("Please define a bemusterung label printer under HOH Settings.") )
    # get raw data
    data = { 
        'items': get_angebot_label_data(selected_quotation)
    }
    # prepare content
    content = frappe.render_template('hoh/templates/labels/bemusterung_label.html', data)
    label_printer = settings.bemusterung_label_printer
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
