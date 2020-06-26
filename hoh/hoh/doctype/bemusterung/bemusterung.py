# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from erpnextswiss.erpnextswiss.doctype.label_printer.label_printer import create_pdf
from datetime import datetime

class Bemusterung(Document):
    def validate(self):
        # make sure only one sample with this colour is used
        same_color_dessins = frappe.get_all("Bemusterung", 
            filters={'dessinnummer': self.dessinnummer, 'farbe': self.farbe},
            fields=['name'])
        if len(same_color_dessins) > 1 or \
           (len(same_color_dessins) == 1 and same_color_dessins[0]['name'] != self.name):
            frappe.throw( _("Diese Dessin/Farb-Kombination existiert bereits in {0}.".format(
                same_color_dessins[0]['name'])) )
        return
        
    def create_item(self):
        # create new item
        new_item = frappe.get_doc({
            'doctype': 'Item',
            'item_name': self.bezeichnung,
            'item_code': self.name,
            'item_group': 'Stickereien',
            'is_stock_item': 1,
            'stock_uom': 'm',
            'dessin': self.dessin,
            'bemusterung': self.name,
            'komposition': self.komposition,
            'pflegesymbole': self.pflegesymbole,
            'stoffbreite_von': self.stoffbreite_von,
            'stoffbreite_bis': self.stoffbreite_bis,
            'fertigbreite_von': self.fertigbreite_von,
            'fertigbreite_bis': self.fertigbreite_bis,
            'country_of_origin':self.country_of_origin,
            'customs_tariff_number': self.customs_tariff_number,
            't_min_menge': self.minimalmenge,
            'standard_rate': self.rate,
            'weight_uom': 'kg',
            'weight_per_unit': self.gewicht,
            'stickmaschine': self.stickmaschine
        })
        for k in self.komposition:
            row = new_item.append('komposition', {
                'anteil': k.anteil,
                'material': k.material
            })
        for p in self.pflegesymbole:
            row = new_item.append('pflegesymbole', {
                'pflegesymbol': p.pflegesymbol
            })
        item = new_item.insert()
        # create new BOM
        new_bom = frappe.get_doc({
            'doctype': 'BOM',
            'item': item.item_code,
            'quantity': 1,
            'is_active': 1,
            'is_default': 1,
            'allow_same_item_multiple_times': 1
        })
        for i in self.items:
            row = new_bom.append('items', {
                'item_code': i.item_code,
                'qty': i.qty,
                'rate': i.valuation_rate
            })
        bom = new_bom.insert()
        # create reference
        self.item = item.name
        self.save()
        # write changes
        frappe.db.commit()
        # return item code
        return item.name
    
    def calculate_composition(self):
        composition = {}
        total_multiplier = 0
        # fetch all items
        for i in self.items:
            item = frappe.get_doc("Item", i.item_code)
            if item.komposition:
                multiplier = (i.qty * item.weight_per_unit or 1)
                total_multiplier += multiplier
                # aggregate contents
                for c in item.komposition:
                    # exclude support materials, the will leave the product in finish
                    if c.material not in ['AC', 'AB', 'VL']:
                        if c.material in composition:
                            composition[c.material] = composition[c.material] + c.anteil * multiplier
                        else:
                            composition[c.material] = c.anteil * multiplier
        # normalise contents
        for key, value in composition.items():
            composition[key] = round(value / total_multiplier)
        # assure that sum is 100%
        sum_p = 0
        for key, value in composition.items():
            sum_p += value
        # subtract highest
        composition[max(composition, key=lambda key: composition[key])] = composition[max(composition, key=lambda key: composition[key])] - (sum_p - 100)
        # update composition
        self.komposition = []
        for key, value in composition.items():
            row = self.append('komposition', {
                'anteil': value,
                'material': key
            })
        return

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
                       `tabItem Pflegesymbol`.`pflegesymbol` AS `pflegesymbol`,
                       `tabItem Komposition`.`material` AS `material`,
                       `tabItem Komposition`.`anteil` AS `anteil`,
                       IFNULL(`tabItem Price`.`price_list_rate`, 0) AS `standard_selling_rate`
                   FROM `tabBemusterung`
                   LEFT JOIN `tabItem` AS `tabItem` ON `tabItem`.`name` = `tabBemusterung`.`name`
                   LEFT JOIN `tabItem Price` AS `tabItem Price` ON (`tabItem Price`.`item_code` = `tabBemusterung`.`name` AND `tabItem Price`.`selling` = 1)
                   LEFT JOIN `tabItem Pflegesymbol` AS `tabItem Pflegesymbol` ON `tabBemusterung`.`name` = `tabItem Pflegesymbol`.`parent`
                   LEFT JOIN `tabItem Komposition` AS `tabItem Komposition` ON `tabBemusterung`.`name` = `tabItem Komposition`.`parent`;
                   WHERE `tabBemusterung`.`name` IN ({selected_items});""".format(selected_items=selected_items)

    return frappe.db.sql(sql_query, as_dict=True)

@frappe.whitelist()
def get_label(label_printer, selected_items):
    # get raw data
    data = { 
        'items': get_label_data(selected_items),
        'date': datetime.today().strftime('%d.%m.%Y')
    }
    # prepare content
    content = frappe.render_template('hoh/hoh/doctype/bemusterung/price_label.html', data)
    # create pdf
    printer = frappe.get_doc("Label Printer", label_printer)
    pdf = create_pdf(printer, content)
    # return download
    frappe.local.response.filename = "{name}.pdf".format(name=label_printer.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = pdf
    frappe.local.response.type = "download"
    
