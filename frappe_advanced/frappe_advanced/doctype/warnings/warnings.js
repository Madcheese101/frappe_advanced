// Copyright (c) 2023, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warnings', {
	onload: function(frm) {
		frm.events.show_hide_fields(frm);		
	},
	refresh:function(frm){
		if(frm.doc.status == "Pending Review"){
			frm.add_custom_button(__('Mark As Reviewed'), function(){
				frm.set_value("status","Reviewed");
				frm.save();
			});
		}
		if(frm.doc.status == "Reviewed"){
			frm.add_custom_button(__('Mark As Pending Review'), function(){
				frm.set_value("status","Pending Review");
				frm.save();
			});
		}
	},
	show_hide_fields: function(frm){
		frm.toggle_display("sales_invoice", (frm.doc.warning_type == "Canceled Sales Invoice"));
		frm.toggle_display("employee", (frm.doc.warning_type != "Account not Transferred"));
		frm.toggle_display("account_name", (frm.doc.warning_type != "Canceled Sales Invoice"));
		frm.toggle_display("account_balance", (frm.doc.warning_type == "Account not Transferred" && frm.doc.account_name));
		frm.toggle_display("last_transfer_date", (frm.doc.warning_type == "Account not Transferred" && frm.doc.account_name));
		frm.toggle_display("transferred_amount", (frm.doc.warning_type == "Partial Account Transfer" && frm.doc.account_name));
		frm.toggle_display("write_off_limit", (frm.doc.warning_type == "Write-Off Limit Exceeded" && frm.doc.account_name));
		frm.toggle_display("write_off_amount_inserted", (frm.doc.warning_type == "Write-Off Limit Exceeded" && frm.doc.account_name));
		frm.toggle_display("payment_entry", ((frm.doc.warning_type == "Write-Off Limit Exceeded" 
												|| frm.doc.warning_type == "Partial Account Transfer")
												&& frm.doc.account_name
											));
	}
});
