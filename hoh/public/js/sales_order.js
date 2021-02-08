frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        // add label button
        frm.add_custom_button(__("Etikette erstellen"), function() {
            create_label(frm);
        }).addClass("btn-primary");
    }
});

/* label printing function */
function create_label(frm) {
// html-content of the label
        var url = "/api/method/hoh.hoh.labels.get_sales_order_label"  
                + "?sales_order=" + encodeURIComponent(frm.doc.name);
        var w = window.open(
             frappe.urllib.get_full_url(url)
        );
        if (!w) {
            frappe.msgprint(__("Please enable pop-ups")); return;
        }
}
