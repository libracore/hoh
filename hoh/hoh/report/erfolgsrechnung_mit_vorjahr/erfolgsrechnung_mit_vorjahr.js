// Copyright (c) 2022, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Erfolgsrechnung mit Vorjahr"] = {
    "filters": [
        {
            "fieldname":"date",
            "label": __("Date"),
            "fieldtype": "Date",
            "default": new Date(),
            "reqd": 1
        },
        {
            "fieldname":"company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("company"),
            "reqd": 1
        }
    ]
};
