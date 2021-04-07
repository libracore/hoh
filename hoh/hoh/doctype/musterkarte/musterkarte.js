// Copyright (c) 2020-21, libracore and contributors
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
        frm.fields_dict.stoffe.grid.get_field('stoffe').get_query =
            function() {
                return {
                    filters: {
                        "item_group": 'Stoffe'
                    }
                }
            };
        
        if ((frm.doc.__islocal) && (!frm.doc.muster) && (frm.doc.dessin)) {
            // initialise all variants
            get_variants(frm);
        }

        // add label button
        frm.add_custom_button(__("Etikette erstellen"), function() {
            create_label(frm);
        }).addClass("btn-primary");
    },
    dessin: function(frm) {
        if ((!frm.doc.title) && (frm.doc.dessin)) {
            cur_frm.set_value('title', frm.doc.dessin);
            get_variants(frm) ;
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

/* label printing function */
function create_label(frm) {
    // html-content of the label - price label
    var url = "/api/method/hoh.hoh.labels.get_price_label"  
            + "?musterkarte=" + encodeURIComponent(frm.doc.name);
    var w = window.open(
         frappe.urllib.get_full_url(url)
    );
    if (!w) {
        frappe.msgprint(__("Please enable pop-ups")); return;
    }
    // content of item detail labels
    var selected_items = [];
    for (var i = 0; i < frm.doc.muster.length; i++) {
        selected_items.push(frm.doc.muster[i].bemusterung);
    }
    for (var i = 0; i < frm.doc.stoffe.length; i++) {
        selected_items.push(frm.doc.stoffe[i].stoffe);
    }
    url = "/api/method/hoh.hoh.labels.get_bemusterung_label"  
            + "?selected_items='" + selected_items.join("','") + "'";
    var w2 = window.open(
         frappe.urllib.get_full_url(url)
    );
    if (!w2) {
        frappe.msgprint(__("Please enable pop-ups")); return;
    }
}
