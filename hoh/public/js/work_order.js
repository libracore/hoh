frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        // button to complete finishing
        if (((frm.doc.status === "Completed") || (frm.doc.status === "Stopped")) && (frm.doc.ausruestung_fertig === 0)) {
            frm.page.set_indicator(__('Ausrüsten'), 'orange');
            frm.add_custom_button(__('Ausrüstung fertig'), function() {
                cur_frm.set_value("ausruestung_fertig", 1);
                cur_frm.save_or_update();
            }).addClass("btn-primary");
        }
        if (frm.doc.docstatus < 2) {
            if ((frm.doc.nutzungen.length > 0) && (!frm.doc.nutzungen[frm.doc.nutzungen.length - 1].end)) {
                frm.add_custom_button(__('Zeiterfassung beenden'), function() {
                    frappe.call({
                        "method": "hoh.hoh.utils.set_wo_timetracking",
                        "args": {
                            "work_order": frm.doc.name
                        },
                        "callback": function(response) {
                            console.log("done");
                            cur_frm.reload_doc();
                        }
                    });
                }).addClass("btn-warning");
            } else {
                frm.add_custom_button(__('Zeit erfassen'), function() {
                    frappe.call({
                        "method": "hoh.hoh.utils.set_wo_timetracking",
                        "args": {
                            "work_order": frm.doc.name
                        },
                        "callback": function(response) {
                            cur_frm.reload_doc();
                        }
                    });
                }).addClass("btn-warning");
            }
        }
        // add label button
        frm.add_custom_button(__("Etikette erstellen"), function() {
            create_label(frm);
        }).addClass("btn-primary");
        // add refresh embroideries button
        frm.add_custom_button(__("Stickereien neu laden"), function() {
			refresh_embroideries(frm);
        }).addClass("btn-primary");
    },
    production_item: function(frm) {
        // change on production item --> fetch related data fields
        if (frm.doc.production_item) {
            fetch_item_details(frm);
            // restore sales order
            cur_frm.set_value("sales_order", frm.doc.sales_order_store);
        }
    },
    before_save: function(frm) {
        if (!frm.doc.stoff) {
            fetch_item_details(frm);
        }
        if ((frm.doc.sales_order) && (!frm.doc.sales_order_store)) {
            // store sales order
            cur_frm.set_value("sales_order_store", frm.doc.sales_order);
        } else if ((!frm.doc.sales_order) && (frm.doc.sales_order_store)) {
            cur_frm.set_value("sales_order", frm.doc.sales_order_store);
        }
    }
});

frappe.ui.form.on('Work Order Nutzung', {
    end: function(frm, cdt, cdn) {
        calculate_machine_hours(frm);
    },
    start: function(frm, cdt, cdn) {
        calculate_machine_hours(frm);
    }
});

function fetch_item_details(frm) {
    frappe.call({
        "method": "hoh.hoh.utils.compile_details",
        "async": false,
        "args": {
            "bemusterung": frm.doc.production_item
        },
        "callback": function(response) {
            var details = response.message;
            // apply values
            cur_frm.set_value("garn", details.garne);
            cur_frm.set_value("stoff", details.stoffe);
            cur_frm.set_value("pailletten", details.pailletten);
            cur_frm.set_value("monofil", details.monofil);
            cur_frm.set_value("bobinen", details.bobinen);
            cur_frm.set_value("kartenmeter", details.kartenmeter);
            if (details.stickmaschine) {
                cur_frm.set_value("stickmaschine", details.stickmaschine);
                cur_frm.set_value("planned_start_date", details.start_date);
            }
            // remove all rows
            var tbl = frm.doc.finish_steps || [];
            var i = tbl.length;
            while (i--)
            {
                cur_frm.get_field("finish_steps").grid.grid_rows[i].remove();
            }
            details.finish_steps.forEach(function (step) {
                var child = cur_frm.add_child('finish_steps');
                frappe.model.set_value(child.doctype, child.name, 'finish_step', step.finish_step);
                frappe.model.set_value(child.doctype, child.name, 'supplier', step.supplier);  
            });
            cur_frm.refresh();
        }
    });
}

function calculate_machine_hours(frm) {
    // calculate total machine hours
    var machine_hours = 0;
    if (frm.doc.nutzungen) {
        for (var i = 0; i < frm.doc.nutzungen.length; i++) {
            if ((frm.doc.nutzungen[i].end) && (frm.doc.nutzungen[i].start)) {
                var duration = (new Date(frm.doc.nutzungen[i].end) - new Date(frm.doc.nutzungen[i].start)) / 3600000;
                frappe.model.set_value(frm.doc.nutzungen[i].doctype, frm.doc.nutzungen[i].name, 'maschinenstunden', duration);
            }
            if (frm.doc.nutzungen[i].activity_type !== "Pause") {
                machine_hours += frm.doc.nutzungen[i].maschinenstunden;
            }
        }
    }
    cur_frm.set_value('summe_maschinenstunden', machine_hours);
}

/* label printing function */
function create_label(frm) {
// html-content of the label
        var url = "/api/method/hoh.hoh.labels.get_work_order_label"  
                + "?selected_items=" + encodeURIComponent("'" + frm.doc.name + "'");
        var w = window.open(
             frappe.urllib.get_full_url(url)
        );
        if (!w) {
            frappe.msgprint(__("Please enable pop-ups")); return;
        }
}

function refresh_embroideries(frm) {
// Check for unsafed Datas
	if (frm.doc.__unsaved) {
		frappe.msgprint("Bitte zuerst die Änderungen speichern.");
	} else {
// Call Server to reload datas
		frappe.call({
		'async': false,
		"method": "hoh.hoh.utils.complete_work_order_details",
		"args": {
			"work_order": frm.doc.name
		},
		"callback": function(response) {
			cur_frm.reload_doc();
			}
		})
	}
}
