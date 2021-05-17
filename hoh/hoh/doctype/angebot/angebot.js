// Copyright (c) 2020, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Angebot', {
    refresh: function(frm) {
        cur_frm.fields_dict['customer_address'].get_query = function(doc) {
            return {
                filters: {
                    "link_doctype": "Customer",
                    "link_name": frm.doc.customer
                }
            }
        }
        cur_frm.fields_dict['customer_contact'].get_query = function(doc) {
            return {
                filters: {
                    "link_doctype": "Customer",
                    "link_name": frm.doc.customer
                }
            }
        }
        if (!frm.doc.angebotsdatum) {
            cur_frm.set_value('angebotsdatum', frappe.datetime.nowdate());
            cur_frm.refresh_field('angebotsdatum');
        }
        if (frm.doc.docstatus == 0) {
            frm.add_custom_button(__("Artikel von Kollektion"), function() {
                load_collection(frm);
            });
            frm.add_custom_button(__("Artikel von Dessin"), function() {
                load_dessin(frm);
            });
        }
    },
    currency: function(frm) {
        if (frm.doc.currency == "EUR") {
            cur_frm.set_value('exchange_rate', 1);
        } else {
            get_exchange_rate(frm);
        }
    }
});

frappe.ui.form.on('Angebot Muster', {
    qty: function(frm, cdt, cdn) {
        update_row_amount(frm, cdt, cdn)
    },
    rate: function(frm, cdt, cdn) {
        var base_rate = frappe.model.get_value(cdt, cdn, 'rate') / frm.doc.exchange_rate;
        frappe.model.set_value(cdt, cdn, "base_rate", base_rate);
        update_row_amount(frm, cdt, cdn)
    },
    base_rate: function(frm, cdt, cdn) {
        var rate = frappe.model.get_value(cdt, cdn, 'base_rate') * frm.doc.exchange_rate
        frappe.model.set_value(cdt, cdn, "rate", rate);
    },
    dessin: function(frm,  cdt, cdn) {
        var d = frappe.model.get_value(cdt, cdn, 'dessin');
        if (d) {
            frappe.call({
                "method": "frappe.client.get",
                "args": {
                    "doctype": "Dessin",
                    "name": d
                },
                "callback": function(response) {
                    var dessin = response.message;
                    if (dessin) {
                        frappe.model.set_value(cdt, cdn, "dessin_image", dessin.image);
                    } 
                }
            });
        }
    },
    bemusterung: function(frm,  cdt, cdn) {
        var d = frappe.model.get_value(cdt, cdn, 'bemusterung');
        if (d) {
            frappe.call({
                "method": "frappe.client.get",
                "args": {
                    "doctype": "Bemusterung",
                    "name": d
                },
                "callback": function(response) {
                    var bemusterung = response.message;
                    if (bemusterung) {
                        frappe.model.set_value(cdt, cdn, "image", bemusterung.image);
                        var compositions = [];
                        for (var i = 0; i < bemusterung.komposition.length; i++) {
                            compositions.push(bemusterung.komposition[i].anteil 
                                + "% " + bemusterung.komposition[i].material);
                        }
                        frappe.model.set_value(cdt, cdn, "zusammensetzung", compositions.join(", "));
                    }
                    // get care symbols
                    frappe.call({
                        "method": "hoh.hoh.doctype.angebot.angebot.get_care_symbol_html",
                        "args": {
                            "bemusterung": d
                        },
                        "callback": function(response) {
                            var html = response.message;
                            frappe.model.set_value(cdt, cdn, "pflegesymbole", html);
                        }
                    });
                }
            });
        }
    }
});

function update_row_amount(frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    var amount = item.qty * item.rate;
    item.amount = amount;
    cur_frm.refresh_field('muster');
    
    // overall total
    var net_total = 0;
    for (var i = 0; i < frm.doc.muster.length; i++) {
        net_total += (frm.doc.muster[i].base_rate + frm.doc.muster[i].qty);
    }
    cur_frm.set_value('base_net_total', net_total);
    cur_frm.refresh_field('base_net_total');
    cur_frm.set_value('net_total', (net_total * frm.doc.exchange_rate));
    cur_frm.refresh_field('net_total');
}

function update_currency_values(frm) {
    var exchange_rate = frm.doc.exchange_rate;
    for (var i = 0; i < frm.doc.muster.length; i++) {
        frappe.model.set_value(cur_frm.doc.items[i].doctype, cur_frm.doc.muster[i].name, 
            "rate", frm.doc.muster[i].net_rate * exchange_rate);
        frappe.model.set_value(cur_frm.doc.items[i].doctype, cur_frm.doc.muster[i].name, 
            "amount", frm.doc.muster[i].net_rate * exchange_rate * frm.doc.muster[i].qty);
    }
    cur_frm.refresh_field('items');
    cur_frm.set_value('net_total', frm.doc.base_net_total * exchange_rate);
    cur_frm.refresh_field('base_net_total');
}

function get_exchange_rate(frm) {
    frappe.call({
        method: 'erpnextaustria.erpnextaustria.utils.get_eur_exchange_rate',
        args: {
            'currency': frm.doc.currency
        },
        callback: function(r) {
            if (r.message) {
                var exchange_rate = r.message;
                cur_frm.set_value('exchange_rate', exchange_rate);
                console.log("Exchange rate " + frm.doc.currency + ": " + exchange_rate);
            } else {
                cur_frm.set_value('exchange_rate', 1);
            }
        }
    });
}

function load_collection(frm) {
    // show dialog to select collection
    frappe.prompt([
            {
                'fieldname': 'collection', 
                'fieldtype': 'Link', 
                'label': 'Kollektion', 
                'options': 'Kollektion',
                'reqd': 1
            }
        ],
        function(values){
            // load collection    
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    doctype: 'Bemusterung',
                    filters: [
                        ['kollektion', '=', values.collection]
                    ],
                    fields: ['name', 'rate']
                },
                callback: function(response) {
                    // add items from collection
                    if (response.message) {
                        var muster = response.message;
                        for (var i = 0; i < response.message.length; i++) {
                            var child = cur_frm.add_child('muster');
                            frappe.model.set_value(child.doctype, child.name, 'bemusterung', muster[i].name);
                            frappe.model.set_value(child.doctype, child.name, 'qty', 1);
                            frappe.model.set_value(child.doctype, child.name, 'rate', muster[i].rate);
                        }
                        cur_frm.refresh_field('muster');
                    }
                }
            });
        },
        'Artikel von Kollektion',
        'Hinzufügen'
    );
}

function load_dessin(frm) {
    frappe.prompt([
        {'fieldname': 'dessin', 'fieldtype': 'Link', 'label': 'Dessin', 'options': 'Dessin', 'reqd': 1} 
    ],
    function(values){
        frappe.call({
            'method': 'frappe.client.get_list',
            'args': {
                'doctype': 'Bemusterung',
                'filters': {'dessin': values.dessin},
                'fields': ["name", "rate"]
            },
            'callback': function(response) {
                var bemusterungen = response.message;
                if (bemusterungen.length > 0) {
                    var fields = [];
                    var half = Math.round(bemusterungen.length/2);
                    for (var i = 0; i < bemusterungen.length; i++) {
                        fields.push({'fieldname': 'c' + i, 'fieldtype': 'Check', 'label': bemusterungen[i].name});
                        if (i === half) {
                            fields.push({'fieldname': 'column_' + i, 'fieldtype': 'Column Break'});
                        }
                    }
                    frappe.prompt(
                        fields,
                        function(v){
                            // insert production steps
                            for (var j = 0; j < bemusterungen.length; j++) {
                                if (v[('c' + j)] === 1) {
                                    var child = cur_frm.add_child('muster');
                                    frappe.model.set_value(child.doctype, child.name, 'bemusterung', bemusterungen[j].name);
                                    frappe.model.set_value(child.doctype, child.name, 'rate', bemusterungen[j].rate);
                                }
                            }
                            cur_frm.refresh_field('muster');
                        },
                        __('Artikel laden'),
                        'OK'
                    );
                } else {
                    frappe.msgprint( __("Leider keine Artikel in diesem Dessin") );
                }
            }
        });
    },
    __('Dessin laden'),
    'OK'
    );
}
