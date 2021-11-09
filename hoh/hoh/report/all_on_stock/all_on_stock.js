// Copyright (c) 2016-2021, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["All on Stock"] = {
	"filters": [
		{
            "fieldname":"item_group",
            "label": __("Item group"),
            "fieldtype": "Link",
            "options": "Item Group",
        },
		{
            "fieldname":"warehouse",
            "label": __("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
        }
	]
};
