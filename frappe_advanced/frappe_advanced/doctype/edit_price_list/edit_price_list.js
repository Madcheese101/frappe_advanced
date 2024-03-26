// Copyright (c) 2024, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Edit Price List', {
	refresh: function(frm) {
		frm.disable_save();
	},
	export_excel: function(frm) {
		let price_list = frm.doc.price_list || 0;
		let percentage = frm.doc.percentage || 0;
		let argss = {
			cmd: "frappe_advanced.frappe_advanced.doctype.edit_price_list.edit_price_list.start_export"
		};
		if (price_list != 0){
			argss["price_list"] = price_list;
			argss["percentage"] = percentage;
		}
		const args = argss;
		open_url_post(frappe.request.url, args);
	},
});
