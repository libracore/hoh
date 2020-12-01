frappe.ui.form.on('Work Order', {
    refresh: function(frm) {
        // button to complete finishing
        if ((frm.doc.status === "Completed") && (frm.doc.ausruestung_fertig === 0)) {
            frm.page.set_indicator(__('Ausrüsten'), 'orange');
            frm.add_custom_button(__('Ausrüstung fertig'), function() {
                cur_frm.set_value("ausruestung_fertig", 1);
                cur_frm.save_or_update();
            }).addClass("btn-primary");
        }
        if (frm.doc.docstatus < 2) {
            var datestamp = frappe.datetime.now_date() + " " + frappe.datetime.now_time();
            if ((frm.doc.nutzungen.length > 0) && (!frm.doc.nutzungen[frm.doc.nutzungen.length - 1].end)) {
                frm.add_custom_button(__('Stop'), function() {
                    frappe.model.set_value(frm.doc.nutzungen[frm.doc.nutzungen.length - 1].doctype, frm.doc.nutzungen[frm.doc.nutzungen.length - 1].name, 'end', datestamp);
                    cur_frm.save_or_update();
                }).addClass("btn-warning");
            } else {
                frm.add_custom_button(__('Start'), function() {
                    var child = cur_frm.add_child('nutzungen');
                    frappe.model.set_value(child.doctype, child.name, 'start', datestamp);
                    cur_frm.save_or_update();
                }).addClass("btn-warning");
            }
        }
    },
    production_item: function(frm) {
        // change on production item --> fetch related data fields
        if (frm.doc.production_item) {
            fetch_item_details(frm);
        }
    },
    before_save: function(frm) {
        if (!frm.doc.stoff) {
            fetch_item_details(frm);
        }
        // calculate total machine hours
        var machine_hours = 0;
        for (var i = 0; i < frm.doc.nutzungen.length; i++) {
            if ((frm.doc.nutzungen[i].end) && (frm.doc.nutzungen[i].start)) {
                var duration = (new Date(frm.doc.nutzungen[i].end) - new Date(frm.doc.nutzungen[i].start)) / 3600000;
                frappe.model.set_value(frm.doc.nutzungen[i].doctype, frm.doc.nutzungen[i].name, 'maschinenstunden', duration);
            }
            machine_hours += frm.doc.nutzungen[i].maschinenstunden;
        }
        cur_frm.set_value('summe_maschinenstunden', machine_hours);
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
