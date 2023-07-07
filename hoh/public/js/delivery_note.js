frappe.ui.form.on('Delivery Note', {
	on_submit: function(frm) {
        var items = frm.doc.items || [];
        
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
                    console.log("is matching", matchingItem)
                }
            }
        });
        
        
         // Iterate over each delivery note item
        $.each(frm.doc.items || [], function(index, item) {
            var deliveryNoteItem = frappe.get_doc(item.doctype, item.name);
            
            // Get the item code
            var itemCode = deliveryNoteItem.item_code;

            // Load the Item document
            frappe.model.with_doc("Item", itemCode, function() {
                var itemDoc = frappe.model.get_doc("Item", itemCode);
                
                // Get the base article
                var baseArticle = itemDoc.bemusterung;
                console.log("is baseArticle", baseArticle)
                
                // Load the Bemusterung document
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
            });
        });
        
	}
	
});
