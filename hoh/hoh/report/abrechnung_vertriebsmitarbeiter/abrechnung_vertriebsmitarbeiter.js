// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Abrechnung Vertriebsmitarbeiter"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From date"),
            "fieldtype": "Date",
            "default": get_start_last_quarter(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To date"),
            "fieldtype": "Date",
            "default": get_end_last_quarter(),
            "reqd": 1
        },
        {
            "fieldname": "sales_person",
            "label": __("Sales Person"),
            "fieldtype": "Link",
            "options": "Sales Person",
            "reqd": 1
        }
    ]
};

function get_start_last_quarter() {
    var today = new Date(frappe.datetime.get_today());
    var act_month = today.getMonth();
    var fullyear = today.getFullYear();
    if ([0, 1, 2].includes(act_month)) {
        fullyear = fullyear - 1;
        var start = new Date(String(fullyear) + "-10-01");
    }
    if ([3, 4, 5].includes(act_month)) {
        var start = new Date(String(fullyear) + "-01-01");
    }
    if ([6, 7, 8].includes(act_month)) {
        var start = new Date(String(fullyear) + "-04-01");
    }
    if ([9, 10, 11].includes(act_month)) {
        var start = new Date(String(fullyear) + "-07-01");
    }
    return start;
}

function get_end_last_quarter() {
    var today = new Date(frappe.datetime.get_today());
    var act_month = today.getMonth();
    var fullyear = today.getFullYear();
    if ([0, 1, 2].includes(act_month)) {
        fullyear = fullyear - 1;
        var end = new Date(String(fullyear) + "-12-31");
    }
    if ([3, 4, 5].includes(act_month)) {
        var end = new Date(String(fullyear) + "-03-31");
    }
    if ([6, 7, 8].includes(act_month)) {
        var end = new Date(String(fullyear) + "-06-30");
    }
    if ([9, 10, 11].includes(act_month)) {
        var end = new Date(String(fullyear) + "-09-30");
    }
    
    return end;
}
