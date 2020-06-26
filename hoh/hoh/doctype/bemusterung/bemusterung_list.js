// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.listview_settings['Bemusterung'] = {
    onload: function(listview) {
		listview.page.add_menu_item(__("Create Label"), function() {
            var selected = listview.get_checked_items();
            create_label(selected);
		});
	}
};

function create_label(selected) {
    // compile items list
    var selected_items = [];
    for (var i = 0; i < selected.length; i++) {
        selected_items.push(selected[i].name);
    }
    // retrieve pdf
    if (selected_items.length > 0) {
        // reference to the Label Printer record to be used
        var label_printer = "Labels 100x48mm"; 
        // html-content of the label
        var url = "/api/method/hoh.hoh.doctype.bemusterung.bemusterung.get_label"  
                + "?label_printer=" + encodeURIComponent(label_printer)
                + "&selected_items=" + encodeURIComponent("'" + selected_items.join("','") + "'");
        var w = window.open(
             frappe.urllib.get_full_url(url)
        );
        if (!w) {
            frappe.msgprint(__("Please enable pop-ups")); return;
        }
    } else {
        frappe.msgprint(__("Please select items")); return;
    }
}
