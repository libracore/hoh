// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stickplan"] = {
	"filters": [
        {
            "fieldname":"stickmaschine",
            "label": __("Stickmaschine"),
            "fieldtype": "Link",
            "options": "Stickmaschine"
        },
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "width": "60px"
        },
                {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), +12),
            "width": "60px"
        }
	]
};
