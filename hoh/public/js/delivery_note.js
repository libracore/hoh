frappe.ui.form.on('Delivery Note', {
    before_save: function(frm) {
        add_traces(frm)        
    },
    on_submit: function(frm) {
        update_weight(frm)
    }
});

function add_traces(frm) {
    var items = frm.doc.items || [];
    // Iterate over each delivery note item    
    items.forEach(function(item) {
        if (!item.against_sales_order) {
            // Find another item with the same item_code that has against_sales_order value
            var matchingItem = items.find(function(match) {
                return match.item_code === item.item_code && match.against_sales_order;
            });
            
            if (matchingItem) {
                // Copy the against_sales_order value to the current item
                frappe.model.set_value(item.doctype, item.name, 'against_sales_order', matchingItem.against_sales_order);
                frappe.model.set_value(item.doctype, item.name, 'uom', matchingItem.uom);
                frappe.model.set_value(item.doctype, item.name, 'conversion_factor', matchingItem.conversion_factor);
                frappe.model.set_value(item.doctype, item.name, 'price_list_rate', matchingItem.price_list_rate);
                frappe.model.set_value(item.doctype, item.name, 'rate', matchingItem.rate);
                frappe.model.set_value(item.doctype, item.name, 'so_detail', matchingItem.so_detail);
                frappe.model.set_value(item.doctype, item.name, 'weight_per_unit', matchingItem.weight_per_unit);
            }
        }
    });
}

function update_weight(frm) {
    frappe.call({
        'method': 'hoh.hoh.utils.update_bemusterung_weight_from_delivery_note',
        'args': {
            'delivery_note': frm.doc.name
        },
        'callback': function(response) {
            frappe.show_alert( __("Gewichte aktualisiert.") );
        }
    });
}
