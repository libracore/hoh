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
        "method": "frappe.client.get",
        "async": false,
        "args": {
            "doctype": "Bemusterung",
            "name": frm.doc.production_item
        },
        "callback": function(response) {
            var bemusterung = response.message;
            fill_details(frm, bemusterung);
        }
    });
}

function fill_details(frm, bemusterung) {
    // collect values from bemusterung > BOM
    var garne = [];
    var stoffe = [];
    var pailletten = [];
    var monofil = [];
    for (var i = 0; i < bemusterung.items.length; i++) {
        if ((bemusterung.items[i].item_group === "Garne") || (bemusterung.items[i].item_group === "Kordel")) {
            garne.push(bemusterung.items[i].item_name);
        } else if ((bemusterung.items[i].item_group === "Stoffe") || (bemusterung.items[i].item_group === "Hilfsstoffe")) {
            stoffe.push(bemusterung.items[i].item_name);
        } else if (bemusterung.items[i].item_group === "Pailletten") {
            pailletten.push(bemusterung.items[i].item_name);
        } else if (bemusterung.items[i].item_group === "Monofil") {
            monofil.push(bemusterung.items[i].item_name);
        }
    }
    // apply values
    cur_frm.set_value("garn", garne.join(" + "));
    cur_frm.set_value("stoff", stoffe.join(" + "));
    cur_frm.set_value("pailletten", pailletten.join(" + "));
    cur_frm.set_value("monofil", monofil.join(" + "));
    // read kartenmeter
    frappe.call({
        "method": "frappe.client.get",
        "async": false,
        "args": {
            "doctype": "Dessin",
            "name": bemusterung.dessin
        },
        "callback": function(response) {
            var dessin = response.message;
            cur_frm.set_value("kartenmeter", dessin.gesamtmeter);
            // read machine
            var machine = null;
            if (dessin.stickmaschine.length > 0) {
                machine = dessin.stickmaschine[0].stickmaschine;
            }
            if (machine) {
                cur_frm.set_value("stickmaschine", machine);
            }
        }
    });
}

function check_material_status(frm) {
    
}
