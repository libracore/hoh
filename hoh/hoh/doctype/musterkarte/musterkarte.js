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
	},
    dessin: function(frm) {
        if ((!frm.doc.title) && (frm.doc.dessin)) {
            cur_frm.set_value('title', frm.doc.dessin);
        }
    }
});
