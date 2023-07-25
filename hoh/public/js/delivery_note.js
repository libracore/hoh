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
	var items = frm.doc.items || [];
	// Iterate over each delivery note item
    items.forEach(function(item) {
		var deliveryNoteItem = frappe.get_doc(item.doctype, item.name);          
        // Get the item code
        var itemCode = deliveryNoteItem.item_code;
        // Fetch Bemusterung in the Item document
        frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: 'Item',
				filters: [
					['name', '=', itemCode]
				],
			fields: ['bemusterung'],
			},
			callback: function(response) {
				var baseArticle = response.message[0].bemusterung;
				console.log("message", baseArticle)
			       
				// Set weight in the Bemusterung document
				frappe.call({
					method: "frappe.client.set_value",
					args: {
						doctype: "Bemusterung",
						name: baseArticle,
						fieldname: {
							gewicht: deliveryNoteItem.weight_per_unit
						}
					}
				});
			}
		});
		
        
	});
}
