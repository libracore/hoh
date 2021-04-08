// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock by Sales Price"] = {
    "filters": [
        {
            fieldname: "item_name",
            label: __("Item Name"),
            fieldtype: "Data"
        },
        {
            fieldname: "item_code",
            label: __("Item Code"),
            fieldtype: "Link",
            options:"Item"
        },
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group"
        },
        {
            fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            options: "Warehouse",
            default: "Africa Shop - HOH"
        }
    ]
};
