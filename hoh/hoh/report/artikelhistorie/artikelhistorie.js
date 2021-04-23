// Copyright (c) 2020-2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Artikelhistorie"] = {
    "filters": [
        {
            "fieldname":"item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "options": "Item",
        },
        {
            "fieldname":"customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": "60px"
        }
    ],
};

