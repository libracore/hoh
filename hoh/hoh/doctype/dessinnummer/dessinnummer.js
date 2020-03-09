// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dessinnummer', {
	refresh: function(frm) {
        if (!frm.doc.dessinnummer) {
            find_next_number(frm);
            console.log("find next");
        }
	}
});

function find_next_number(frm) {
    frappe.call({
        method: 'find_next_number',
        doc: frm.doc,
        callback: function(response) {
           cur_frm.set_value('dessinnummer', response.message);
           refresh_field(['dessinnummer']);
        }
    });
}
