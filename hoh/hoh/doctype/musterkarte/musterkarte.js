// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Musterkarte', {
	refresh: function(frm) {
        frm.fields_dict.muster.grid.get_field('bemusterung').get_query =
            function() {
                return {
                    filters: {
                        "dessin": frm.doc.dessin
                    }
                }
            };
        
        if ((frm.doc.__islocal) && (!frm.doc.muster) && (frm.doc.dessin)) {
            // initialise all variants
            get_variants(frm);
        }
	},
    dessin: function(frm) {
        if ((!frm.doc.title) && (frm.doc.dessin)) {
            cur_frm.set_value('title', frm.doc.dessin);
        }
    }
});

function get_variants(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
        doctype: 'Bemusterung',
        filters: [
            ['dessin', '=', frm.doc.dessin]
        ],
            fields: ['name'],
        },
        callback: function(response) {
            if (response.message) {
                for (var i = 0; i < response.message.length; i++) {
                    var child = cur_frm.add_child('muster');
                    frappe.model.set_value(child.doctype, child.name, 'bemusterung', response.message[i].name);
                }
                cur_frm.refresh_field('muster');
            }
        }
    });
}
