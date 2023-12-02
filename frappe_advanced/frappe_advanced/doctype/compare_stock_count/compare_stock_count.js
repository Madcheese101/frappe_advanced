// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Compare Stock Count', {
	refresh: function(frm) {
		frm.disable_save();
	},
	export_excel: function(frm) {
		const args = {
			cmd: "frappe_advanced.frappe_advanced.doctype.compare_stock_count.compare_stock_count.start_export",
			item_group: frm.doc.item_group
		};
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
