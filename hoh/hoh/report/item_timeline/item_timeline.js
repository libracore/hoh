// Copyright (c) 2020-2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Timeline"] = {
    "filters": [
        {
            "fieldname":"item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item"
        }
    ],
    "onload": (report) => {
        report.page.add_inner_button(__('Bestellbestand'), function () {
           frappe.set_route("query-report", "Bestellbestand");
        })
    }
};
