// Copyright (c) 2020-2021, libracore and contributors
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
                        try {
                            frappe.model.set_value(child.doctype, child.name, 'stickmaschine', dessin.stickmaschine[i].stickmaschine);
                        } catch { console.log("error"); }
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
               refresh_field(['komposition', 'gewicht']);
               cur_frm.dirty();
            }
        });
    },
    validate: function(frm) {
        // check that remaining material is 0..1
        for (var i = 0; i < frm.doc.items.length; i++) {
            if ((frm.doc.items[i].remaining_material < 0) || (frm.doc.items[i].remaining_material > 1)) {
                frappe.msgprint( __("Invalid remaining material in row {1}: {2} should be between 0 and 1.").replace("{1}", (i+1)).replace("{2}", frm.doc.items[i].remaining_material) );
                frappe.validated=false;
            }
        }
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
    },
    btn_nadelrechner: function(frm, cdt, cdn) {
        var target = {'cdt': cdt, 'cdn': cdn, 'field': 'qty'};
        var current = frappe.model.get_value(cdt, cdn, 'qty');
        var item_group = frappe.model.get_value(cdt, cdn, 'item_group'); 
        var g_per_m = frappe.model.get_value(cdt, cdn, 'weight_per_m');
        var g_per_uom = frappe.model.get_value(cdt, cdn, 'weight_per_unit');
        var uom = frappe.model.get_value(cdt, cdn, 'stock_uom');
        // ignore weight per m for pailletten, this is in pcs
        if (uom === "Stk") {
            g_per_m = 1;
            g_per_uom = 1;
        }
        nadelrechner(frm, current, 0.0, target, g_per_m, g_per_uom, uom);
    }
});

function update_title(frm) {
    if ((frm.doc.dessin) && (frm.doc.farbe) && (!frm.doc.title)) {
        cur_frm.set_value('title', frm.doc.dessin + " " + frm.doc.farbe);
    }
}

function nadelrechner(frm, input, output, target=null, g_per_m=1, g_per_uom=1, uom="kg") {
    var d = new frappe.ui.Dialog({
        'fields': [
            {'fieldname': 'stickrapport', 'label': 'Stickrapport', 'fieldtype': 'Select', 'options': '4/4\n8/4\n12/4\n16/4\n20/4\n24/4\n28/4\n32/4\n36/4\n40/4\n44/4\n48/4\n52/4\n56/4\n64/4\n68/4\n72/4\n76/4\n80/4\n84/4\n88/4\n92/4\n96/4\n104/4', 'default': frm.doc.stickrapport},
            {'fieldname': 'g_per_m', 'label': 'g pro m', 'fieldtype': 'Float', 'default': g_per_m, 'precission': 3},
            {'fieldname': 'g_per_uom', 'label': 'g pro ' + uom, 'fieldtype': 'Float', 'default': g_per_uom, 'precission': 3},
            {'fieldname': 'nadel', 'fieldtype': 'Float', 'label': 'x pro Nadel', 'default': input, 'precission': 3},
            {'fieldname': 'pro_m', 'fieldtype': 'Float', 'label': 'x pro Meter', 'read_only': 1, 'default': output, 'precission': 3}
        ],
        primary_action: function(){
            d.hide();
            // calculate
            var input = d.get_values().nadel;
            var g_per_m = d.get_values().g_per_m;
            var g_per_uom = d.get_values().g_per_uom;
            var needle_per_m = 114 / 9.1;
            if (frm.doc.stickrapport === "4/4") {
                needle_per_m = 342 / 9.1;
            } else if (frm.doc.stickrapport === "8/4") {
                needle_per_m = 171 / 9.1;
            } else if (frm.doc.stickrapport === "12/4") {
                needle_per_m = 114 / 9.1;
            } else if (frm.doc.stickrapport === "16/4") {
                needle_per_m = 86 / 9.1;
            } else if (frm.doc.stickrapport === "20/4") {
                needle_per_m = 69 / 9.1;
            } else if (frm.doc.stickrapport === "24/4") {
                needle_per_m = 57 / 9.1;
            } else if (frm.doc.stickrapport === "28/4") {
                needle_per_m = 49 / 9.1;
            } else if (frm.doc.stickrapport === "32/4") {
                needle_per_m = 43 / 9.1;
            } else if (frm.doc.stickrapport === "36/4") {
                needle_per_m = 38 / 9.1;
            } else if (frm.doc.stickrapport === "40/4") {
                needle_per_m = 35 / 9.1;
            } else if (frm.doc.stickrapport === "44/4") {
                needle_per_m = 31 / 9.1;
            } else if (frm.doc.stickrapport === "48/4") {
                needle_per_m = 29 / 9.1;
            } else if (frm.doc.stickrapport === "52/4") {
                needle_per_m = 26 / 9.1;
            } else if (frm.doc.stickrapport === "56/4") {
                needle_per_m = 24 / 9.1;
            } else if (frm.doc.stickrapport === "60/4") {
                needle_per_m = 22 / 9.1;
            } else if (frm.doc.stickrapport === "64/4") {
                needle_per_m = 21 / 9.1;
            } else if (frm.doc.stickrapport === "68/4") {
                needle_per_m = 20 / 9.1;
            } else if (frm.doc.stickrapport === "72/4") {
                needle_per_m = 19 / 9.1;
            } else if (frm.doc.stickrapport === "76/4") {
                needle_per_m = 18 / 9.1;
            } else if (frm.doc.stickrapport === "80/4") {
                needle_per_m = 17 / 9.1;
            } else if (frm.doc.stickrapport === "84/4") {
                needle_per_m = 16 / 9.1;
            } else if (frm.doc.stickrapport === "88/4") {
                needle_per_m = 15 / 9.1;
            } else if (frm.doc.stickrapport === "92/4") {
                needle_per_m = 14 / 9.1;
            } else if (frm.doc.stickrapport === "96/4") {
                needle_per_m = 14 / 9.1;
            } else if (frm.doc.stickrapport === "100/4") {
                needle_per_m = 13 / 9.1;
            } else if (frm.doc.stickrapport === "104/4") {
                needle_per_m = 13 / 9.1;
            } else {
                frappe.msgprint("Unbekannter Rapport");
            }
            output = input * needle_per_m * g_per_m / g_per_uom;
            // assure output is not smaller than 0.001 (minimum qty)
            if (output < 0.001) {
                output = 0.001;
            }
            // if there is a target, fill value
            if (target) {
                frappe.model.set_value(target.cdt, target.cdn, target.field, output);
            } else {
                // repeat
                nadelrechner(frm, input, output);
            }
        },
        primary_action_label: __('OK'),
        title: __("Nadelrechner")
    });
    d.show();
}
