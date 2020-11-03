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
        },
                {
            "fieldname":"sales_order",
            "label": __("Sales Order"),
            "fieldtype": "Link",
            "options": "Sales Order"
        },
        {
            "fieldname":"item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item"
        }
    ],
    "onload": (report) => {
        report.page.add_inner_button(__('Work Order List'), function () {
           window.location.href="/desk#List/Work Order/List";
        });
        report.page.add_inner_button(__('Update Material'), function () {
           frappe.call({
            "method": "hoh.hoh.report.stickplan.stickplan.update_material_status",
            "callback": function(response) {
                frappe.show_alert( __("Updated") );
            }
        });
        });
    }
};

/* add event listener for double clicks to move up */
cur_page.container.addEventListener("dblclick", function(event) {
    var content = event.target.innerHTML;
    if (content.startsWith("WO-")) {
        /* move this work order up by one */
        
    }
});
