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
    },
    production_item: function(frm) {
        // change on production item --> fetch related data fields
        if (frm.doc.production_item) {
            fetch_item_details(frm);
        }
    }
});

function fetch_item_details(frm) {
    frappe.call({
        "method": "frappe.client.get",
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
        "args": {
            "doctype": "Dessin",
            "name": bemusterung.dessin
        },
        "callback": function(response) {
            var dessin = response.message;
            cur_frm.set_value("kartenmeter", dessin.gesamtmeter);
        }
    });
}

function check_material_status(frm) {
    
}
