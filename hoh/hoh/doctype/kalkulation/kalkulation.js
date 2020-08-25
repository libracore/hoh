// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Kalkulation', {
	refresh: function(frm) {

	},
    bemusterung: function(frm) {
        // change trigger for base item
        if (frm.doc.bemusterung) {
            frappe.call({
                method: 'load_items',
                doc: frm.doc,
                args: {
                    'base_item': frm.doc.bemusterung
                },
                callback: function(response) {
                    console.log("back");
                   var material = response.message;
                   console.log(material);
                   // clear material table
                   clear_material_rows(frm);
                   console.log("clear");
                   // fill material
                   for (var i = 0; i < material.length; i++) {
                       var child = cur_frm.add_child('material');
                        frappe.model.set_value(child.doctype, child.name, 'item', material[i].item);
                        frappe.model.set_value(child.doctype, child.name, 'qty', material[i].qty);
                        frappe.model.set_value(child.doctype, child.name, 'rate', material[i].rate);
                   }
                   cur_frm.refresh_field('material');
                }
            });
        }
    }
});

function clear_material_rows(frm) {
    // remove all rows
    var tbl = frm.doc.material || [];
    var i = tbl.length;
    while (i--)
    {
        cur_frm.get_field("material").grid.grid_rows[i].remove();
    }
    cur_frm.refresh();
}
