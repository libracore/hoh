// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Abrechnung Vertriebsmitarbeiter"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
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
            "fieldname": "owner",
            "label": __("Owner"),
            "fieldtype": "Link",
            "options": "User",
            "reqd": 1
        }
    ]
};
