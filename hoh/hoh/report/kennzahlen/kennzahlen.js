// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Kennzahlen"] = {
    "filters": [
        {
            "fieldname":"year",
            "label": __("Year"),
            "fieldtype": "Int",
            "default": new Date().getFullYear(),
            "reqd": 1
        }
    ],
    "onload": (report) => {
        report.page.add_inner_button(__('Balance Sheet'), function () {
           window.location.href="/desk#query-report/Balance Sheet";
        }, __("Open") );
        report.page.add_inner_button(__('Profit and Loss Statement'), function () {
           window.location.href="/desk#query-report/Profit and Loss Statement";
        }, __("Open") );
        report.page.add_inner_button(__('Accounts Receivable'), function () {
           window.location.href="/desk#query-report/Accounts Receivable";
        }, __("Open") );
        report.page.add_inner_button(__('Accounts Payable'), function () {
           window.location.href="/desk#query-report/Accounts Payable";
        }, __("Open") );
    },
};
