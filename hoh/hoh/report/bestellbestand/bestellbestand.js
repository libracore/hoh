// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bestellbestand"] = {
	"filters": [
		{
			fieldname: "item_name",
			label: __("Item Name"),
			fieldtype: "Link",
			options:"Item Name",
			default: "",
		},
		{
			fieldname: "item_code",
			label: __("Item Code"),
			fieldtype: "Link",
			options:"Item",
			default: "",
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Select",
			options: "Item Group",
			default: "",
		}
	]
};
