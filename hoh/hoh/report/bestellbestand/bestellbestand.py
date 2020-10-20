# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 100},
		{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 100},
		{"label": _("UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 50},
		{"label": _("Actual Qty"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Planned Qty"), "fieldname": "planned_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Requested Qty"), "fieldname": "indented_qty", "fieldtype": "Float", "width": 110, "convertible": "qty"},
		{"label": _("Ordered Qty"), "fieldname": "ordered_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Reserved Qty"), "fieldname": "reserved_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Reserved Qty for Production"), "fieldname": "reserved_qty_for_production", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Reserved for sub contracting"), "fieldname": "reserved_qty_for_sub_contract", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Safety Stock"), "fieldname": "safety_stock", "fieldtype": "Float", "width": 100, "convertible": "qty"},
		{"label": _("Projected Qty"), "fieldname": "projected_qty", "fieldtype": "Float", "width": 100, "convertible": "qty"}
	]

def get_data(filters):
	if filters.item_code:
		item_code_filter = """ AND `tabBin`.`item_code` = '{item_code}'""".format(item_code=filters.item_code)
	else:
		item_code_filter = ''
	
	data = frappe.db.sql("""SELECT 
								`tabBin`.`item_code` AS `item_code`,
								`tabItem`.`item_name` AS `item_name`,
								`tabItem`.`item_group` AS `item_group`,
								`tabItem`.`stock_uom` AS `uom`,
								`tabItem`.`safety_stock` AS `safety_stock`,
								`tabBin`.`actual_qty` AS `actual_qty`,
								`tabBin`.`planned_qty` AS `planned_qty`,
								`tabBin`.`indented_qty` AS `indented_qty`,
								`tabBin`.`ordered_qty` AS `ordered_qty`,
								`tabBin`.`reserved_qty` AS `reserved_qty`,
								`tabBin`.`reserved_qty_for_production` AS `reserved_qty_for_production`,
								`tabBin`.`reserved_qty_for_sub_contract` AS `reserved_qty_for_sub_contract`,
								`tabBin`.`projected_qty` AS `projected_qty`,
								CASE
									WHEN `tabBin`.`projected_qty` < 0 THEN ((`tabBin`.`projected_qty` * -1) + `tabItem`.`safety_stock`)
									WHEN `tabBin`.`projected_qty` > 0 THEN (`tabItem`.`safety_stock` - `tabBin`.`projected_qty`)
								END AS `zu bestellen`
							FROM `tabBin`
							LEFT JOIN `tabItem` ON `tabBin`.`item_code` = `tabItem`.`name`
							WHERE `tabBin`.`warehouse` = 'Lagerräume - HOH'
				AND `tabBin`.`projected_qty` < `tabItem`.`safety_stock`{item_code_filter};""".format(item_code_filter=item_code_filter), as_list=True)
	return data
