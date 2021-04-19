// Copyright (c) 2020-2021, libracore and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stickmaschine', {
    refresh: function(frm) {
        frm.add_custom_button(__("Auslastung"), function() {
            frappe.set_route("query-report", "Auslastung Stickmaschine", {"stickmaschine": frm.doc.name});;
        }, __("View"));
        frm.add_custom_button(__("Stickplan"), function() {
            frappe.set_route("query-report", "Stickplan", {"stickmaschine": frm.doc.name});;
        }, __("View"));
    },
    yds_per_cp: function(frm) {
        if (frm.doc.yds_per_cp) {
            cur_frm.set_value("m_per_cp", (frm.doc.yds_per_cp * 0.91));
        } else {
            cur_frm.set_value("m_per_cp", 0);
        }
    }
});
