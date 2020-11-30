// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Statistik Warenbewegung"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "default": "Stoffe",
            "reqd": 1
        }
    ]
};

/* add event listener for double clicks to move up */
cur_page.container.addEventListener("dblclick", function(event) {
    var content = strip_html_tags(event.target.innerHTML).trim();
    if (content.includes(": ")) {
        frappe.set_route("query-report", "Detail Warenbewegung", {"item": content.split(': ')[0]});
    }
});

function strip_html_tags(str)
{
   if ((str===null) || (str===''))
       return false;
   else
   str = str.toString();
  return str.replace(/<[^>]*>/g, '');
}

