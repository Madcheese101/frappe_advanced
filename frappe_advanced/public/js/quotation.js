frappe.ui.form.on('Quotation', {
	refresh: function(frm) {
		if(frm.doc.docstatus){
			frm.add_custom_button(__('Get Items Stock'), function(){
				frm.call({
					doc: frm.doc,
					method: 'get_item_warehouses',
				});
			});
		}

	}
});