// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Planning"] = {
    "filters": [

    ],
    "onload": (report) => {
        report.page.add_inner_button(__('Maschine zuweisen'), function ()  {
           frappe.set_route("List", "Work Order", {
                "stickmaschine": ["like", "%"], 
                "docstatus": ["<", 2],
                "status": ["!=", "Completed"]
            });
        });
    },
};
