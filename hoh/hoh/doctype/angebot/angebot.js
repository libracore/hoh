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
	},
    customer_name: function(frm) {
        cur_frm.set_value('title', frm.doc.customer_name);
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
