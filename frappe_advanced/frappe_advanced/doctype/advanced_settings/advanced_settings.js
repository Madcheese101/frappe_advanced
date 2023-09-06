// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Advanced Settings', {
	refresh: function(frm) {
		frm.events.show_hide_fields(frm);
	},
	onload: function(frm) {
		frm.events.show_hide_fields(frm);
	},
	account_transfer_limit_warning: function(frm) {
		frm.events.show_hide_fields(frm);
	},
	stock_entry_not_accepted_warning: function(frm) {
		frm.events.show_hide_fields(frm);
	},
	write_off_limit_warning: function(frm) {
		frm.events.show_hide_fields(frm);
	},	
	auto_split_batch: function(frm) {
		frm.events.show_hide_fields(frm);
	},
	show_hide_fields: function(frm){
		frm.toggle_display("account_transfer_days_limit", (frm.doc.account_transfer_limit_warning));
		frm.toggle_display("stock_entry_days_limit", (frm.doc.stock_entry_not_accepted_warning));
		frm.toggle_display("exclude_account_numbers", (frm.doc.account_transfer_limit_warning));
		frm.toggle_display("write_off_limit", (frm.doc.write_off_limit_warning));
		frm.toggle_display("for_item_groups", (frm.doc.auto_split_batch));
	},
	setup:function(frm){
		frm.set_query('for_item_groups', () => {
			return {
				filters: {
					is_group: 0
				}
			}
		})
	}
});
