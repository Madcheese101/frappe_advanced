frappe.ui.form.on('Sales Order', {
	refresh: function(frm) {
		if(frm.doc.docstatus){
			frm.add_custom_button(__('Get Items Stock'), function(){
				frappe.call({
					method: 'frappe_advanced.frappe_advanced.api.api.get_item_warehouses',
					args: {"so_id": frm.doc.name},
				});
			});
		}
	}
});