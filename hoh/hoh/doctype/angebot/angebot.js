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
    }
});

frappe.ui.form.on('Angebot Muster', {
	qty: function(frm, cdt, cdn) {
        update_row_amount(frm, cdt, cdn)
	},
    rate: function(frm, cdt, cdn) {
        update_row_amount(frm, cdt, cdn)
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
        net_total += frm.doc.muster[i].amount;
    }
    cur_frm.set_value('net_total', net_total);
    cur_frm.refresh_field('net_total');
}
