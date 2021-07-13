// Copyright (c) 2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Control', {
    refresh: function(frm) {
        if (!frm.doc.date) {
            cur_frm.set_value("date", frappe.datetime.get_today());
        }
    },
    before_save: function(frm) {
        // make sure all qty diffs are calculated
        frm.doc.items.forEach(function (item) {
            update_qty(frm, item.doctype, item.name);
        });
    }
});

frappe.ui.form.on('Stock Control Item', {
    item: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item) {
            frappe.call({
                'method': 'get_stock',
                'doc': frm.doc,
                'args': {
                    'item': row.item
                },
                'callback': function(response) {
                    frappe.model.set_value(cdt, cdn, 'expected_qty', response.message);
                    update_diff(frm, cdt, cdn);
                }
            });
        } else {
            frappe.model.set_value(cdt, cdn, 'expected_qty', 0);
            update_diff(frm, cdt, cdn);
        }
    },
    qty: function(frm, cdt, cdn) {
        update_diff(frm, cdt, cdn);
    }
});

function update_diff(frm, cdt, cdn) {
    var row = locals[cdt][cdn];
    var diff = row.qty - row.expected_qty;
    frappe.model.set_value(cdt, cdn, 'difference_qty', diff);
}
