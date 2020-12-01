# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

class Bemusterung(Document):
    def validate(self):
        # make sure only one sample with this colour is used (made obsolete 2020-11-11)
        #same_color_dessins = frappe.get_all("Bemusterung", 
        #    filters={'dessinnummer': self.dessinnummer, 'farbe': self.farbe},
        #    fields=['name'])
        #if len(same_color_dessins) > 1 or \
        #   (len(same_color_dessins) == 1 and same_color_dessins[0]['name'] != self.name):
        #    frappe.throw( _("Diese Dessin/Farb-Kombination existiert bereits in {0}.".format(
        #        same_color_dessins[0]['name'])) )
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
            'farbe': self.farbe,
            'komposition': self.komposition,
            'pflegesymbole': self.pflegesymbole,
            'stoffbreite_von': self.stoffbreite_von,
            'stoffbreite_bis': self.stoffbreite_bis,
            'fertigbreite_von': self.fertigbreite_von,
            'fertigbreite_bis': self.fertigbreite_bis,
            'country_of_origin':self.country_of_origin,
            'customs_tariff_number': self.customs_tariff_number,
            't_min_menge': self.minimalmenge,
            'weight_uom': 'g',
            'weight_per_unit': (self.gewicht * 1000),
            'gewicht': (self.gewicht * 1000),
            'is_sales_item': 1
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
        for s in self.stickmaschine:
            row = new_item.append('stickmaschine', {
                'stickmaschine': s.stickmaschine
            })
        item = new_item.insert()
        # create new item price record
        price_list = frappe.get_value("Selling Settings", "Selling Settings", "selling_price_list")
        new_item_price = frappe.get_doc({
            'doctype': 'Item Price',
            'item_code': item.item_code,
            'uom': 'm',
            'price_list': price_list,
            'price_list_rate': self.rate
        })
        new_item_price.insert()
        # create new BOM
        new_bom = frappe.get_doc({
            'doctype': 'BOM',
            'item': item.item_code,
            'quantity': 1,
            'is_active': 1,
            'is_default': 1,
            'allow_same_item_multiple_times': 1,
            'uom': new_item.stock_uom
        })
        for i in self.items:
            row = new_bom.append('items', {
                'item_code': i.item_code,
                'qty': i.qty,
                'uom': i.stock_uom,
                'rate': i.valuation_rate
            })
        bom = new_bom.insert()
        bom.submit()            # auto submit BOM
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
            # proceed only with components that have a composition and not with Pailleten (based on foil)
            if item.komposition and not item.item_group == "Folie":
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
        # store total weight
        self.gewicht = ((total_multiplier or 0) / 1000)
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
