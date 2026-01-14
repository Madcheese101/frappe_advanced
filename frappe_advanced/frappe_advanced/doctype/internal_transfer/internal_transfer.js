// Copyright (c) 2025, MadCheese and contributors
// For license information, please see license.txt

frappe.ui.form.on('Internal Transfer', {
	refresh: function(frm) {
		frm.fields_dict['fetch_data'].$wrapper
            .find('button')
            .addClass('btn-primary btn-sm primary-action'); //I can remove class with .removeClass()
	},
	account_type: function(frm) {
		frm.trigger('set_from_account');
		let filters = {}
		if(frm.doc.account_type.includes("بطاقة")) {
			filters['account_number'] = ['in', ["152003", "125002", "125001"]]
		}
		if(frm.doc.account_type.includes("صك")) 
		{
			filters['account_number'] = ['not in', ["152003", "125002", "125001"]]
			filters['account_name'] = ['like', "%مصرف%"]
		}
		frm.set_query('receiving_account', function() {
			return {
				filters: filters
			};
		});
	},

	set_from_account: function(frm) {
		if(frm.doc.account_type == "نقدي"){
			frm.set_value('mode_of_payment', "نقدية علي ساسي");
			frm.set_value('from_account', "1121-2 - عمي علي نقدي - BC");
			frm.set_value('receiving_account', "1111 - الخزينة الرئيسية نقدي - BC");
			return;
		};
		if(frm.doc.account_type == "بطاقة"){
			frm.set_value('mode_of_payment', "بطاقة علي ساسي");
			frm.set_value('from_account', "1121-1 - عمي علي بطاقة - BC");
			frm.set_value('receiving_account', "");
			return;
		};
		if(frm.doc.account_type == "صك"){
			frm.set_value('mode_of_payment', "صكوك علي ساسي");
			frm.set_value('from_account', "1121-3 - عمي علي صكوك - BC");
			frm.set_value('receiving_account', "");
			return;
		};
		frm.set_value('mode_of_payment', "");
		frm.set_value('from_account', "");
		frm.set_value('receiving_account', "");
		return;
	},

	fetch_data: function(frm) {
		console.log("Fetch Data Button Clicked");
		const me = this;
		frm.call('fetch_internal_transfer_data').then(r => {
			me.refresh_fields();
		});
	}
});
