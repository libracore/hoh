// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Production Throughput"] = {
	"filters": [
		{
			"fieldname": "year",
			"label": __("Year"),
			"fieldtype": "Int",
			"default": new Date().getFullYear(),
			"reqd": 1
		}
	],
    "onload": (report) => {
        report.page.add_inner_button(__('Stickplan'), function () {
           window.location.href="/desk#query-report/Stickplan";
        } );
    },
};
