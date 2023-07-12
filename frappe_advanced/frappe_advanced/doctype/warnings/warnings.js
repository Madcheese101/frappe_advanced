// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warnings', {
	onload: function(frm) {
		frm.events.show_hide_fields(frm);
	},
	warning_type: function(frm){
		frm.events.show_hide_fields(frm);
		frm.set_value("sales_invoice","");
		frm.set_value("account_name","");
		frm.set_value("account_amount","");
		frm.set_value("last_transfer_date","");
		frm.set_value("account_amount_transferred","");
		frm.set_value("write_off_limit","");
		frm.set_value("write_off_amount_inserted","");
	},
	account_name: function(frm){
		frm.events.show_hide_fields(frm);
	},
	show_hide_fields: function(frm){
		frm.toggle_display("sales_invoice", (frm.doc.warning_type == "Canceled Sales Invoice"));
		frm.toggle_display("employee", (frm.doc.warning_type != "Account not Transferred"));
		frm.toggle_display("account_name", (frm.doc.warning_type != "Canceled Sales Invoice"));
		frm.toggle_display("account_amount", (frm.doc.warning_type == "Account not Transferred" && frm.doc.account_name));
		frm.toggle_display("last_transfer_date", (frm.doc.warning_type == "Account not Transferred" && frm.doc.account_name));
		frm.toggle_display("account_amount_transferred", (frm.doc.warning_type == "Partial Account Transfer" && frm.doc.account_name));
		frm.toggle_display("write_off_limit", (frm.doc.warning_type == "Write-Off Limit Exceeded" && frm.doc.account_name));
		frm.toggle_display("write_off_amount_inserted", (frm.doc.warning_type == "Write-Off Limit Exceeded" && frm.doc.account_name));
	}
});
