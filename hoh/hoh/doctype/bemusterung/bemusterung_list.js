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
    console.log(selected_items);
    // retrieve full doctype information
    frappe.call({
        method: 'hoh.hoh.doctype.bemusterung.bemusterung.get_label_data',
        args: {
            selected_items: selected_items
        },
        callback: function(r) {
            if(r.message) {
                var label_objects = r.message;
                
                var content = "";
                for (var i = 0; i < label_objects.length; i++) {
                    content += "<table style=\"width: 100mm; height: 47mm;\"><tbody><tr>";
                    content += "<td></td>";
                    content += "<td>" + label_objects[i].name + "<br>";
                    content += label_objects[i].standard_selling_rate + "</td>";
                    content += "</tr></tbody></table>";
                }
                
                // reference to the Label Printer record to be used
                var label_printer = "Labels 100x48mm"; 
                // html-content of the label
                var url = "/api/method/erpnextswiss.erpnextswiss.doctype.label_printer.label_printer.download_label"  
                        + "?label_reference=" + encodeURIComponent(label_printer)
                        + "&content=" + encodeURIComponent(content);
                var w = window.open(
                     frappe.urllib.get_full_url(url)
                );
                if (!w) {
                    frappe.msgprint(__("Please enable pop-ups")); return;
                }
                        } 
                    }
                }); 
}
