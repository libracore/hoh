// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bemusterung', {
	refresh: function(frm) {

	},
    dessin: function(frm) {
        console.log("dessin...");
        if (!frm.doc.bezeichnung) {
            frappe.call({
                "method": "frappe.client.get",
                "args": {
                    "doctype": "Dessin",
                    "name": frm.doc.dessin
                },
                "callback": function(response) {
                    var dessin = response.message;

                    if (dessin) {
                        frm.set_value('bezeichnung', dessin.bezeichnung);
                    } 
                }
            });
            // cur_frm.add_fetch('dessin', 'bezeichnung', 'bezeichnung');
            console.log("set...");
        }
        
        update_title(frm);
    },
    farbe: function(frm) {
        update_title(frm);
    }
});

function update_title(frm) {
    if ((frm.doc.dessin) && (frm.doc.farbe) && (!frm.doc.title)) {
        cur_frm.set_value('title', frm.doc.dessin + " " + frm.doc.farbe);
    }
}
