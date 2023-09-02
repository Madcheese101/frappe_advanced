// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Order Settings', {
	refresh: function(frm) {
		frm.call('set_table')
	},
	onload: function(frm){
		frm.call('set_table')
	}
});
