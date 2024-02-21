// Copyright (c) 2024, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expenses', {
	refresh: function(frm) {
		let is_allowed = frappe.user_roles.includes('Accounts Manager');
		frm.set_df_property('branch', 'read_only', !is_allowed);
		
		frm.call('set_fields');
	}
});
