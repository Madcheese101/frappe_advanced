// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Compare Stock Count', {
	refresh: function(frm) {
		frm.disable_save();
	},
	export_excel: function(frm) {
		let item_group = frm.doc.item_group || 0;
		let argss = {
			cmd: "frappe_advanced.frappe_advanced.doctype.compare_stock_count.compare_stock_count.start_export"
		};
		if (item_group != 0){
			argss["item_group"] = item_group;
		}
		const args = argss;
		open_url_post(frappe.request.url, args);
	},
	setup: function(frm){
		frm.set_query('item_group', () => {
			return {
				filters: {
					name: ["descendants of", "Products - منتجات"],
					is_group: 0 
				}
			}
		})
	}
});
