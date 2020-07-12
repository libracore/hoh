// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bemusterung', {
	refresh: function(frm) {
        if ((!frm.doc.__islocal) && (!frm.doc.item)) {
            frm.add_custom_button(__("Artikel erstellen"), function() {
                frappe.call({
                    method: 'create_item',
                    doc: frm.doc,
                    callback: function(response) {
                       frappe.show_alert( __("Erstellt: ") + response.message );
                       cur_frm.reload_doc();
                    }
                });

            });
        }
        frm.add_custom_button(__("Nadelrechner"), function() {
            nadelrechner(frm, 0.0, 0.0);
        });
	},
    dessin: function(frm) {
        console.log("dessin...");
        frappe.call({
            "method": "frappe.client.get",
            "args": {
                "doctype": "Dessin",
                "name": frm.doc.dessin
            },
            "callback": function(response) {
                var dessin = response.message;

                if (dessin) {
                    cur_frm.set_value('bezeichnung', dessin.bezeichnung);
                    for (var i = 0; i < dessin.stickmaschine.length; i++) {
                        var child = cur_frm.add_child('stickmaschine');
                        frappe.model.set_value(child.doctype, child.name, 'stickmaschine', dessin.stickmaschine[i].stickmaschine);
                    }
                    cur_frm.refresh_field('stickmaschine');
                } 
                
                update_title(frm);
            }
        });
    },
    farbe: function(frm) {
        update_title(frm);
    },
    calculate_composition: function(frm) {
        frappe.call({
            method: 'calculate_composition',
            doc: frm.doc,
            callback: function(response) {
               frappe.show_alert( __("Done!") );
               refresh_field(['komposition']);
            }
        });
    }
});

frappe.ui.form.on('Bemusterung Artikel', {
    item_group: function(frm, cdt, cdn) {
        // if the item is a fabric, fetch width
        if (frappe.model.get_value(cdt, cdn, 'item_group') === "Stoffe") {
            frappe.call({
                'method': 'frappe.client.get',
                'args': {
                    'doctype': 'Item',
                    'name': frappe.model.get_value(cdt, cdn, 'item_code')
                },
                'callback': function(response) {
                    var item = response.message;

                    if (item) {
                        cur_frm.set_value('stoffbreite_von', item.stoffbreite_von);
                        cur_frm.set_value('stoffbreite_bis', item.stoffbreite_bis);
                    } 
                }
            });
        }
    }
});

function update_title(frm) {
    if ((frm.doc.dessin) && (frm.doc.farbe) && (!frm.doc.title)) {
        cur_frm.set_value('title', frm.doc.dessin + " " + frm.doc.farbe);
    }
}

function nadelrechner(frm, input, output) {
    var d = new frappe.ui.Dialog({
        'fields': [
            {'fieldname': 'stickrapport', 'label': 'Stickrapport', 'fieldtype': 'Data', 'read_only': 1, 'default': frm.doc.stickrapport},
            {'fieldname': 'nadel', 'fieldtype': 'Float', 'label': 'x pro Nadel', 'default': input},
            {'fieldname': 'pro_m', 'fieldtype': 'Float', 'label': 'x pro Meter', 'read_only': 1, 'default': output}
        ],
        primary_action: function(){
            d.hide();
            // calculate
            var input = d.get_values().nadel;
            var needle_per_m = 70 / 9.26;
            if (frm.doc.stickrapport === "4/4") {
                needle_per_m = 684 / 9.26;
            } else if (frm.doc.stickrapport === "8/4") {
                needle_per_m = 342 / 9.26;
            } else if (frm.doc.stickrapport === "12/4") {
                needle_per_m = 228 / 9.26;
            } else if (frm.doc.stickrapport === "16/4") {
                needle_per_m = 172 / 9.26;
            } else if (frm.doc.stickrapport === "20/4") {
                needle_per_m = 138 / 9.26;
            } else if (frm.doc.stickrapport === "24/4") {
                needle_per_m = 114 / 9.26;
            } else if (frm.doc.stickrapport === "28/4") {
                needle_per_m = 98 / 9.26;
            } else if (frm.doc.stickrapport === "32/4") {
                needle_per_m = 86 / 9.26;
            } else if (frm.doc.stickrapport === "36/4") {
                needle_per_m = 76 / 9.26;
            } else if (frm.doc.stickrapport === "40/4") {
                needle_per_m = 70 / 9.26;
            } else {
                frappe.msgprint("Unbekannter Rapport");
            }
            output = input * needle_per_m;
            // repeat
            nadelrechner(frm, input, output);
        },
        primary_action_label: __('OK'),
        title: __("Nadelrechner")
    });
    d.show();
}
