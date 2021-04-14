frappe.listview_settings['Kommissionsabrechnung'] = {
    onload: function(listview) {
        listview.page.add_menu_item( __("Kommissionsabrechnung erstellen"), function() {
            create_commission_statement();
        });
    }
}

function create_commission_statement() {
    // get from and to dates
    var d = new Date();
    var n = d.getMonth();
    var from_date = null;
    var to_date = null;
    var title = "";
    // define title as Qn YYYY of the last complete quarter
    if ((n > (-1)) && (n < 3)) {
        title = "Q04 / " + (d.getFullYear() - 1);
        from_date = (d.getFullYear() - 1) + "-10-01";
        to_date = (d.getFullYear() - 1) + "-12-31";
    } else if ((n > (2)) && (n < 6)) {
        title = "Q01 / " + d.getFullYear();
        from_date = d.getFullYear() + "-01-01";
        to_date = d.getFullYear() + "-03-31";
    } else if ((n > (5)) && (n < 9)) {
        title = "Q02 / " + d.getFullYear();
        from_date = d.getFullYear() + "-04-01";
        to_date = d.getFullYear() + "-06-30";
    } else {
        title = "Q03 / " + d.getFullYear();
        from_date = d.getFullYear() + "-07-01";
        to_date = d.getFullYear() + "-09-30";
    } 

    frappe.prompt([
            {'fieldname': 'sales_partner', 'fieldtype': 'Link', 'label': __("Sales Partner"), 'options': 'Sales Partner', 'reqd': 1 },
            {'fieldname': 'from_date', 'fieldtype': 'Date', 'label': __('From date'), 'reqd': 1, 'default': from_date},
            {'fieldname': 'to_date', 'fieldtype': 'Date', 'label': __('To date'), 'reqd': 1, 'default': to_date},
            {'fieldname': 'quarter', 'fieldtype': 'Data', 'label': __('Description'), 'reqd': 1, 'default': title}
        ],
        function(values){
            frappe.call({
                "method": "hoh.hoh.doctype.kommissionsabrechnung.kommissionsabrechnung.create",
                "args": {
                    "sales_partner": values.sales_partner,
                    "from_date": values.from_date,
                    "to_date": values.to_date,
                    "quarter": values.quarter
                },
                "callback": function(response) {
                    frappe.set_route("Form", "Kommissionsabrechnung", response.message);
                }
            });
        },
        __('Kommissionsabrechnung'),
        __('Create')
    );
}
