// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Statistik Warenbewegung"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "default": "Stoffe",
            "reqd": 1
        }
    ]
};
