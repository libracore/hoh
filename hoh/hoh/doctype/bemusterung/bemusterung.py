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
    
    def before_save(self):
        # update specification lines
        stoffe = []
        pailletten = []
        applikationen = []
        prints = []
        for m in self.items:
            if m.item_group in ['Stoffe', 'Hilfsstoffe']:
                if self.panneau:
                    # in case of panneau, add fabric fractions
                    fraction = "1/1"
                    if m.remaining_material <= 0.20:
                        raction = "1/5"
                    elif m.remaining_material <= 0.25:
                        fraction = "1/4"
                    elif m.remaining_material <= 0.35:
                        fraction = "1/3"
                    elif m.remaining_material <= 0.55:
                        fraction = "1/2"
                    elif m.remaining_material <= 0.7:
                        fraction = "2/3"
                    stoffe.append("{0} {1}".format(fraction, m.item_name))
                else:
                    # normal case
                    stoffe.append(m.item_name)
            elif m.item_group in ['Kordel', 'Pailletten', 'Garne']:
                pailletten.append(m.item_name)
            elif m.item_group in ['Steine', 'Applikationen']:
                applikationen.append(m.item_name)
            elif m.item_group in ['Print']:
                prints.append(m.item_name)
        self.d_stoffe = " + ".join(stoffe)
        self.d_pailletten = " + ".join(pailletten)
        self.d_applikationen = " + ".join(applikationen)
        self.d_prints = " + ".join(prints)
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
            'is_sales_item': 1,
            'd_stoffe': self.d_stoffe,
            'd_pailletten': self.d_pailletten,
            'd_applikationen': self.d_applikationen,
            'd_prints': self.d_prints
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
        # set default warehouse
        if "Nigeria" in (self.kollektion or ""):
            row = new_item.append('item_defaults', {
                    'default_warehouse': "Africa Shop - HOH"
                })
        else:
            row = new_item.append('item_defaults', {
                    'default_warehouse': "Fertigerzeugnisse - HOH"
                })
        # insert
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
    
    def calculate_composition(self, debug=False):
        composition = {}
        total_multiplier = 0
        if debug:
            print("Compontent parts:")
        # fetch all items
        for i in self.items:
            item = frappe.get_doc("Item", i.item_code)
            # proceed only with components that have a composition and not with Pailleten (based on foil) and exclude support materials
            if item.komposition and not (item.item_group == "Folie" or item.item_group == "Hilfsstoffe"):
                multiplier = (i.qty * item.weight_per_unit or 1)
                total_multiplier += multiplier
                # aggregate contents
                for c in item.komposition:
                    new_part = i.remaining_material * c.anteil * multiplier
                    if c.material in composition:
                        composition[c.material] = composition[c.material] + new_part
                    else:
                        composition[c.material] = new_part
                    if debug:
                        print("Adding {f}x{q}x{m} ({qty}x{w}) of {c} from {i} ({g})".format(
                            q=c.anteil, m=multiplier, c=c.material, i=i.item_code, g=item.item_group,
                            qty=i.qty, w=(item.weight_per_unit or 1), f=i.remaining_material))
            else:
                if debug:
                    if not item.komposition:
                        print("Item {0} ({1}) has no composition".format(i.item_code, item.item_group))
                    else:
                        print("Item {0} ({1}) is auxiliary (Folie/Hilfsstoffe)".format(i.item_code, item.item_group))
        # store total weight
        self.gewicht = ((total_multiplier or 0) / 1000)
        # normalise contents
        if debug:
            print("Raw composition")
        for key, value in composition.items():
            composition[key] = round(value / total_multiplier)
            # minimum fraction is 1%
            if composition[key] < 1:
                composition[key] = 1
            if debug:
                print("{0}: {1} ({2} %)".format(key, value, composition[key]))
        # assure that sum is 100%
        sum_p = 0
        for key, value in composition.items():
            sum_p += value
        # subtract highest
        composition[max(composition, key=lambda key: composition[key])] = composition[max(composition, key=lambda key: composition[key])] - (sum_p - 100)
        # update composition
        self.komposition = []
        for key, value in sorted(composition.items(), key=lambda kv: kv[1], reverse=True):
            row = self.append('komposition', {
                'anteil': value,
                'material': key
            })
        return

"""
This is a troubleshooting function for the composition calulcation that allows tracing

Use from console with
 $ bench execute hoh.hoh.doctype.bemusterung.bemusterung.debug_composition --kwargs "{'bemusterung': '37572GU.LU TS2'}"
"""
def debug_composition(bemusterung):
    doc = frappe.get_doc("Bemusterung", bemusterung)
    print("Composition calculation trace for {0}".format(bemusterung))
    doc.calculate_composition(debug=True)
    print("Composition trace end")
    return
