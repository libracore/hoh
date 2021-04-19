// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Development Analysis"] = {
    "filters": [
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
            "width": "60px",
            "reqd": 1
        },
                {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "width": "60px",
            "reqd": 1
        },
        {
            "fieldname": "customer_group",
            "label": __("Customer Group"),
            "fieldtype": "Link",
            "options": "Customer Group"
        },
        {
            "fieldname": "territory",
            "label": __("Territory"),
            "fieldtype": "Link",
            "options": "Territory"
        },
        {
            "fieldname": "kollektion",
            "label": __("Kollektion"),
            "fieldtype": "Link",
            "options": "Kollektion"
        },
        {
            "fieldname": "gruppierung",
            "label": __("Gruppierung"),
            "fieldtype": "Select",
            "options": "Nach Kunde\nNach DWG\nNach Kundengruppe\nNach Region",
            "default": "Nach Kunde",
            "reqd": 1
        }
    ]
};
